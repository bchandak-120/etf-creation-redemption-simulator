"""
NAV (Net Asset Value) calculation engine for ETF Creation Redemption Simulator.

Computes daily NAV from constituent weights and prices, calculates premium/discount.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


class NavEngine:
    """Calculates NAV and premium/discount for ETF simulation."""
    
    def __init__(self):
        self.nav_data = None
        self.premium_discount = None
    
    def calculate_nav(
        self, 
        constituent_prices: pd.DataFrame, 
        weights: Dict[str, float]
    ) -> pd.Series:
        """
        Calculate daily NAV from constituent prices and weights.
        
        Args:
            constituent_prices: DataFrame of constituent prices
            weights: Dictionary of ticker -> weight
            
        Returns:
            Series of daily NAV values
        """
        # Validate inputs
        missing_tickers = set(weights.keys()) - set(constituent_prices.columns)
        if missing_tickers:
            raise ValueError(f"Missing price data for: {missing_tickers}")
        
        # Calculate weighted portfolio value
        nav = pd.Series(0.0, index=constituent_prices.index)
        
        for ticker, weight in weights.items():
            nav += constituent_prices[ticker] * weight
        
        return nav
    
    def normalize_values(
        self, 
        etf_prices: pd.Series, 
        nav_values: pd.Series
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Normalize ETF and NAV to same starting value for comparison.
        
        Args:
            etf_prices: Series of ETF prices
            nav_values: Series of NAV values
            
        Returns:
            Tuple of normalized (etf_prices, nav_values)
        """
        # Find common dates
        common_dates = etf_prices.index.intersection(nav_values.index)
        etf_aligned = etf_prices.loc[common_dates]
        nav_aligned = nav_values.loc[common_dates]
        
        if len(common_dates) == 0:
            raise ValueError("No overlapping dates between ETF and NAV data")
        
        # Normalize to first common date
        first_etf_price = etf_aligned.iloc[0]
        first_nav_value = nav_aligned.iloc[0]
        
        # Calculate normalization factor
        nav_multiplier = first_etf_price / first_nav_value
        
        # Apply normalization
        nav_normalized = nav_aligned * nav_multiplier
        
        return etf_aligned, nav_normalized
    
    def calculate_premium_discount(
        self, 
        etf_prices: pd.Series, 
        nav_values: pd.Series
    ) -> pd.Series:
        """
        Calculate premium/discount as (ETF price - NAV) / NAV.
        
        Args:
            etf_prices: Series of ETF prices
            nav_values: Series of NAV values
            
        Returns:
            Series of premium/discount percentages
        """
        # Ensure same index
        common_dates = etf_prices.index.intersection(nav_values.index)
        etf_aligned = etf_prices.loc[common_dates]
        nav_aligned = nav_values.loc[common_dates]
        
        # Calculate premium/discount
        premium_discount = (etf_aligned - nav_aligned) / nav_aligned * 100
        
        return premium_discount
    
    def get_nav_statistics(
        self, 
        premium_discount: pd.Series
    ) -> Dict[str, float]:
        """
        Calculate summary statistics for premium/discount.
        
        Args:
            premium_discount: Series of premium/discount percentages
            
        Returns:
            Dictionary of statistics
        """
        stats = {
            'mean_premium': premium_discount.mean(),
            'median_premium': premium_discount.median(),
            'std_premium': premium_discount.std(),
            'max_premium': premium_discount.max(),
            'min_premium': premium_discount.min(),
            'percent_positive': (premium_discount > 0).mean() * 100,
            'percent_negative': (premium_discount < 0).mean() * 100,
            'avg_positive': premium_discount[premium_discount > 0].mean() if (premium_discount > 0).any() else 0,
            'avg_negative': premium_discount[premium_discount < 0].mean() if (premium_discount < 0).any() else 0,
        }
        
        return stats
    
    def analyze_tracking_error(
        self, 
        etf_prices: pd.Series, 
        nav_values: pd.Series
    ) -> Dict[str, float]:
        """
        Analyze tracking error between ETF and NAV.
        
        Args:
            etf_prices: Series of ETF prices
            nav_values: Series of NAV values
            
        Returns:
            Dictionary of tracking error metrics
        """
        # Ensure same index
        common_dates = etf_prices.index.intersection(nav_values.index)
        etf_aligned = etf_prices.loc[common_dates]
        nav_aligned = nav_values.loc[common_dates]
        
        # Calculate returns
        etf_returns = etf_aligned.pct_change().dropna()
        nav_returns = nav_aligned.pct_change().dropna()
        
        # Align returns
        common_returns = etf_returns.index.intersection(nav_returns.index)
        etf_ret_aligned = etf_returns.loc[common_returns]
        nav_ret_aligned = nav_returns.loc[common_returns]
        
        # Calculate tracking error
        tracking_diff = etf_ret_aligned - nav_ret_aligned
        
        metrics = {
            'tracking_error': tracking_diff.std() * np.sqrt(252),  # Annualized
            'correlation': etf_ret_aligned.corr(nav_ret_aligned),
            'mean_return_diff': tracking_diff.mean() * 252,  # Annualized
            'tracking_error_daily': tracking_diff.std(),
        }
        
        return metrics
