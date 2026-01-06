"""
Multi-Timeframe Momentum Analysis
Analyzes Weekly, Daily, 4H, 1H momentum and alignment
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class MomentumAnalyzer:
    """Analyze momentum across multiple timeframes"""
    
    def __init__(self):
        """Initialize momentum analyzer"""
        pass
    
    def calculate_ema(self, series: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return series.ewm(span=period, adjust=False).mean()
    
    def calculate_macd(self, close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD
        
        Returns:
            Tuple of (macd_line, signal_line, histogram)
        """
        ema_fast = self.calculate_ema(close, fast)
        ema_slow = self.calculate_ema(close, slow)
        macd_line = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    def calculate_rsi(self, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> Tuple[float, float, float]:
        """
        Calculate ADX (Average Directional Index)
        
        Returns:
            Tuple of (di_plus, di_minus, adx)
        """
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        # Directional Movement
        up_move = high - high.shift()
        down_move = low.shift() - low
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        plus_dm_series = pd.Series(plus_dm, index=high.index).rolling(window=period).mean()
        minus_dm_series = pd.Series(minus_dm, index=high.index).rolling(window=period).mean()
        
        # Directional Indicators
        di_plus = 100 * (plus_dm_series / atr)
        di_minus = 100 * (minus_dm_series / atr)
        
        # ADX
        dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus)
        adx = dx.rolling(window=period).mean()
        
        # Return last values
        return (
            di_plus.iloc[-1] if len(di_plus) > 0 else 0,
            di_minus.iloc[-1] if len(di_minus) > 0 else 0,
            adx.iloc[-1] if len(adx) > 0 else 0
        )
    
    def calculate_roc(self, close: pd.Series, period: int = 10) -> pd.Series:
        """Calculate Rate of Change"""
        roc = ((close - close.shift(period)) / close.shift(period)) * 100
        return roc
    
    def analyze_timeframe(self, df: pd.DataFrame) -> Dict:
        """
        Analyze momentum for a single timeframe
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary with momentum analysis
        """
        try:
            if len(df) < 50:
                logger.warning("Insufficient data for momentum analysis")
                return self._empty_analysis()
            
            close = df['close']
            high = df['high']
            low = df['low']
            
            # Calculate indicators
            ema_8 = self.calculate_ema(close, 8)
            ema_21 = self.calculate_ema(close, 21)
            macd_line, signal_line, macd_hist = self.calculate_macd(close)
            rsi = self.calculate_rsi(close)
            di_plus, di_minus, adx = self.calculate_adx(high, low, close)
            roc = self.calculate_roc(close)
            
            # Get current values
            current_close = close.iloc[-1]
            current_ema_8 = ema_8.iloc[-1]
            current_ema_21 = ema_21.iloc[-1]
            current_macd = macd_line.iloc[-1]
            current_signal = signal_line.iloc[-1]
            current_macd_hist = macd_hist.iloc[-1]
            current_rsi = rsi.iloc[-1]
            current_roc = roc.iloc[-1]
            
            # Determine trend direction
            ema_rising = current_ema_8 > ema_8.iloc[-2] and current_ema_8 > current_ema_21
            ema_falling = current_ema_8 < ema_8.iloc[-2] and current_ema_8 < current_ema_21
            
            macd_bullish = current_macd > 0 and current_macd_hist > 0
            macd_bearish = current_macd < 0 and current_macd_hist < 0
            
            rsi_bullish = 50 < current_rsi < 75
            rsi_bearish = 25 < current_rsi < 50
            
            roc_bullish = current_roc > 0
            roc_bearish = current_roc < 0
            
            # Direction: 1=bullish, -1=bearish, 0=neutral
            direction = 0
            if ema_rising and macd_bullish:
                direction = 1
            elif ema_falling and macd_bearish:
                direction = -1
            
            # Calculate strength score (0-100)
            strength = 0.0
            if direction == 1:  # Bullish
                strength += 25 if ema_rising else 0
                strength += 25 if macd_bullish else 0
                strength += 25 if rsi_bullish else 0
                strength += 25 if roc_bullish else 0
            elif direction == -1:  # Bearish
                strength += 25 if ema_falling else 0
                strength += 25 if macd_bearish else 0
                strength += 25 if rsi_bearish else 0
                strength += 25 if roc_bearish else 0
            
            # Boost for strong ADX trend
            if adx > 25:
                strength *= 1.2
                strength = min(strength, 100)
            
            return {
                'direction': direction,  # 1, 0, -1
                'strength': strength,  # 0-100
                'ema_8': current_ema_8,
                'ema_21': current_ema_21,
                'macd_line': current_macd,
                'macd_signal': current_signal,
                'macd_hist': current_macd_hist,
                'rsi': current_rsi,
                'adx': adx,
                'di_plus': di_plus,
                'di_minus': di_minus,
                'roc': current_roc,
            }
            
        except Exception as e:
            logger.error(f"Error analyzing momentum: {e}")
            return self._empty_analysis()
    
    def _empty_analysis(self) -> Dict:
        """Return empty analysis if data insufficient"""
        return {
            'direction': 0,
            'strength': 0,
            'ema_8': 0,
            'ema_21': 0,
            'macd_line': 0,
            'macd_signal': 0,
            'macd_hist': 0,
            'rsi': 50,
            'adx': 0,
            'di_plus': 0,
            'di_minus': 0,
            'roc': 0,
        }
    
    def analyze_multi_timeframe(self, data_dict: Dict[str, pd.DataFrame]) -> Dict:
        """
        Analyze momentum across multiple timeframes
        
        Args:
            data_dict: Dictionary {timeframe: DataFrame}
                      e.g., {"W1": weekly_df, "D1": daily_df, "H4": h4_df, "H1": h1_df}
        
        Returns:
            Dictionary with multi-timeframe analysis
        """
        try:
            results = {}
            
            # Analyze each timeframe
            for tf, df in data_dict.items():
                results[tf] = self.analyze_timeframe(df)
            
            # Calculate combined momentum (weighted)
            weights = {
                'W1': 0.40,  # Weekly: 40%
                'D1': 0.30,  # Daily: 30%
                'H4': 0.20,  # 4-Hour: 20%
                'H1': 0.10,  # 1-Hour: 10%
            }
            
            combined_momentum = 0.0
            for tf, weight in weights.items():
                if tf in results:
                    combined_momentum += results[tf]['strength'] * weight
            
            # Check HTF alignment
            directions = []
            for tf in ['W1', 'D1', 'H4']:
                if tf in results:
                    directions.append(results[tf]['direction'])
            
            htf_aligned_bullish = all(d == 1 for d in directions) if directions else False
            htf_aligned_bearish = all(d == -1 for d in directions) if directions else False
            htf_aligned = htf_aligned_bullish or htf_aligned_bearish
            
            # Calculate HTF factor (weighted alignment strength)
            htf_factor = 0.0
            if htf_aligned_bullish or htf_aligned_bearish:
                htf_factor = 1.0  # Perfect alignment
            else:
                # Partial alignment
                bullish_count = sum(1 for d in directions if d == 1)
                bearish_count = sum(1 for d in directions if d == -1)
                
                if bullish_count >= 2 or bearish_count >= 2:
                    htf_factor = 0.65  # 2 out of 3 aligned
                elif bullish_count >= 1 or bearish_count >= 1:
                    htf_factor = 0.40  # 1 out of 3 aligned
                else:
                    htf_factor = 0.20  # Neutral
            
            results['combined'] = {
                'momentum': combined_momentum,
                'htf_aligned': htf_aligned,
                'htf_aligned_bullish': htf_aligned_bullish,
                'htf_aligned_bearish': htf_aligned_bearish,
                'htf_factor': htf_factor,
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe analysis: {e}")
            return {}
