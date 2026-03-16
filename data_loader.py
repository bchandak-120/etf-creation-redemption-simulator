"""
Data loading module for ETF Creation Redemption Simulator.

Handles fetching historical price data for ETFs and constituents using yfinance.
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class DataLoader:
    """Handles loading and cleaning market data for ETF simulation."""
    
    def __init__(self):
        self.data_cache = {}
    
    def fetch_price_data(
        self, 
        tickers: List[str], 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """
        Fetch historical price data for given tickers.
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            
        Returns:
            DataFrame with adjusted close prices for all tickers
        """
        try:
            # Download data individually for more reliable data fetching
            price_dict = {}
            
            for ticker in tickers:
                try:
                    ticker_data = yf.download(
                        ticker, 
                        start=start_date, 
                        end=end_date,
                        progress=False
                    )
                    
                    if not ticker_data.empty:
                        # Extract price data based on column structure
                        if isinstance(ticker_data.columns, pd.MultiIndex):
                            # MultiIndex case - extract Close price
                            if 'Close' in ticker_data.columns.get_level_values(0):
                                price_series = ticker_data.xs('Close', axis=1, level=0)
                                if ticker in price_series.columns:
                                    price_dict[ticker] = price_series[ticker]
                                    print(f"Successfully fetched Close data for {ticker}")
                                else:
                                    print(f"Close data not found for {ticker}")
                                    continue
                            else:
                                print(f"No Close data available for {ticker}")
                                continue
                        else:
                            # Single level columns
                            if 'Close' in ticker_data.columns:
                                price_dict[ticker] = ticker_data['Close']
                            elif 'Adj Close' in ticker_data.columns:
                                price_dict[ticker] = ticker_data['Adj Close']
                            else:
                                # Use first column as fallback
                                price_dict[ticker] = ticker_data.iloc[:, 0]
                                print(f"Using first column for {ticker} (Close not available)")
                        
                        print(f"Successfully fetched data for {ticker}")
                    else:
                        print(f"No data available for {ticker}")
                        
                except Exception as e:
                    print(f"Failed to fetch {ticker}: {str(e)}")
                    continue
            
            if not price_dict:
                raise ValueError("No valid data fetched for any ticker")
            
            # Create DataFrame from dictionary
            # Align all series to common date index
            common_index = None
            for ticker, series in price_dict.items():
                if common_index is None:
                    common_index = series.index
                else:
                    common_index = common_index.intersection(series.index)
            
            # Filter all series to common dates and create DataFrame
            aligned_data = {}
            for ticker, series in price_dict.items():
                aligned_data[ticker] = series.loc[common_index]
            
            prices = pd.DataFrame(aligned_data)
            
            # Clean and validate data
            prices = self._clean_price_data(prices)
            
            return prices
            
        except Exception as e:
            raise ValueError(f"Failed to fetch price data: {str(e)}")
    
    def _clean_price_data(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate price data.
        
        Args:
            prices: Raw price DataFrame
            
        Returns:
            Cleaned price DataFrame
        """
        # Forward fill missing values (limited)
        prices = prices.ffill(limit=5)
        
        # Drop any remaining NaN rows
        prices = prices.dropna()
        
        # Remove any zero or negative prices
        prices = prices[prices > 0]
        
        return prices
    
    def validate_constituents(
        self, 
        etf_ticker: str, 
        constituents: Dict[str, float]
    ) -> Tuple[Dict[str, float], List[str]]:
        """
        Validate constituent data and weights.
        
        Args:
            etf_ticker: ETF ticker symbol
            constituents: Dictionary of ticker -> weight
            
        Returns:
            Tuple of (cleaned constituents, list of invalid tickers)
        """
        valid_constituents = {}
        invalid_tickers = []
        
        for ticker, weight in constituents.items():
            if weight <= 0 or weight > 1:
                invalid_tickers.append(f"{ticker} (invalid weight: {weight})")
                continue
                
            try:
                # Test if ticker is valid by fetching recent data
                test_data = yf.Ticker(ticker)
                if not test_data.history(period="5d").empty:
                    valid_constituents[ticker] = weight
                else:
                    invalid_tickers.append(f"{ticker} (no data found)")
            except:
                invalid_tickers.append(f"{ticker} (fetch error)")
        
        # Normalize weights if they don't sum to 1
        total_weight = sum(valid_constituents.values())
        if total_weight != 1.0 and total_weight > 0:
            valid_constituents = {
                ticker: weight / total_weight 
                for ticker, weight in valid_constituents.items()
            }
        
        return valid_constituents, invalid_tickers
    
    def get_default_constituents(self, etf_ticker: str) -> Dict[str, float]:
        """
        Get default constituent weights for common ETFs.
        
        Args:
            etf_ticker: ETF ticker symbol
            
        Returns:
            Dictionary of ticker -> weight
        """
        default_baskets = {
            'SPY': {
                'AAPL': 0.07, 'MSFT': 0.07, 'AMZN': 0.03, 'NVDA': 0.04,
                'GOOGL': 0.02, 'META': 0.02, 'BRK-B': 0.02, 'JNJ': 0.01,
                'V': 0.01, 'PG': 0.01
            },
            'QQQ': {
                'AAPL': 0.12, 'MSFT': 0.12, 'AMZN': 0.06, 'NVDA': 0.07,
                'GOOGL': 0.04, 'META': 0.04, 'TSLA': 0.04, 'ADBE': 0.02,
                'NFLX': 0.02, 'CSCO': 0.01
            },
            'IWM': {
                'SPY': 1.0  # Use SPY as proxy for small cap
            }
        }
        
        return default_baskets.get(etf_ticker.upper(), {'SPY': 1.0})
