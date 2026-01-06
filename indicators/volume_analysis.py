"""
Volume Analysis and OBV Divergence Detection
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class VolumeAnalyzer:
    """Analyze volume patterns, OBV, and detect divergences"""
    
    def __init__(self, volume_spike_threshold: float = 1.5):
        """
        Initialize volume analyzer
        
        Args:
            volume_spike_threshold: Multiplier for volume spike detection (e.g., 1.5 = 150% of average)
        """
        self.volume_spike_threshold = volume_spike_threshold
    
    def calculate_obv(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate On-Balance Volume (OBV)
        
        Args:
            df: DataFrame with close and volume columns
            
        Returns:
            Series with OBV values
        """
        close = df['close']
        volume = df['volume']
        
        # Calculate price direction
        direction = np.where(close > close.shift(1), 1, np.where(close < close.shift(1), -1, 0))
        
        # Calculate OBV
        obv = (direction * volume).cumsum()
        
        return pd.Series(obv, index=df.index)
    
    def analyze_volume_pattern(self, df: pd.DataFrame, lookback: int = 10) -> Dict:
        """
        Analyze volume pattern over lookback period
        
        Args:
            df: DataFrame with OHLCV data
            lookback: Number of bars to analyze
            
        Returns:
            Dictionary with volume analysis
        """
        try:
            if len(df) < lookback + 20:
                return self._empty_volume_analysis()
            
            # Get recent data
            recent_df = df.tail(lookback)
            
            close = recent_df['close']
            open_price = recent_df['open']
            volume = recent_df['volume']
            
            # Calculate volume average
            vol_avg = df['volume'].tail(20).mean()
            
            # Separate up and down volume
            up_vol_sum = 0.0
            down_vol_sum = 0.0
            up_count = 0
            down_count = 0
            
            for idx in range(len(recent_df)):
                vol = volume.iloc[idx]
                c = close.iloc[idx]
                o = open_price.iloc[idx]
                
                if c > o:
                    up_vol_sum += vol
                    up_count += 1
                elif c < o:
                    down_vol_sum += vol
                    down_count += 1
            
            # Calculate averages
            avg_up_vol = up_vol_sum / up_count if up_count > 0 else 0
            avg_down_vol = down_vol_sum / down_count if down_count > 0 else 0
            
            # Check for volume spike
            max_vol = volume.max()
            volume_spike_detected = max_vol > (vol_avg * self.volume_spike_threshold)
            
            # Check if volume is declining
            vol_first_half = volume.iloc[:lookback//2].mean()
            vol_second_half = volume.iloc[lookback//2:].mean()
            volume_declining = vol_second_half < vol_first_half
            
            # Calculate volume score (0-100)
            score = 0.0
            
            # Score component 1: Up/Down volume dominance (30 points)
            if avg_up_vol > avg_down_vol * 1.2:
                score += 30  # Bullish: Up volume dominant
            elif avg_down_vol > avg_up_vol * 1.2:
                score += 30  # Bearish: Down volume dominant
            
            # Score component 2: Volume declining (30 points) - Good for accumulation
            if volume_declining:
                score += 30
            
            # Score component 3: Volume spike absorbed (40 points) - Good sign
            if volume_spike_detected:
                score += 40
            
            return {
                'score': score,
                'avg_up_vol': avg_up_vol,
                'avg_down_vol': avg_down_vol,
                'up_vol_dominant': avg_up_vol > avg_down_vol,
                'down_vol_dominant': avg_down_vol > avg_up_vol,
                'volume_declining': volume_declining,
                'volume_spike_detected': volume_spike_detected,
                'volume_avg': vol_avg,
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volume pattern: {e}")
            return self._empty_volume_analysis()
    
    def _empty_volume_analysis(self) -> Dict:
        """Return empty volume analysis"""
        return {
            'score': 50.0,
            'avg_up_vol': 0,
            'avg_down_vol': 0,
            'up_vol_dominant': False,
            'down_vol_dominant': False,
            'volume_declining': False,
            'volume_spike_detected': False,
            'volume_avg': 0,
        }
    
    def detect_obv_divergence(self, df: pd.DataFrame, setup_type: int, reference_level: float) -> Dict:
        """
        Detect OBV divergence
        
        Args:
            df: DataFrame with OHLCV data
            setup_type: 1 for long (at 0/8), -1 for short (at 8/8)
            reference_level: The 0/8 or 8/8 level
            
        Returns:
            Dictionary with divergence info
        """
        try:
            if len(df) < 50:
                return self._empty_divergence()
            
            close = df['close']
            obv = self.calculate_obv(df)
            
            # Find price lows/highs near reference level
            if setup_type == 1:  # Long setup - look for bullish divergence
                # Find recent lows
                lows = []
                obv_at_lows = []
                
                for i in range(len(df) - 20, len(df)):
                    if i >= 1 and i < len(df) - 1:
                        c = close.iloc[i]
                        if c < reference_level * 1.01:  # Near 0/8
                            # Check if local low
                            if close.iloc[i] <= close.iloc[i-1] and close.iloc[i] <= close.iloc[i+1]:
                                lows.append(c)
                                obv_at_lows.append(obv.iloc[i])
                
                # Check for bullish divergence
                if len(lows) >= 2:
                    price_low_1 = lows[-2]
                    price_low_2 = lows[-1]
                    obv_low_1 = obv_at_lows[-2]
                    obv_low_2 = obv_at_lows[-1]
                    
                    # Bullish divergence: Price makes lower low, OBV makes higher low
                    if price_low_2 <= price_low_1 and obv_low_2 > obv_low_1:
                        return {
                            'divergence': 1,  # Bullish
                            'score': 100.0,
                            'type': 'bullish',
                            'description': 'Bullish divergence detected'
                        }
                    elif price_low_2 <= price_low_1 and obv_low_2 <= obv_low_1:
                        return {
                            'divergence': -1,  # Bearish (bad for long)
                            'score': 0.0,
                            'type': 'bearish',
                            'description': 'Bearish divergence detected'
                        }
            
            elif setup_type == -1:  # Short setup - look for bearish divergence
                # Find recent highs
                highs = []
                obv_at_highs = []
                
                for i in range(len(df) - 20, len(df)):
                    if i >= 1 and i < len(df) - 1:
                        c = close.iloc[i]
                        if c > reference_level * 0.99:  # Near 8/8
                            # Check if local high
                            if close.iloc[i] >= close.iloc[i-1] and close.iloc[i] >= close.iloc[i+1]:
                                highs.append(c)
                                obv_at_highs.append(obv.iloc[i])
                
                # Check for bearish divergence
                if len(highs) >= 2:
                    price_high_1 = highs[-2]
                    price_high_2 = highs[-1]
                    obv_high_1 = obv_at_highs[-2]
                    obv_high_2 = obv_at_highs[-1]
                    
                    # Bearish divergence: Price makes higher high, OBV makes lower high
                    if price_high_2 >= price_high_1 and obv_high_2 < obv_high_1:
                        return {
                            'divergence': -1,  # Bearish
                            'score': 100.0,
                            'type': 'bearish',
                            'description': 'Bearish divergence detected'
                        }
                    elif price_high_2 >= price_high_1 and obv_high_2 >= obv_high_1:
                        return {
                            'divergence': 1,  # Bullish (bad for short)
                            'score': 0.0,
                            'type': 'bullish',
                            'description': 'Bullish divergence detected'
                        }
            
            # No clear divergence - use OBV slope
            obv_slope = obv.iloc[-1] - obv.iloc[-10]
            
            if setup_type == 1 and obv_slope > 0:
                return {
                    'divergence': 0,
                    'score': 75.0,
                    'type': 'positive_slope',
                    'description': 'OBV rising (no divergence)'
                }
            elif setup_type == -1 and obv_slope < 0:
                return {
                    'divergence': 0,
                    'score': 75.0,
                    'type': 'negative_slope',
                    'description': 'OBV falling (no divergence)'
                }
            else:
                return {
                    'divergence': 0,
                    'score': 50.0,
                    'type': 'neutral',
                    'description': 'No clear OBV pattern'
                }
                
        except Exception as e:
            logger.error(f"Error detecting OBV divergence: {e}")
            return self._empty_divergence()
    
    def _empty_divergence(self) -> Dict:
        """Return empty divergence analysis"""
        return {
            'divergence': 0,
            'score': 50.0,
            'type': 'unknown',
            'description': 'Insufficient data'
        }
