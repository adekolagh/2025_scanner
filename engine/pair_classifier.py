"""
Pair Classifier
Determines if a pair is Trending, Ranging, or Mixed
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple
from indicators.momentum_analysis import MomentumAnalyzer

logger = logging.getLogger(__name__)


class PairClassifier:
    """Classify pairs as Trending, Ranging, or Mixed"""
    
    TRENDING = "TRENDING"
    RANGING = "RANGING"
    MIXED = "MIXED"
    
    def __init__(self, config: Dict):
        """
        Initialize pair classifier
        
        Args:
            config: Configuration dictionary with classification settings
        """
        self.config = config
        self.method = config.get('CLASSIFICATION_METHOD', 'MANUAL')
        self.trending_pairs = config.get('TRENDING_PAIRS', [])
        self.ranging_pairs = config.get('RANGING_PAIRS', [])
        
        # Auto-detection thresholds
        self.auto_thresholds = config.get('AUTO_CLASSIFICATION_THRESHOLDS', {})
        
        self.momentum_analyzer = MomentumAnalyzer()
    
    def classify(self, symbol: str, weekly_df: pd.DataFrame = None) -> Tuple[str, int, Dict]:
        """
        Classify a pair as TRENDING, RANGING, or MIXED
        
        Args:
            symbol: Trading symbol
            weekly_df: Weekly timeframe data (for auto-detection)
            
        Returns:
            Tuple of (classification, confidence, details)
        """
        if self.method == "MANUAL":
            return self._classify_manual(symbol)
        else:  # AUTO
            if weekly_df is None:
                logger.warning(f"No weekly data for auto-classification of {symbol}, using manual")
                return self._classify_manual(symbol)
            return self._classify_auto(symbol, weekly_df)
    
    def _classify_manual(self, symbol: str) -> Tuple[str, int, Dict]:
        """
        Manual classification based on predefined lists
        
        Returns:
            Tuple of (classification, confidence, details)
        """
        if symbol in self.trending_pairs:
            return (
                self.TRENDING,
                100,
                {
                    'method': 'manual',
                    'reason': 'In trending pairs list',
                    'weekly_adx': None,
                    'range_pct': None
                }
            )
        elif symbol in self.ranging_pairs:
            return (
                self.RANGING,
                100,
                {
                    'method': 'manual',
                    'reason': 'In ranging pairs list',
                    'weekly_adx': None,
                    'range_pct': None
                }
            )
        else:
            return (
                self.MIXED,
                100,
                {
                    'method': 'manual',
                    'reason': 'Not in any specific list',
                    'weekly_adx': None,
                    'range_pct': None
                }
            )
    
    def _classify_auto(self, symbol: str, weekly_df: pd.DataFrame) -> Tuple[str, int, Dict]:
        """
        Automatic classification based on market analysis
        
        Returns:
            Tuple of (classification, confidence, details)
        """
        try:
            if len(weekly_df) < 20:
                logger.warning(f"Insufficient data for auto-classification of {symbol}")
                return self._classify_manual(symbol)
            
            # Get weekly momentum analysis
            momentum = self.momentum_analyzer.analyze_timeframe(weekly_df)
            weekly_adx = momentum.get('adx', 0)
            
            # Calculate 12-week range percentage
            recent_weekly = weekly_df.tail(12)
            high_12w = recent_weekly['high'].max()
            low_12w = recent_weekly['low'].min()
            range_pct = ((high_12w - low_12w) / low_12w) * 100
            
            # Get thresholds
            trending_thresholds = self.auto_thresholds.get('TRENDING', {})
            ranging_thresholds = self.auto_thresholds.get('RANGING', {})
            
            min_adx_trending = trending_thresholds.get('min_weekly_adx', 30)
            min_range_trending = trending_thresholds.get('min_range_pct', 12.0)
            
            max_adx_ranging = ranging_thresholds.get('max_weekly_adx', 22)
            max_range_ranging = ranging_thresholds.get('max_range_pct', 6.0)
            
            # Classify based on criteria
            is_strong_trending = (weekly_adx > min_adx_trending and range_pct > min_range_trending)
            is_moderate_trending = (weekly_adx > 25 and range_pct > 8.0) and not is_strong_trending
            is_ranging = (weekly_adx < max_adx_ranging or range_pct < max_range_ranging)
            
            if is_strong_trending or is_moderate_trending:
                confidence = 95 if is_strong_trending else 80
                return (
                    self.TRENDING,
                    confidence,
                    {
                        'method': 'auto',
                        'reason': f'ADX {weekly_adx:.1f}, Range {range_pct:.1f}%',
                        'weekly_adx': weekly_adx,
                        'range_pct': range_pct,
                        'strength': 'strong' if is_strong_trending else 'moderate'
                    }
                )
            elif is_ranging:
                return (
                    self.RANGING,
                    85,
                    {
                        'method': 'auto',
                        'reason': f'ADX {weekly_adx:.1f}, Range {range_pct:.1f}%',
                        'weekly_adx': weekly_adx,
                        'range_pct': range_pct
                    }
                )
            else:
                return (
                    self.MIXED,
                    60,
                    {
                        'method': 'auto',
                        'reason': f'ADX {weekly_adx:.1f}, Range {range_pct:.1f}%',
                        'weekly_adx': weekly_adx,
                        'range_pct': range_pct
                    }
                )
                
        except Exception as e:
            logger.error(f"Error in auto-classification for {symbol}: {e}")
            return self._classify_manual(symbol)
    
    def get_atr_multipliers(self, classification: str) -> Dict[str, float]:
        """
        Get ATR multipliers for a classification
        
        Args:
            classification: TRENDING, RANGING, or MIXED
            
        Returns:
            Dictionary with stop, trail, target multipliers
        """
        multipliers = self.config.get('ATR_MULTIPLIERS', {})
        return multipliers.get(classification, multipliers.get('MIXED', {
            'stop': 2.25,
            'trail': 1.75,
            'target': 7.0
        }))
