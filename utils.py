"""
Utility functions for ETF Creation Redemption Simulator.

Helper functions for data processing, validation, and formatting.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import re


def validate_ticker(ticker: str) -> bool:
    """
    Validate ticker symbol format.
    
    Args:
        ticker: Ticker symbol to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not ticker or not isinstance(ticker, str):
        return False
    
    # Remove any whitespace and convert to uppercase
    ticker = ticker.strip().upper()
    
    # Basic validation: 1-5 letters, optionally with dot exchange suffix
    pattern = r'^[A-Z]{1,5}(\.[A-Z]{1,3})?$'
    return bool(re.match(pattern, ticker))


def validate_date_format(date_str: str) -> bool:
    """
    Validate date string format (YYYY-MM-DD).
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid format, False otherwise
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_weights(weights: Dict[str, float]) -> Tuple[bool, List[str]]:
    """
    Validate constituent weights.
    
    Args:
        weights: Dictionary of ticker -> weight
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not weights:
        errors.append("No weights provided")
        return False, errors
    
    total_weight = 0
    
    for ticker, weight in weights.items():
        # Validate ticker
        if not validate_ticker(ticker):
            errors.append(f"Invalid ticker format: {ticker}")
            continue
        
        # Validate weight
        if not isinstance(weight, (int, float)):
            errors.append(f"Weight must be numeric for {ticker}")
            continue
        
        if weight <= 0:
            errors.append(f"Weight must be positive for {ticker}")
            continue
        
        if weight > 1:
            errors.append(f"Weight cannot exceed 1 for {ticker}")
            continue
        
        total_weight += weight
    
    # Check total weight
    if abs(total_weight - 1.0) > 0.01:  # Allow small rounding error
        errors.append(f"Weights sum to {total_weight:.3f}, should sum to 1.0")
    
    return len(errors) == 0, errors


def format_currency(value: float, decimals: int = 2) -> str:
    """
    Format value as currency string.
    
    Args:
        value: Numeric value to format
        decimals: Number of decimal places
        
    Returns:
        Formatted currency string
    """
    if pd.isna(value):
        return "N/A"
    
    return f"${value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format value as percentage string.
    
    Args:
        value: Numeric value (as decimal, e.g., 0.025 for 2.5%)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if pd.isna(value):
        return "N/A"
    
    return f"{value * 100:.{decimals}f}%"


def format_bps(value: float) -> str:
    """
    Format value as basis points.
    
    Args:
        value: Numeric value (as decimal)
        
    Returns:
        Formatted basis points string
    """
    if pd.isna(value):
        return "N/A"
    
    return f"{value * 10000:.0f} bps"


def get_date_range(years_back: int = 1) -> Tuple[str, str]:
    """
    Get date range for n years back from today.
    
    Args:
        years_back: Number of years to go back
        
    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years_back)
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')


def parse_constituents_input(input_str: str) -> Dict[str, float]:
    """
    Parse constituents input string into dictionary.
    
    Expected format: "TICKER1:weight1,TICKER2:weight2"
    
    Args:
        input_str: Input string to parse
        
    Returns:
        Dictionary of ticker -> weight
    """
    constituents = {}
    
    if not input_str or not input_str.strip():
        return constituents
    
    # Split by comma
    pairs = input_str.split(',')
    
    for pair in pairs:
        pair = pair.strip()
        if not pair:
            continue
        
        # Split by colon
        if ':' not in pair:
            continue
        
        ticker, weight_str = pair.split(':', 1)
        ticker = ticker.strip().upper()
        weight_str = weight_str.strip()
        
        try:
            weight = float(weight_str)
            constituents[ticker] = weight
        except ValueError:
            continue
    
    return constituents


def create_sample_constituents() -> Dict[str, float]:
    """
    Create sample constituent weights for demonstration.
    
    Returns:
        Dictionary of sample constituents
    """
    return {
        'AAPL': 0.07,
        'MSFT': 0.07,
        'AMZN': 0.03,
        'NVDA': 0.04,
        'GOOGL': 0.02,
        'META': 0.02,
        'BRK-B': 0.02,
        'JNJ': 0.01,
        'V': 0.01,
        'PG': 0.01
    }


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe ratio for a series of returns.
    
    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate (as decimal)
        
    Returns:
        Sharpe ratio
    """
    if len(returns) < 2:
        return np.nan
    
    # Calculate excess returns
    excess_returns = returns - risk_free_rate / 252
    
    # Calculate Sharpe ratio
    if excess_returns.std() == 0:
        return 0
    
    sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
    return sharpe


