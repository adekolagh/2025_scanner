"""
Probability Engine
Calculates the 0-100% probability score for each setup
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional
from indicators.murrey_math import MurreyMath
from indicators.momentum_analysis import MomentumAnalyzer
from indicators.volume_analysis import VolumeAnalyzer
from indicators.spring_detector import SpringDetector
from indicators.technical_indicators import TechnicalIndicators

logger = logging.getLogger(__name__)


class ProbabilityEngine:
    """Calculate setup probability score"""
    
    def __init__(self, config: Dict):
        """
        Initialize probability engine
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.min_time_bars = config.get('MIN_TIME_AT_LEVEL', 10)
        
        # Initialize analyzers
        self.murrey = MurreyMath(
            frame_size=config.get('MURREY_FRAME', 64),
            multiplier=config.get('MURREY_MULTIPLIER', 1.5),
            ignore_wicks=config.get('MURREY_IGNORE_WICKS', True)
        )
        self.momentum_analyzer = MomentumAnalyzer()
        self.volume_analyzer = VolumeAnalyzer(
            volume_spike_threshold=config.get('VOLUME_SPIKE_THRESHOLD', 1.5)
        )
        self.spring_detector = SpringDetector(
            volume_spike_threshold=config.get('VOLUME_SPIKE_THRESHOLD', 1.5),
            max_snapback_bars=config.get('SPRING_MAX_BARS', 3)
        )
    
    def calculate_probability(self, symbol: str, data_dict: Dict[str, pd.DataFrame], 
                             pair_classification: str, htf_momentum: Dict) -> Dict:
        """
        Calculate complete probability score for a setup
        
        Args:
            symbol: Trading symbol
            data_dict: Dictionary of {timeframe: DataFrame}
            pair_classification: TRENDING, RANGING, or MIXED
            htf_momentum: HTF momentum analysis results
            
        Returns:
            Dictionary with probability score and all components
        """
        try:
            # Get primary timeframe data (1H)
            h1_df = data_dict.get('H1')
            if h1_df is None or len(h1_df) < 100:
                logger.warning(f"Insufficient H1 data for {symbol}")
                return self._empty_probability()
            
            # Calculate Murrey Math levels
            levels = self.murrey.calculate_levels(h1_df)
            if not levels:
                logger.warning(f"Could not calculate Murrey levels for {symbol}")
                return self._empty_probability()
            
            current_price = h1_df['close'].iloc[-1]
            increment = levels.get('increment', 0)
            zone_width = increment * 1.5
            
            # Calculate Daily ATR for zone width adjustment
            d1_df = data_dict.get('D1')
            daily_atr = TechnicalIndicators.calculate_atr(d1_df) if d1_df is not None else 0
            zone_width_adaptive = max(zone_width, daily_atr * 2)
            
            # Determine setup type
            setup_type, reference_level = self._determine_setup_type(
                current_price, levels, zone_width_adaptive, htf_momentum
            )
            
            if setup_type == 0:
                # Not at 0/8 or 8/8
                return self._empty_probability()
            
            # Calculate time at level
            time_at_level = self._calculate_time_at_level(
                h1_df, reference_level, zone_width_adaptive, setup_type
            )
            
            # Component 1: Time at level score (20% weight)
            time_score = self._calculate_time_score(time_at_level)
            
            # Component 2: Volume analysis (20% weight)
            volume_analysis = self.volume_analyzer.analyze_volume_pattern(h1_df, lookback=10)
            volume_score = volume_analysis['score']
            
            # Component 3: OBV divergence (15% weight)
            obv_analysis = self.volume_analyzer.detect_obv_divergence(
                h1_df, setup_type, reference_level
            )
            obv_score = obv_analysis['score']
            
            # Component 4: Spring/shakeout pattern (10% weight)
            spring_analysis = self.spring_detector.detect_spring(
                h1_df, reference_level, increment, setup_type, time_at_level
            )
            spring_score = spring_analysis['score']
            
            # Component 5: HTF momentum (25% weight)
            combined_momentum = htf_momentum.get('combined', {}).get('momentum', 0)
            
            # Component 6: HTF alignment bonus (10% weight)
            htf_aligned = htf_momentum.get('combined', {}).get('htf_aligned', False)
            alignment_bonus = 10 if htf_aligned else 0
            
            # Calculate base probability (weighted sum)
            base_probability = (
                (time_score * 0.20) +
                (volume_score * 0.20) +
                (obv_score * 0.15) +
                (spring_score * 0.10) +
                (combined_momentum * 0.25) +
                alignment_bonus
            )
            
            # Quality bonuses
            quality_bonus = 0.0
            
            if spring_analysis['state'] == SpringDetector.STATE_COMPLETE:
                quality_bonus += 10
            
            if obv_analysis['divergence'] == 1 and setup_type == 1:
                quality_bonus += 8
            elif obv_analysis['divergence'] == -1 and setup_type == -1:
                quality_bonus += 8
            
            if time_at_level >= 12:
                quality_bonus += 7
            
            if volume_analysis['volume_spike_detected']:
                quality_bonus += 5
            
            # Adjusted probability
            adjusted_probability = min(100, base_probability + quality_bonus)
            
            # Apply HTF factor
            htf_factor = htf_momentum.get('combined', {}).get('htf_factor', 0.5)
            final_probability = adjusted_probability * htf_factor
            
            # Check 15M confirmation (if near entry)
            m15_confirmed = False
            if final_probability >= 70:
                m15_df = data_dict.get('M15')
                if m15_df is not None:
                    m15_confirmed = self._check_15m_confirmation(m15_df, setup_type)
            
            return {
                'probability': final_probability,
                'adjusted_probability': adjusted_probability,
                'setup_type': setup_type,  # 1=long, -1=short
                'setup_direction': 'LONG' if setup_type == 1 else 'SHORT',
                'reference_level': reference_level,
                'current_price': current_price,
                'murrey_levels': levels,
                'zone_width': zone_width_adaptive,
                'time_at_level': time_at_level,
                'time_score': time_score,
                'volume_score': volume_score,
                'obv_score': obv_score,
                'obv_analysis': obv_analysis,
                'spring_score': spring_score,
                'spring_analysis': spring_analysis,
                'combined_momentum': combined_momentum,
                'htf_aligned': htf_aligned,
                'htf_factor': htf_factor,
                'm15_confirmed': m15_confirmed,
                'quality_bonus': quality_bonus,
            }
            
        except Exception as e:
            logger.error(f"Error calculating probability for {symbol}: {e}")
            return self._empty_probability()
    
    def _determine_setup_type(self, current_price: float, levels: Dict, 
                              zone_width: float, htf_momentum: Dict) -> tuple:
        """
        Determine if at 0/8 (long) or 8/8 (short) setup
        
        Returns:
            Tuple of (setup_type, reference_level)
            setup_type: 1=long, -1=short, 0=none
        """
        zero_level = levels.get('0_8', 0)
        eight_level = levels.get('8_8', 0)
        
        # Check if at 0/8 (potential long)
        if self.murrey.is_at_zero_eight(current_price, levels, zone_width):
            # Check if HTF is bullish or neutral
            htf_results = htf_momentum
            weekly_dir = htf_results.get('W1', {}).get('direction', 0)
            daily_dir = htf_results.get('D1', {}).get('direction', 0)
            
            if weekly_dir == 1 or daily_dir == 1:
                return (1, zero_level)  # Long setup
        
        # Check if at 8/8 (potential short)
        if self.murrey.is_at_eight_eight(current_price, levels, zone_width):
            # Check if HTF is bearish or neutral
            htf_results = htf_momentum
            weekly_dir = htf_results.get('W1', {}).get('direction', 0)
            daily_dir = htf_results.get('D1', {}).get('direction', 0)
            
            if weekly_dir == -1 or daily_dir == -1:
                return (-1, eight_level)  # Short setup
        
        return (0, 0)  # No setup
    
    def _calculate_time_at_level(self, df: pd.DataFrame, reference_level: float, 
                                  zone_width: float, setup_type: int) -> int:
        """Calculate how many bars price has been at the level"""
        try:
            close = df['close']
            
            if setup_type == 1:  # Long at 0/8
                zone_low = reference_level - zone_width * 0.5
                zone_high = reference_level + zone_width
            else:  # Short at 8/8
                zone_low = reference_level - zone_width
                zone_high = reference_level + zone_width * 0.5
            
            # Count consecutive bars in zone
            time_at_level = 0
            for i in range(len(close) - 1, -1, -1):
                if zone_low <= close.iloc[i] <= zone_high:
                    time_at_level += 1
                else:
                    break
            
            return time_at_level
            
        except Exception as e:
            logger.error(f"Error calculating time at level: {e}")
            return 0
    
    def _calculate_time_score(self, time_at_level: int) -> float:
        """Calculate score based on time at level"""
        if time_at_level >= 16:
            return 100.0
        elif time_at_level >= self.min_time_bars:
            return 80.0
        elif time_at_level >= 6:
            return 50.0
        else:
            return time_at_level * 8.0
    
    def _check_15m_confirmation(self, m15_df: pd.DataFrame, setup_type: int) -> bool:
        """Check if 15M timeframe confirms entry"""
        try:
            if len(m15_df) < 20:
                return False
            
            close = m15_df['close']
            open_price = m15_df['open']
            
            # Calculate 15M indicators
            rsi = self.momentum_analyzer.calculate_rsi(close, 14)
            ema_8 = self.momentum_analyzer.calculate_ema(close, 8)
            
            current_rsi = rsi.iloc[-1]
            current_close = close.iloc[-1]
            current_open = open_price.iloc[-1]
            current_ema = ema_8.iloc[-1]
            
            if setup_type == 1:  # Long
                # RSI > 45, bullish candle, above EMA
                return (current_rsi > 45 and 
                       current_close > current_open and 
                       current_close > current_ema)
            else:  # Short
                # RSI < 55, bearish candle, below EMA
                return (current_rsi < 55 and 
                       current_close < current_open and 
                       current_close < current_ema)
                
        except Exception as e:
            logger.error(f"Error checking 15M confirmation: {e}")
            return False
    
    def _empty_probability(self) -> Dict:
        """Return empty probability result"""
        return {
            'probability': 0.0,
            'adjusted_probability': 0.0,
            'setup_type': 0,
            'setup_direction': 'NONE',
            'reference_level': 0,
            'current_price': 0,
            'murrey_levels': {},
            'zone_width': 0,
            'time_at_level': 0,
            'time_score': 0,
            'volume_score': 0,
            'obv_score': 0,
            'obv_analysis': {},
            'spring_score': 0,
            'spring_analysis': {},
            'combined_momentum': 0,
            'htf_aligned': False,
            'htf_factor': 0,
            'm15_confirmed': False,
            'quality_bonus': 0,
        }
