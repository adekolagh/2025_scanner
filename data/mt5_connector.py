"""
MetaTrader 5 Data Connector
Handles connection and data fetching from MT5 terminals
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class MT5Connector:
    """Connect to MetaTrader 5 and fetch market data"""
    
    def __init__(self, config: Dict):
        """
        Initialize MT5 connector
        
        Args:
            config: Dictionary with login, password, server, etc.
        """
        self.config = config
        self.connected = False
        
    def connect(self) -> bool:
        """
        Connect to MT5 terminal
        
        Returns:
            bool: True if connected successfully
        """
        try:
            # Initialize MT5
            if not mt5.initialize():
                logger.error(f"MT5 initialize() failed, error code: {mt5.last_error()}")
                return False
            
            # Login to account
            authorized = mt5.login(
                login=self.config['login'],
                password=self.config['password'],
                server=self.config['server'],
                timeout=self.config.get('timeout', 60000)
            )
            
            if not authorized:
                logger.error(f"MT5 login failed, error code: {mt5.last_error()}")
                mt5.shutdown()
                return False
            
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Failed to get account info")
                mt5.shutdown()
                return False
            
            logger.info(f"Connected to MT5: {account_info.server}, Login: {account_info.login}")
            logger.info(f"Balance: ${account_info.balance:.2f}, Equity: ${account_info.equity:.2f}")
            
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"MT5 connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MT5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("Disconnected from MT5")
    
    def get_ohlcv(self, symbol: str, timeframe: str, bars: int = 1000) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV data for a symbol
        
        Args:
            symbol: Trading symbol (e.g., "XAUUSD", "EURUSD")
            timeframe: Timeframe ("M15", "H1", "H4", "D1", "W1")
            bars: Number of bars to fetch
            
        Returns:
            DataFrame with columns: time, open, high, low, close, volume, tick_volume
        """
        if not self.connected:
            logger.error("Not connected to MT5")
            return None
        
        try:
            # Map timeframe string to MT5 constant
            tf_map = {
                "M1": mt5.TIMEFRAME_M1,
                "M5": mt5.TIMEFRAME_M5,
                "M15": mt5.TIMEFRAME_M15,
                "M30": mt5.TIMEFRAME_M30,
                "H1": mt5.TIMEFRAME_H1,
                "H4": mt5.TIMEFRAME_H4,
                "D1": mt5.TIMEFRAME_D1,
                "W1": mt5.TIMEFRAME_W1,
                "MN1": mt5.TIMEFRAME_MN1,
            }
            
            mt5_timeframe = tf_map.get(timeframe)
            if mt5_timeframe is None:
                logger.error(f"Invalid timeframe: {timeframe}")
                return None
            
            # Fetch rates
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, bars)
            
            if rates is None or len(rates) == 0:
                logger.warning(f"No data for {symbol} {timeframe}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Rename columns to standard format
            df = df.rename(columns={
                'tick_volume': 'tick_volume',
                'spread': 'spread',
                'real_volume': 'volume'
            })
            
            # Use tick_volume if real_volume is 0 (common for forex)
            if df['volume'].sum() == 0 and 'tick_volume' in df.columns:
                df['volume'] = df['tick_volume']
            
            logger.debug(f"Fetched {len(df)} bars for {symbol} {timeframe}")
            
            return df[['time', 'open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        Get symbol information (point size, digits, etc.)
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with symbol info
        """
        if not self.connected:
            return None
        
        try:
            info = mt5.symbol_info(symbol)
            if info is None:
                return None
            
            return {
                'symbol': info.name,
                'description': info.description,
                'point': info.point,
                'digits': info.digits,
                'spread': info.spread,
                'trade_contract_size': info.trade_contract_size,
                'trade_tick_size': info.trade_tick_size,
                'trade_tick_value': info.trade_tick_value,
                'min_volume': info.volume_min,
                'max_volume': info.volume_max,
                'volume_step': info.volume_step,
            }
            
        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
            return None
    
    def get_available_symbols(self) -> List[str]:
        """
        Get list of all available symbols
        
        Returns:
            List of symbol names
        """
        if not self.connected:
            return []
        
        try:
            symbols = mt5.symbols_get()
            if symbols is None:
                return []
            
            return [s.name for s in symbols]
            
        except Exception as e:
            logger.error(f"Error getting symbols: {e}")
            return []
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if symbol exists and is tradable
        
        Args:
            symbol: Trading symbol
            
        Returns:
            bool: True if symbol is valid
        """
        if not self.connected:
            return False
        
        try:
            info = mt5.symbol_info(symbol)
            if info is None:
                return False
            
            # Check if symbol is visible (tradable)
            if not info.visible:
                # Try to enable symbol
                if not mt5.symbol_select(symbol, True):
                    logger.warning(f"Symbol {symbol} not available")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating symbol {symbol}: {e}")
            return False