def calculate_max_drawdown(values: pd.Series) -> Dict[str, float]:
    """
    Calculate maximum drawdown and related metrics.
    
    Args:
        values: Series of portfolio values
        
    Returns:
        Dictionary with drawdown metrics
    """
    if len(values) < 2:
        return {'max_drawdown': 0, 'max_drawdown_pct': 0}
    
    # Calculate running maximum
    running_max = values.expanding().max()
    
    # Calculate drawdown
    drawdown = values - running_max
    drawdown_pct = drawdown / running_max
    
    max_drawdown = drawdown.min()
    max_drawdown_pct = drawdown_pct.min()
    
    return {
        'max_drawdown': max_drawdown,
        'max_drawdown_pct': max_drawdown_pct,
        'max_drawdown_bps': max_drawdown_pct * 10000
    }


def resample_data(data: pd.DataFrame, frequency: str = 'W') -> pd.DataFrame:
    """
    Resample time series data to different frequency.
    
    Args:
        data: DataFrame with datetime index
        frequency: Resampling frequency ('D', 'W', 'M', 'Q', 'Y')
        
    Returns:
        Resampled DataFrame
    """
    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("Data must have DatetimeIndex")
    
    # Define resampling rules
    resample_rules = {
        'D': '1D',
        'W': '1W',
        'M': '1M',
        'Q': '1Q',
        'Y': '1Y'
    }
    
    if frequency not in resample_rules:
        raise ValueError(f"Invalid frequency: {frequency}")
    
    # Resample
    resampled = data.resample(resample_rules[frequency]).last()
    
    return resampled.dropna()


def get_trading_days(start_date: str, end_date: str) -> pd.DatetimeIndex:
    """
    Get trading days between two dates (excludes weekends).
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        DatetimeIndex of trading days
    """
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    # Create date range
    all_dates = pd.date_range(start=start, end=end, freq='D')
    
    # Filter out weekends
    trading_days = all_dates[all_dates.dayofweek < 5]
    
    return trading_days


def clean_numeric_input(value: Any, default: float = 0.0) -> float:
    """
    Clean and validate numeric input.
    
    Args:
        value: Input value to clean
        default: Default value if invalid
        
    Returns:
        Cleaned numeric value
    """
    try:
        if isinstance(value, str):
            value = value.replace('%', '').replace('$', '').replace(',', '').strip()
        
        return float(value)
    except (ValueError, TypeError):
        return default


def generate_report_summary(results: Dict) -> str:
    """
    Generate a text summary of simulation results.
    
    Args:
        results: Simulation results dictionary
        
    Returns:
        Formatted summary string
    """
    if not results:
        return "No results available"
    
    metadata = results.get('metadata', {})
    stats = results.get('statistics', {})
    
    summary = f"""
ETF Creation Redemption Simulation Report
========================================

ETF: {metadata.get('etf_ticker', 'N/A')}
Period: {metadata.get('start_date', 'N/A')} to {metadata.get('end_date', 'N/A')}
Total Days: {metadata.get('total_days', 'N/A')}

Key Metrics:
-----------
Average Premium: {format_percentage(stats.get('nav_stats', {}).get('mean_premium', 0) / 100)}
Average Discount: {format_percentage(stats.get('nav_stats', {}).get('avg_negative', 0) / 100)}
Creation Events: {stats.get('arbitrage_stats', {}).get('creation_events', 0)}
Redemption Events: {stats.get('arbitrage_stats', {}).get('redemption_events', 0)}
Total Arbitrage Profit: {format_currency(stats.get('arbitrage_stats', {}).get('total_profit', 0))}
Win Rate: {format_percentage(stats.get('arbitrage_stats', {}).get('win_rate', 0))}
Tracking Error: {format_percentage(stats.get('tracking_stats', {}).get('tracking_error', 0))}
Correlation: {stats.get('tracking_stats', {}).get('correlation', 0):.3f}
"""
    
    return summary.strip()
