"""
Arbitrage engine for ETF Creation Redemption Simulator.

Determines when authorized participants should execute creations or redemptions
based on arbitrage opportunities after transaction costs.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from cost_model import CostModel, CostAssumptions


class ArbitrageEngine:
    """Determines optimal creation/redemption arbitrage opportunities."""
    
    def __init__(self, cost_model: CostModel):
        self.cost_model = cost_model
        self.signals = None
        self.profits = None
    
    def generate_signals(
        self, 
        premium_discount: pd.Series, 
        nav_values: pd.Series
    ) -> pd.DataFrame:
        """
        Generate creation/redemption signals based on premium/discount.
        
        Args:
            premium_discount: Series of premium/discount percentages
            nav_values: Series of NAV values
            
        Returns:
            DataFrame with signals and calculated profits
        """
        results = pd.DataFrame(index=premium_discount.index)
        results['premium_discount'] = premium_discount
        results['nav_value'] = nav_values
        
        # Calculate thresholds
        creation_thresholds = []
        redemption_thresholds = []
        
        for nav in nav_values:
            creation_th = self.cost_model.get_creation_threshold(nav)
            redemption_th = self.cost_model.get_redemption_threshold(nav)
            creation_thresholds.append(creation_th)
            redemption_thresholds.append(redemption_th)
        
        results['creation_threshold'] = creation_thresholds
        results['redemption_threshold'] = redemption_thresholds
        
        # Generate signals
        signals = []
        profits = []
        profit_pct = []
        
        for i, (pd_pct, nav, create_th, redeem_th) in enumerate(
            zip(premium_discount, nav_values, creation_thresholds, redemption_thresholds)
        ):
            signal, profit_info = self._evaluate_arbitrage_opportunity(
                pd_pct, nav, create_th, redeem_th
            )
            signals.append(signal)
            profits.append(profit_info['profit'])
            profit_pct.append(profit_info['profit_pct'])
        
        results['signal'] = signals
        results['profit'] = profits
        results['profit_pct'] = profit_pct
        
        self.signals = results
        return results
    
    def _evaluate_arbitrage_opportunity(
        self, 
        premium_discount_pct: float, 
        nav_value: float,
        creation_threshold: float,
        redemption_threshold: float
    ) -> Tuple[str, Dict]:
        """
        Evaluate arbitrage opportunity for a single day.
        
        Args:
            premium_discount_pct: Premium (+) or discount (-) as percentage
            nav_value: NAV value
            creation_threshold: Required premium for creation
            redemption_threshold: Required discount for redemption
            
        Returns:
            Tuple of (signal, profit_info)
        """
        if premium_discount_pct >= creation_threshold:
            # Creation arbitrage opportunity
            profit_info = self.cost_model.calculate_arbitrage_profit(
                premium_discount_pct, nav_value, 'create'
            )
            return 'CREATE', profit_info
        
        elif premium_discount_pct <= -redemption_threshold:
            # Redemption arbitrage opportunity
            profit_info = self.cost_model.calculate_arbitrage_profit(
                premium_discount_pct, nav_value, 'redeem'
            )
            return 'REDEEM', profit_info
        
        else:
            # No arbitrage opportunity
            return 'NONE', {'profit': 0, 'profit_pct': 0, 'is_profitable': False}
    
    def get_trading_events(self) -> pd.DataFrame:
        """
        Extract only trading events (creations and redemptions).
        
        Returns:
            DataFrame filtered for trading events only
        """
        if self.signals is None:
            raise ValueError("Must call generate_signals first")
        
        trading_events = self.signals[
            self.signals['signal'].isin(['CREATE', 'REDEEM'])
        ].copy()
        
        return trading_events
    
    def analyze_arbitrage_performance(self) -> Dict:
        """
        Analyze overall arbitrage performance.
        
        Returns:
            Dictionary with performance metrics
        """
        if self.signals is None:
            raise ValueError("Must call generate_signals first")
        
        trading_events = self.get_trading_events()
        
        metrics = {
            'total_days': len(self.signals),
            'trading_days': len(trading_events),
            'creation_events': len(trading_events[trading_events['signal'] == 'CREATE']),
            'redemption_events': len(trading_events[trading_events['signal'] == 'REDEEM']),
            'total_profit': trading_events['profit'].sum(),
            'avg_profit_per_trade': trading_events['profit'].mean() if len(trading_events) > 0 else 0,
            'avg_profit_pct': trading_events['profit_pct'].mean() if len(trading_events) > 0 else 0,
            'max_profit': trading_events['profit'].max() if len(trading_events) > 0 else 0,
            'min_profit': trading_events['profit'].min() if len(trading_events) > 0 else 0,
            'profitable_trades': (trading_events['profit'] > 0).sum() if len(trading_events) > 0 else 0,
            'win_rate': (trading_events['profit'] > 0).mean() if len(trading_events) > 0 else 0,
        }
        
        # Calculate annualized metrics
        if len(self.signals) > 0:
            days_span = (self.signals.index[-1] - self.signals.index[0]).days
            if days_span > 0:
                metrics['annualized_trades'] = (metrics['trading_days'] / days_span) * 252
                metrics['annualized_profit'] = metrics['total_profit'] * (252 / days_span)
        
        return metrics
    
    def calculate_cumulative_profits(self) -> pd.Series:
        """
        Calculate cumulative arbitrage profits over time.
        
        Returns:
            Series of cumulative profits
        """
        if self.signals is None:
            raise ValueError("Must call generate_signals first")
        
        cumulative_profits = self.signals['profit'].cumsum()
        return cumulative_profits
    
    def get_signal_distribution(self) -> Dict:
        """
        Get distribution of different signal types.
        
        Returns:
            Dictionary with signal counts and percentages
        """
        if self.signals is None:
            raise ValueError("Must call generate_signals first")
        
        signal_counts = self.signals['signal'].value_counts()
        total_signals = len(self.signals)
        
        distribution = {}
        for signal, count in signal_counts.items():
            distribution[signal] = {
                'count': count,
                'percentage': (count / total_signals) * 100
            }
        
        return distribution
    
    def optimize_thresholds(
        self, 
        premium_discount: pd.Series, 
        nav_values: pd.Series,
        creation_fee_range: Tuple[float, float] = (0.001, 0.005),
        redemption_fee_range: Tuple[float, float] = (0.001, 0.005)
    ) -> Dict:
        """
        Optimize fee thresholds for maximum profitability.
        
        Args:
            premium_discount: Series of premium/discount percentages
            nav_values: Series of NAV values
            creation_fee_range: Range to test for creation fees
            redemption_fee_range: Range to test for redemption fees
            
        Returns:
            Dictionary with optimal parameters and results
        """
        best_profit = -np.inf
        best_params = None
        results = []
        
        # Test different fee combinations
        creation_fees = np.linspace(creation_fee_range[0], creation_fee_range[1], 5)
        redemption_fees = np.linspace(redemption_fee_range[0], redemption_fee_range[1], 5)
        
        for create_fee in creation_fees:
            for redeem_fee in redemption_fees:
                # Update cost model
                self.cost_model.update_assumptions(
                    creation_fee=create_fee,
                    redemption_fee=redeem_fee
                )
                
                # Generate signals
                signals = self.generate_signals(premium_discount, nav_values)
                trading_events = self.get_trading_events()
                
                total_profit = trading_events['profit'].sum()
                trade_count = len(trading_events)
                
                results.append({
                    'creation_fee': create_fee,
                    'redemption_fee': redeem_fee,
                    'total_profit': total_profit,
                    'trade_count': trade_count,
                    'avg_profit': total_profit / trade_count if trade_count > 0 else 0
                })
                
                if total_profit > best_profit:
                    best_profit = total_profit
                    best_params = {
                        'creation_fee': create_fee,
                        'redemption_fee': redeem_fee,
                        'total_profit': total_profit,
                        'trade_count': trade_count
                    }
        
        return {
            'best_params': best_params,
            'all_results': results
        }
