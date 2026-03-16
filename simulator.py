"""
Main simulator for ETF Creation Redemption Simulator.

Orchestrates the entire simulation workflow from data loading to arbitrage analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

from data_loader import DataLoader
from nav_engine import NavEngine
from cost_model import CostModel, CostAssumptions
from arbitrage_engine import ArbitrageEngine


class ETFSimulator:
    """Main simulator class for ETF creation/redemption analysis."""
    
    def __init__(self, cost_assumptions: CostAssumptions = None):
        self.data_loader = DataLoader()
        self.nav_engine = NavEngine()
        self.cost_model = CostModel(cost_assumptions)
        self.arbitrage_engine = ArbitrageEngine(self.cost_model)
        
        # Results storage
        self.raw_data = None
        self.nav_data = None
        self.premium_discount = None
        self.signals = None
        self.results = None
    
    def run_simulation(
        self,
        etf_ticker: str,
        constituents: Dict[str, float],
        start_date: str,
        end_date: str,
        use_default_basket: bool = False
    ) -> Dict:
        """
        Run complete ETF simulation.
        
        Args:
            etf_ticker: ETF ticker symbol
            constituents: Dictionary of ticker -> weight
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            use_default_basket: Whether to use default constituent weights
            
        Returns:
            Dictionary with all simulation results
        """
        try:
            # 1. Load data
            if use_default_basket or not constituents:
                constituents = self.data_loader.get_default_constituents(etf_ticker)
            
            all_tickers = [etf_ticker] + list(constituents.keys())
            price_data = self.data_loader.fetch_price_data(all_tickers, start_date, end_date)
            
            # 2. Calculate NAV
            etf_prices = price_data[etf_ticker]
            constituent_prices = price_data[list(constituents.keys())]
            
            nav_values = self.nav_engine.calculate_nav(constituent_prices, constituents)
            etf_normalized, nav_normalized = self.nav_engine.normalize_values(
                etf_prices, nav_values
            )
            
            # 3. Calculate premium/discount
            premium_discount = self.nav_engine.calculate_premium_discount(
                etf_normalized, nav_normalized
            )
            
            # 4. Generate arbitrage signals
            signals = self.arbitrage_engine.generate_signals(
                premium_discount, nav_normalized
            )
            
            # 5. Compile results
            results = self._compile_results(
                etf_ticker, constituents, etf_normalized, nav_normalized,
                premium_discount, signals, price_data
            )
            
            # Store results
            self.results = results
            
            return results
            
        except Exception as e:
            raise RuntimeError(f"Simulation failed: {str(e)}")
    
    def _compile_results(
        self,
        etf_ticker: str,
        constituents: Dict[str, float],
        etf_prices: pd.Series,
        nav_values: pd.Series,
        premium_discount: pd.Series,
        signals: pd.DataFrame,
        raw_data: pd.DataFrame
    ) -> Dict:
        """
        Compile all simulation results into comprehensive dictionary.
        
        Args:
            etf_ticker: ETF ticker symbol
            constituents: Constituent weights
            etf_prices: Normalized ETF prices
            nav_values: Normalized NAV values
            premium_discount: Premium/discount series
            signals: Arbitrage signals
            raw_data: Raw price data
            
        Returns:
            Dictionary with compiled results
        """
        # Store raw data
        self.raw_data = raw_data
        self.nav_data = pd.DataFrame({
            'etf_price': etf_prices,
            'nav': nav_values,
            'premium_discount': premium_discount
        })
        self.premium_discount = premium_discount
        self.signals = signals
        
        # Calculate statistics
        nav_stats = self.nav_engine.get_nav_statistics(premium_discount)
        tracking_stats = self.nav_engine.analyze_tracking_error(etf_prices, nav_values)
        arbitrage_stats = self.arbitrage_engine.analyze_arbitrage_performance()
        signal_dist = self.arbitrage_engine.get_signal_distribution()
        
        # Get trading events
        trading_events = self.arbitrage_engine.get_trading_events()
        
        # Calculate cumulative profits
        cumulative_profits = self.arbitrage_engine.calculate_cumulative_profits()
        
        results = {
            'metadata': {
                'etf_ticker': etf_ticker,
                'constituents': constituents,
                'start_date': str(etf_prices.index[0].date()),
                'end_date': str(etf_prices.index[-1].date()),
                'total_days': len(etf_prices)
            },
            'price_data': {
                'etf_prices': etf_prices,
                'nav_values': nav_values,
                'premium_discount': premium_discount
            },
            'signals': signals,
            'trading_events': trading_events,
            'cumulative_profits': cumulative_profits,
            'statistics': {
                'nav_stats': nav_stats,
                'tracking_stats': tracking_stats,
                'arbitrage_stats': arbitrage_stats,
                'signal_distribution': signal_dist
            },
            'cost_assumptions': self.cost_model.get_assumptions_summary()
        }
        
        return results
    
    def get_summary_metrics(self) -> Dict:
        """
        Get key summary metrics for dashboard display.
        
        Returns:
            Dictionary of key metrics
        """
        if self.results is None:
            raise ValueError("Must run simulation first")
        
        stats = self.results['statistics']
        metadata = self.results['metadata']
        
        summary = {
            'etf_ticker': metadata['etf_ticker'],
            'analysis_period': f"{metadata['start_date']} to {metadata['end_date']}",
            'total_days': metadata['total_days'],
            'avg_premium': f"{stats['nav_stats']['mean_premium']:.2f}%",
            'avg_discount': f"{stats['nav_stats']['avg_negative']:.2f}%",
            'creation_events': stats['arbitrage_stats']['creation_events'],
            'redemption_events': stats['arbitrage_stats']['redemption_events'],
            'total_arbitrage_profit': f"${stats['arbitrage_stats']['total_profit']:,.2f}",
            'arbitrage_win_rate': f"{stats['arbitrage_stats']['win_rate']*100:.1f}%",
            'tracking_error': f"{stats['tracking_stats']['tracking_error']*100:.2f}%",
            'correlation': f"{stats['tracking_stats']['correlation']:.3f}",
        }
        
        return summary
    
    def update_cost_assumptions(self, **kwargs) -> None:
        """
        Update cost assumptions and recalculate signals.
        
        Args:
            **kwargs: New cost assumption values
        """
        self.cost_model.update_assumptions(**kwargs)
        
        # Recalculate signals if data exists
        if self.premium_discount is not None and self.nav_data is not None:
            self.signals = self.arbitrage_engine.generate_signals(
                self.premium_discount, self.nav_data['nav']
            )
            
            # Update results
            if self.results is not None:
                self.results['signals'] = self.signals
                self.results['trading_events'] = self.arbitrage_engine.get_trading_events()
                self.results['cumulative_profits'] = self.arbitrage_engine.calculate_cumulative_profits()
                self.results['statistics']['arbitrage_stats'] = self.arbitrage_engine.analyze_arbitrage_performance()
                self.results['statistics']['signal_distribution'] = self.arbitrage_engine.get_signal_distribution()
                self.results['cost_assumptions'] = self.cost_model.get_assumptions_summary()
    
    def export_results(self, filename: str = None) -> str:
        """
        Export simulation results to CSV files.
        
        Args:
            filename: Base filename for exports
            
        Returns:
            Path to exported files
        """
        if self.results is None:
            raise ValueError("Must run simulation first")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"etf_simulation_{timestamp}"
        
        # Export main results
        main_results = self.results['signals'].copy()
        main_results.to_csv(f"{filename}_signals.csv")
        
        # Export trading events
        if not self.results['trading_events'].empty:
            self.results['trading_events'].to_csv(f"{filename}_trading_events.csv")
        
        # Export price data
        price_data = self.results['price_data']
        price_df = pd.DataFrame({
            'etf_price': price_data['etf_prices'],
            'nav': price_data['nav_values'],
            'premium_discount': price_data['premium_discount']
        })
        price_df.to_csv(f"{filename}_price_data.csv")
        
        return filename
    
    def get_chart_data(self) -> Dict:
        """
        Get data formatted for charting.
        
        Returns:
            Dictionary with chart-ready data
        """
        if self.results is None:
            raise ValueError("Must run simulation first")
        
        price_data = self.results['price_data']
        signals = self.results['signals']
        
        # Prepare data for ETF vs NAV chart
        chart_data = {
            'dates': price_data['etf_prices'].index,
            'etf_prices': price_data['etf_prices'].values,
            'nav_values': price_data['nav_values'].values,
            'premium_discount': price_data['premium_discount'].values,
            'creation_threshold': signals['creation_threshold'].values,
            'redemption_threshold': -signals['redemption_threshold'].values,
            'signals': signals['signal'].values,
            'cumulative_profits': self.results['cumulative_profits'].values
        }
        
        return chart_data
    
    def validate_simulation(self) -> Dict:
        """
        Validate simulation results for data quality issues.
        
        Returns:
            Dictionary with validation results
        """
        if self.results is None:
            raise ValueError("Must run simulation first")
        
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check data sufficiency
        total_days = self.results['metadata']['total_days']
        if total_days < 30:
            validation_results['warnings'].append(f"Short analysis period: {total_days} days")
        
        # Check premium/discount extremes
        premium_discount = self.results['price_data']['premium_discount']
        max_premium = premium_discount.max()
        min_discount = premium_discount.min()
        
        if abs(max_premium) > 10:  # 10% premium seems unrealistic
            validation_results['warnings'].append(f"High premium detected: {max_premium:.2f}%")
        
        if abs(min_discount) > 10:  # 10% discount seems unrealistic
            validation_results['warnings'].append(f"High discount detected: {min_discount:.2f}%")
        
        # Check tracking error
        tracking_error = self.results['statistics']['tracking_stats']['tracking_error']
        if tracking_error > 0.05:  # 5% annual tracking error is high
            validation_results['warnings'].append(f"High tracking error: {tracking_error:.2%}")
        
        # Check correlation
        correlation = self.results['statistics']['tracking_stats']['correlation']
        if correlation < 0.95:  # Low correlation might indicate bad proxy basket
            validation_results['warnings'].append(f"Low correlation: {correlation:.3f}")
        
        # Check for missing data
        if premium_discount.isnull().any():
            validation_results['errors'].append("Missing data detected in premium/discount series")
            validation_results['is_valid'] = False
        
        return validation_results
