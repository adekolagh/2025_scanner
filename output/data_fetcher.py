"""
Unified Data Fetcher
Tries MT5 first, falls back to Yahoo Finance if unavailable
"""

import pandas as pd
import logging
from typing import Optional, Dict, List
from data.mt5_connector import MT5Connector
from data.yahoo_fetcher import YahooFinanceFetcher

logger = logging.getLogger(__name__)


class DataFetcher:
    """
    Unified data fetcher with automatic fallback
    Priority: MT5 → Yahoo Finance
    """
    
    def __init__(self, config: Dict):
        """
        Initialize data fetcher
        
        Args:
            config: Configuration dictionary from config.py
        """
        self.config = config
        self.mt5_enabled = config.get('MT5_ENABLED', True)
        self.yahoo_enabled = config.get('YAHOO_FINANCE_ENABLED', True)
        self.broker = config.get('MT5_BROKER', 'Exness')
        self.configured_broker = self.broker  # Remember original
        
        # Initialize connectors
        self.mt5 = None
        self.yahoo = YahooFinanceFetcher()
        
        # Connection status
        self.mt5_connected = False
        self.primary_source = None
        
        # Initialize MT5 if enabled
        if self.mt5_enabled:
            self._init_mt5()
    
    def _init_mt5(self):
        """Initialize MT5 connection with auto-broker fallback"""
        # List of brokers to try (primary first, then fallbacks)
        all_mt5_configs = self.config.get('MT5_CONFIG', {})
        
        # Start with configured broker
        brokers_to_try = [self.broker]
        
        # Add other brokers as fallbacks
        for broker_name in all_mt5_configs.keys():
            if broker_name != self.broker:
                brokers_to_try.append(broker_name)
        
        logger.info(f"🔍 Will try brokers in order: {', '.join(brokers_to_try)}")
        
        # Try each broker
        for broker_name in brokers_to_try:
            try:
                mt5_config = all_mt5_configs.get(broker_name)
                if mt5_config is None:
                    logger.debug(f"⚠️ No config for {broker_name}, skipping")
                    continue
                
                logger.info(f"🔌 Attempting to connect to {broker_name}...")
                
                self.mt5 = MT5Connector(mt5_config)
                self.mt5_connected = self.mt5.connect()
                
                if self.mt5_connected:
                    self.broker = broker_name  # Update active broker
                    self.primary_source = "MT5"
                    logger.info(f"✅ PRIMARY DATA SOURCE: MT5 ({broker_name})")
                    logger.info(f"✅ Successfully connected to {broker_name}!")
                    return  # Success! Exit the loop
                else:
                    logger.warning(f"❌ {broker_name} connection failed, trying next broker...")
                    
            except Exception as e:
                logger.error(f"❌ {broker_name} error: {e}")
                continue
        
        # If we get here, all brokers failed
        logger.error("🚨 ALL BROKERS FAILED! Falling back to Yahoo Finance")
        self.mt5_connected = False
        self.primary_source = "Yahoo Finance"
    
    def get_data(self, symbol: str, timeframe: str, bars: int = 1000) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV data with automatic fallback
        
        Args:
            symbol: Trading symbol (standard format)
            timeframe: Timeframe ("M15", "H1", "H4", "D1", "W1")
            bars: Number of bars to fetch
            
        Returns:
            DataFrame with OHLCV data or None
        """
        # Apply symbol mapping if needed
        broker_symbol = self._map_symbol(symbol)
        
        # Try MT5 first
        if self.mt5_connected and self.mt5 is not None:
            try:
                df = self.mt5.get_ohlcv(broker_symbol, timeframe, bars)
                if df is not None and len(df) > 0:
                    logger.debug(f"✅ {symbol} data from MT5")
                    return df
                else:
                    logger.debug(f"⚠️ No MT5 data for {symbol}, trying Yahoo Finance...")
            except Exception as e:
                logger.error(f"MT5 fetch error for {symbol}: {e}")
        
        # Fallback to Yahoo Finance
        if self.yahoo_enabled:
            try:
                df = self.yahoo.get_ohlcv(symbol, timeframe, bars)
                if df is not None and len(df) > 0:
                    logger.debug(f"✅ {symbol} data from Yahoo Finance")
                    return df
                else:
                    logger.warning(f"❌ No data for {symbol} from any source")
            except Exception as e:
                logger.error(f"Yahoo Finance fetch error for {symbol}: {e}")
        
        return None
    
    def get_multi_timeframe_data(self, symbol: str, timeframes: List[str], bars: int = 1000) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple timeframes at once
        
        Args:
            symbol: Trading symbol
            timeframes: List of timeframes ["W1", "D1", "H4", "H1", "M15"]
            bars: Number of bars per timeframe
            
        Returns:
            Dictionary {timeframe: DataFrame}
        """
        result = {}
        
        for tf in timeframes:
            df = self.get_data(symbol, tf, bars)
            if df is not None:
                result[tf] = df
            else:
                logger.warning(f"Failed to fetch {symbol} {tf}")
        
        return result
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if symbol is available from any source
        
        Args:
            symbol: Trading symbol
            
        Returns:
            bool: True if symbol is available
        """
        broker_symbol = self._map_symbol(symbol)
        
        # Try MT5 first
        if self.mt5_connected and self.mt5 is not None:
            if self.mt5.validate_symbol(broker_symbol):
                return True
        
        # Try Yahoo Finance
        if self.yahoo_enabled:
            if self.yahoo.validate_symbol(symbol):
                return True
        
        return False
    
    def _map_symbol(self, symbol: str) -> str:
        """
        Map symbol between brokers if active broker different from configured
        
        Args:
            symbol: Symbol in configured broker format
            
        Returns:
            Symbol in active broker format
        """
        # If we're using the configured broker, no mapping needed
        if self.broker == self.configured_broker:
            return symbol
        
        # Need to map from configured broker to active broker
        broker_symbols = self.config.get('BROKER_SYMBOLS', {})
        
        # Find which standard symbol this is
        configured_symbols = broker_symbols.get(self.configured_broker, {})
        standard_symbol = None
        
        # Search through symbol types
        for symbol_type in ['TRENDING', 'RANGING', 'MIXED']:
            symbols_list = configured_symbols.get(symbol_type, [])
            if symbol in symbols_list:
                # Find its position
                idx = symbols_list.index(symbol)
                # Get corresponding symbol from active broker
                active_symbols = broker_symbols.get(self.broker, {}).get(symbol_type, [])
                if idx < len(active_symbols):
                    mapped = active_symbols[idx]
                    logger.info(f"🔄 Mapped {symbol} ({self.configured_broker}) → {mapped} ({self.broker})")
                    return mapped
        
        # If no mapping found, return as-is
        logger.warning(f"⚠️ Could not map {symbol} from {self.configured_broker} to {self.broker}")
        return symbol
    
    def get_available_pairs(self) -> List[str]:
        """
        Get list of all configured pairs
        
        Returns:
            List of symbol names
        """
        all_pairs = self.config.get('ALL_PAIRS', [])
        
        # Validate each pair
        available = []
        for pair in all_pairs:
            if self.validate_symbol(pair):
                available.append(pair)
            else:
                logger.warning(f"Pair {pair} not available from any data source")
        
        return available
    
    def disconnect(self):
        """Disconnect from all data sources"""
        if self.mt5 is not None and self.mt5_connected:
            self.mt5.disconnect()
            self.mt5_connected = False
        
        logger.info("Disconnected from all data sources")
    
    def get_source_info(self) -> Dict:
        """
        Get information about active data sources
        
        Returns:
            Dictionary with source information
        """
        return {
            'primary_source': self.primary_source,
            'mt5_enabled': self.mt5_enabled,
            'mt5_connected': self.mt5_connected,
            'mt5_broker': self.broker if self.mt5_connected else None,
            'yahoo_enabled': self.yahoo_enabled,
            'fallback_available': self.yahoo_enabled,
        }
