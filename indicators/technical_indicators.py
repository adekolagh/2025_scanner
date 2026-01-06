"""
Technical Indicators Helper
Additional technical indicators not covered in other modules
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Calculate various technical indicators"""
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
        """
        Calculate Average True Range (ATR)
        
        Args:
            df: DataFrame with high, low, close columns
            period: ATR period (default 14)
            
        Returns:
            Current ATR value
        """
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            # True Range components
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            # True Range = max of three components
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # ATR = moving average of TR
            atr = tr.rolling(window=period).mean()
            
            return atr.iloc[-1] if len(atr) > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return 0.0
    
    @staticmethod
    def calculate_sma(series: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return series.rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(series: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return series.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_bollinger_bands(close: pd.Series, period: int = 20, std: float = 2.0) -> tuple:
        """
        Calculate Bollinger Bands
        
        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        middle = close.rolling(window=period).mean()
        std_dev = close.rolling(window=period).std()
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        return upper, middle, lower
    
    @staticmethod
    def calculate_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> tuple:
        """
        Calculate Stochastic Oscillator
        
        Returns:
            Tuple of (%K, %D)
        """
        high = df['high']
        low = df['low']
        close = df['close']
        
        # %K = (Close - Lowest Low) / (Highest High - Lowest Low) * 100
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=d_period).mean()
        
        return k, d
    
    @staticmethod
    def calculate_momentum(close: pd.Series, period: int = 10) -> pd.Series:
        """Calculate Momentum indicator"""
        return close - close.shift(period)
    
    @staticmethod
    def detect_crossover(series1: pd.Series, series2: pd.Series) -> bool:
        """
        Detect if series1 crossed above series2
        
        Returns:
            True if crossover occurred in last bar
        """
        if len(series1) < 2 or len(series2) < 2:
            return False
        
        # Current: series1 > series2
        # Previous: series1 <= series2
        return (series1.iloc[-1] > series2.iloc[-1] and 
                series1.iloc[-2] <= series2.iloc[-2])
    
    @staticmethod
    def detect_crossunder(series1: pd.Series, series2: pd.Series) -> bool:
        """
        Detect if series1 crossed below series2
        
        Returns:
            True if crossunder occurred in last bar
        """
        if len(series1) < 2 or len(series2) < 2:
            return False
        
        # Current: series1 < series2
        # Previous: series1 >= series2
        return (series1.iloc[-1] < series2.iloc[-1] and 
                series1.iloc[-2] >= series2.iloc[-2])
