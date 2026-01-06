"""
Spring and Shakeout Pattern Detector
Detects Wyckoff-style spring patterns at support/resistance
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class SpringDetector:
    """Detect spring and shakeout patterns"""
    
    # Spring states
    STATE_NONE = 0
    STATE_POTENTIAL = 1
    STATE_COMPLETE = 2
    STATE_FAILED = 3
    
    def __init__(self, volume_spike_threshold: float = 1.5, max_snapback_bars: int = 3):
        """
        Initialize spring detector
        
        Args:
            volume_spike_threshold: Volume multiplier for spike detection
            max_snapback_bars: Maximum bars for price to snap back
        """
        self.volume_spike_threshold = volume_spike_threshold
        self.max_snapback_bars = max_snapback_bars
    
    def detect_spring(self, df: pd.DataFrame, reference_level: float, increment: float, 
                      setup_type: int, time_at_level: int) -> Dict:
        """
        Detect spring or shakeout pattern
        
        Args:
            df: DataFrame with OHLCV data
            reference_level: The 0/8 or 8/8 level
            increment: Murrey Math increment
            setup_type: 1 for long (spring), -1 for short (shakeout)
            time_at_level: Number of bars accumulating at level
            
        Returns:
            Dictionary with spring detection results
        """
        try:
            if len(df) < 20 or time_at_level < 6:
                return self._empty_spring()
            
            close = df['close']
            volume = df['volume']
            vol_avg = volume.tail(20).mean()
            
            # Get recent data (last 10 bars)
            recent_df = df.tail(10)
            
            if setup_type == 1:  # Long setup - detect spring below 0/8
                return self._detect_bullish_spring(recent_df, reference_level, increment, vol_avg)
            
            elif setup_type == -1:  # Short setup - detect shakeout above 8/8
                return self._detect_bearish_shakeout(recent_df, reference_level, increment, vol_avg)
            
            else:
                return self._empty_spring()
                
        except Exception as e:
            logger.error(f"Error detecting spring pattern: {e}")
            return self._empty_spring()
    
    def _detect_bullish_spring(self, df: pd.DataFrame, reference_level: float, 
                               increment: float, vol_avg: float) -> Dict:
        """
        Detect bullish spring pattern (dip below support, then snap back)
        
        Args:
            df: Recent OHLCV data
            reference_level: 0/8 level
            increment: Murrey increment
            vol_avg: Average volume
            
        Returns:
            Dictionary with spring info
        """
        close = df['close']
        low = df['low']
        volume = df['volume']
        
        # Define spring threshold (dip below -1/8)
        spring_threshold = reference_level - (increment * 0.5)
        
        # Check for dip below threshold with volume spike
        dipped = False
        dip_bar = None
        
        for i in range(len(df) - 3, len(df)):
            if i >= 0:
                if low.iloc[i] < spring_threshold and volume.iloc[i] > (vol_avg * self.volume_spike_threshold):
                    dipped = True
                    dip_bar = i
                    break
        
        if not dipped:
            return {
                'state': self.STATE_NONE,
                'score': 40.0,
                'description': 'No spring detected',
                'bars_since': 0
            }
        
        # Check for snapback above reference level
        bars_since_dip = len(df) - 1 - dip_bar
        
        if bars_since_dip <= self.max_snapback_bars:
            # Check if price has recovered
            current_close = close.iloc[-1]
            current_volume = volume.iloc[-1]
            
            if current_close > reference_level and current_volume < vol_avg:
                # Spring complete!
                return {
                    'state': self.STATE_COMPLETE,
                    'score': 100.0,
                    'description': 'Bullish spring complete - dipped and snapped back',
                    'bars_since': bars_since_dip,
                    'dip_level': low.iloc[dip_bar],
                    'recovery_level': current_close
                }
            else:
                # Still forming
                return {
                    'state': self.STATE_POTENTIAL,
                    'score': 60.0,
                    'description': 'Potential spring forming',
                    'bars_since': bars_since_dip
                }
        else:
            # Too long to snap back - failed
            return {
                'state': self.STATE_FAILED,
                'score': 0.0,
                'description': 'Spring failed - did not snap back',
                'bars_since': bars_since_dip
            }
    
    def _detect_bearish_shakeout(self, df: pd.DataFrame, reference_level: float, 
                                  increment: float, vol_avg: float) -> Dict:
        """
        Detect bearish shakeout pattern (spike above resistance, then drop back)
        
        Args:
            df: Recent OHLCV data
            reference_level: 8/8 level
            increment: Murrey increment
            vol_avg: Average volume
            
        Returns:
            Dictionary with shakeout info
        """
        close = df['close']
        high = df['high']
        volume = df['volume']
        
        # Define shakeout threshold (spike above +1/8)
        shakeout_threshold = reference_level + (increment * 0.5)
        
        # Check for spike above threshold with volume
        spiked = False
        spike_bar = None
        
        for i in range(len(df) - 3, len(df)):
            if i >= 0:
                if high.iloc[i] > shakeout_threshold and volume.iloc[i] > (vol_avg * self.volume_spike_threshold):
                    spiked = True
                    spike_bar = i
                    break
        
        if not spiked:
            return {
                'state': self.STATE_NONE,
                'score': 40.0,
                'description': 'No shakeout detected',
                'bars_since': 0
            }
        
        # Check for drop back below reference level
        bars_since_spike = len(df) - 1 - spike_bar
        
        if bars_since_spike <= self.max_snapback_bars:
            # Check if price has dropped back
            current_close = close.iloc[-1]
            current_volume = volume.iloc[-1]
            
            if current_close < reference_level and current_volume < vol_avg:
                # Shakeout complete!
                return {
                    'state': self.STATE_COMPLETE,
                    'score': 100.0,
                    'description': 'Bearish shakeout complete - spiked and dropped back',
                    'bars_since': bars_since_spike,
                    'spike_level': high.iloc[spike_bar],
                    'drop_level': current_close
                }
            else:
                # Still forming
                return {
                    'state': self.STATE_POTENTIAL,
                    'score': 60.0,
                    'description': 'Potential shakeout forming',
                    'bars_since': bars_since_spike
                }
        else:
            # Too long to drop back - failed
            return {
                'state': self.STATE_FAILED,
                'score': 0.0,
                'description': 'Shakeout failed - did not drop back',
                'bars_since': bars_since_spike
            }
    
    def _empty_spring(self) -> Dict:
        """Return empty spring analysis"""
        return {
            'state': self.STATE_NONE,
            'score': 40.0,
            'description': 'No pattern detected',
            'bars_since': 0
        }
    
    def get_state_name(self, state: int) -> str:
        """Get human-readable state name"""
        names = {
            self.STATE_NONE: "None",
            self.STATE_POTENTIAL: "Potential",
            self.STATE_COMPLETE: "Complete",
            self.STATE_FAILED: "Failed"
        }
        return names.get(state, "Unknown")
