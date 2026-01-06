"""
Yahoo Finance Data Fetcher (Fallback)
Used when MT5 is unavailable or for backtesting
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class YahooFinanceFetcher:
    """Fetch market data from Yahoo Finance"""
    
    # Symbol mapping: Standard → Yahoo Finance format
    SYMBOL_MAP = {
        # Forex
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "USDJPY": "USDJPY=X",
        "AUDUSD": "AUDUSD=X",
        "USDCAD": "USDCAD=X",
        "USDCHF": "USDCHF=X",
        "NZDUSD": "NZDUSD=X",
        "EURGBP": "EURGBP=X",
        "EURJPY": "EURJPY=X",
        
        # Metals
        "XAUUSD": "GC=F",  # Gold futures
        "XAGUSD": "SI=F",  # Silver futures
        
        # Commodities
        "USOIL": "CL=F",   # WTI Crude Oil futures
        "UKOUSD": "BZ=F",  # Brent Crude futures
        "NATGAS": "NG=F",  # Natural Gas futures
        
        # Indices
        "US500": "^GSPC",  # S&P 500
        "NAS100": "^IXIC", # NASDAQ
        "US30": "^DJI",    # Dow Jones
        
        # Crypto
        "BTCUSD": "BTC-USD",
        "ETHUSD": "ETH-USD",
    }
    
    # Reverse mapping for display
    REVERSE_MAP = {v: k for k, v in SYMBOL_MAP.items()}
    
    def __init__(self):
        """Initialize Yahoo Finance fetcher"""
        pass
    
    def get_yahoo_symbol(self, symbol: str) -> str:
        """
        Convert standard symbol to Yahoo Finance format
        
        Args:
            symbol: Standard symbol (e.g., "XAUUSD")
            
        Returns:
            Yahoo Finance symbol (e.g., "GC=F")
        """
        return self.SYMBOL_MAP.get(symbol, symbol)
    
    def get_ohlcv(self, symbol: str, timeframe: str, bars: int = 1000) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV data from Yahoo Finance
        
        Args:
            symbol: Trading symbol (standard format)
            timeframe: Timeframe ("M15", "H1", "H4", "D1", "W1")
            bars: Number of bars to fetch
            
        Returns:
            DataFrame with columns: time, open, high, low, close, volume
        """
        try:
            # Convert symbol
            yf_symbol = self.get_yahoo_symbol(symbol)
            
            # Map timeframe to Yahoo Finance interval
            interval_map = {
                "M15": "15m",
                "M30": "30m",
                "H1": "1h",
                "H4": "4h",  # Not directly supported, will use 1h and resample
                "D1": "1d",
                "W1": "1wk",
            }
            
            interval = interval_map.get(timeframe)
            if interval is None:
                logger.error(f"Unsupported timeframe for Yahoo Finance: {timeframe}")
                return None
            
            # Calculate period based on bars and timeframe
            period_map = {
                "M15": timedelta(days=bars * 15 // (60 * 24) + 7),  # Add buffer
                "M30": timedelta(days=bars * 30 // (60 * 24) + 7),
                "H1": timedelta(days=bars // 24 + 7),
                "H4": timedelta(days=bars * 4 // 24 + 7),
                "D1": timedelta(days=bars + 30),
                "W1": timedelta(weeks=bars + 4),
            }
            
            period = period_map.get(timeframe, timedelta(days=365))
            start_date = datetime.now() - period
            end_date = datetime.now()
            
            # Fetch data
            logger.debug(f"Fetching {yf_symbol} from Yahoo Finance...")
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if df.empty:
                logger.warning(f"No data for {symbol} ({yf_symbol}) from Yahoo Finance")
                return None
            
            # Resample for H4 if needed (Yahoo doesn't support 4h directly)
            if timeframe == "H4" and interval == "1h":
                df = df.resample('4H').agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum'
                }).dropna()
            
            # Standardize column names
            df = df.reset_index()
            df = df.rename(columns={
                'Date': 'time',
                'Datetime': 'time',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Limit to requested bars
            df = df.tail(bars)
            
            # Handle missing volume (some forex pairs don't have volume)
            if df['volume'].sum() == 0:
                # Use price volatility as proxy for volume
                df['volume'] = (df['high'] - df['low']) * 1000000
            
            logger.debug(f"Fetched {len(df)} bars for {symbol} from Yahoo Finance")
            
            return df[['time', 'open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            logger.error(f"Error fetching {symbol} from Yahoo Finance: {e}")
            return None
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if symbol is available on Yahoo Finance
        
        Args:
            symbol: Standard symbol
            
        Returns:
            bool: True if available
        """
        try:
            yf_symbol = self.get_yahoo_symbol(symbol)
            ticker = yf.Ticker(yf_symbol)
            
            # Try to get info
            info = ticker.info
            
            return info is not None and 'regularMarketPrice' in info
            
        except Exception as e:
            logger.debug(f"Symbol {symbol} not available on Yahoo Finance: {e}")
            return False
