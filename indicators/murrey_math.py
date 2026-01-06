"""
Murrey Math Calculator
Calculates all 8/8 levels and zones
"""

import pandas as pd
import numpy as np
import logging
from typing import Tuple, Dict

logger = logging.getLogger(__name__)


class MurreyMath:
    """Calculate Murrey Math levels"""
    
    def __init__(self, frame_size: int = 64, multiplier: float = 1.5, ignore_wicks: bool = True):
        """
        Initialize Murrey Math calculator
        
        Args:
            frame_size: Base frame size (default 64)
            multiplier: Frame multiplier (default 1.5)
            ignore_wicks: Use only close prices instead of high/low
        """
        self.frame_size = frame_size
        self.multiplier = multiplier
        self.ignore_wicks = ignore_wicks
    
    def calculate_levels(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate all Murrey Math levels from OHLC data
        
        Args:
            df: DataFrame with columns: open, high, low, close
            
        Returns:
            Dictionary with all levels (0/8 through 8/8, plus extensions)
        """
        try:
            lookback = int(self.frame_size * self.multiplier)
            
            # Get price extremes
            if self.ignore_wicks:
                high_prices = df[['open', 'close']].max(axis=1)
                low_prices = df[['open', 'close']].min(axis=1)
            else:
                high_prices = df['high']
                low_prices = df['low']
            
            # Get highest and lowest in lookback period
            v_high = high_prices.tail(lookback).max()
            v_low = low_prices.tail(lookback).min()
            v_dist = v_high - v_low
            
            # Handle negative prices (shouldn't happen in forex/commodities, but just in case)
            tmp_high = v_high if v_low >= 0 else 0 - v_low
            tmp_low = v_low if v_low >= 0 else 0 - v_low - v_dist
            shift = v_low < 0
            
            # Murrey Math algorithm
            log_ten = np.log(10)
            log_8 = np.log(8)
            log_2 = np.log(2)
            
            sf_var = np.log(0.4 * tmp_high) / log_ten - np.floor(np.log(0.4 * tmp_high) / log_ten)
            
            if tmp_high > 25:
                SR = np.exp(log_ten * (np.floor(np.log(0.4 * tmp_high) / log_ten) + 1)) if sf_var > 0 else np.exp(log_ten * np.floor(np.log(0.4 * tmp_high) / log_ten))
            else:
                SR = 100 * np.exp(log_8 * np.floor(np.log(0.005 * tmp_high) / log_8))
            
            n_var1 = np.log(SR / (tmp_high - tmp_low)) / log_8
            n_var2 = n_var1 - np.floor(n_var1)
            N = 0 if n_var1 <= 0 else (np.floor(n_var1) if n_var2 == 0 else np.floor(n_var1) + 1)
            
            SI = SR * np.exp(-N * log_8)
            M = np.floor(1.0 / log_2 * np.log((tmp_high - tmp_low) / SI) + 0.0000001)
            I = int(np.round((tmp_high + tmp_low) * 0.5 / (SI * np.exp((M - 1) * log_2))))
            
            Bot = (I - 1) * SI * np.exp((M - 1) * log_2)
            Top = (I + 1) * SI * np.exp((M - 1) * log_2)
            
            # Check if shift is needed
            do_shift = (tmp_high - Top > 0.25 * (Top - Bot)) or (Bot - tmp_low > 0.25 * (Top - Bot))
            ER = 1 if do_shift else 0
            
            # Adjust if needed
            if ER == 1:
                MM = M + 1 if M < 2 else 0
                NN = N if M < 2 else N - 1
                final_SI = SR * np.exp(-NN * log_8)
                final_I = int(np.round((tmp_high + tmp_low) * 0.5 / (final_SI * np.exp((MM - 1) * log_2))))
                final_Bot = (final_I - 1) * final_SI * np.exp((MM - 1) * log_2)
                final_Top = (final_I + 1) * final_SI * np.exp((MM - 1) * log_2)
            else:
                final_Bot = Bot
                final_Top = Top
            
            # Calculate increment
            inc = (final_Top - final_Bot) / 8
            
            # Calculate all levels
            abs_top = -(final_Bot - 3 * inc) if shift else final_Top + 3 * inc
            
            levels = {
                'plus_3_8': abs_top,
                'plus_2_8': abs_top - inc,
                'plus_1_8': abs_top - 2 * inc,
                '8_8': abs_top - 3 * inc,
                '7_8': abs_top - 4 * inc,
                '6_8': abs_top - 5 * inc,
                '5_8': abs_top - 6 * inc,
                '4_8': abs_top - 7 * inc,
                '3_8': abs_top - 8 * inc,
                '2_8': abs_top - 9 * inc,
                '1_8': abs_top - 10 * inc,
                '0_8': abs_top - 11 * inc,
                'minus_1_8': abs_top - 12 * inc,
                'minus_2_8': abs_top - 13 * inc,
                'minus_3_8': abs_top - 14 * inc,
                'increment': inc
            }
            
            return levels
            
        except Exception as e:
            logger.error(f"Error calculating Murrey Math levels: {e}")
            return {}
    
    def get_current_position(self, current_price: float, levels: Dict[str, float]) -> Tuple[str, float]:
        """
        Determine which Murrey level price is closest to
        
        Args:
            current_price: Current market price
            levels: Dictionary of Murrey levels
            
        Returns:
            Tuple of (level_name, distance_from_level)
        """
        if not levels:
            return ("unknown", 0.0)
        
        # Find closest level
        level_names = ['0_8', '1_8', '2_8', '3_8', '4_8', '5_8', '6_8', '7_8', '8_8']
        closest_level = None
        min_distance = float('inf')
        
        for level_name in level_names:
            if level_name in levels:
                level_value = levels[level_name]
                distance = abs(current_price - level_value)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_level = level_name
        
        return (closest_level, min_distance)
    
    def is_near_level(self, current_price: float, level_value: float, zone_width: float) -> bool:
        """
        Check if price is within zone of a level
        
        Args:
            current_price: Current market price
            level_value: Murrey level value
            zone_width: Width of zone around level
            
        Returns:
            bool: True if price is within zone
        """
        return abs(current_price - level_value) <= zone_width
    
    def is_at_zero_eight(self, current_price: float, levels: Dict[str, float], zone_width: float) -> bool:
        """
        Check if price is at 0/8 level (support/buy zone)
        
        Args:
            current_price: Current market price
            levels: Murrey levels dictionary
            zone_width: Zone width
            
        Returns:
            bool: True if at 0/8
        """
        if '0_8' not in levels:
            return False
        
        zero_level = levels['0_8']
        zone_low = zero_level - zone_width * 0.5
        zone_high = zero_level + zone_width
        
        return zone_low <= current_price <= zone_high
    
    def is_at_eight_eight(self, current_price: float, levels: Dict[str, float], zone_width: float) -> bool:
        """
        Check if price is at 8/8 level (resistance/sell zone)
        
        Args:
            current_price: Current market price
            levels: Murrey levels dictionary
            zone_width: Zone width
            
        Returns:
            bool: True if at 8/8
        """
        if '8_8' not in levels:
            return False
        
        eight_level = levels['8_8']
        zone_low = eight_level - zone_width
        zone_high = eight_level + zone_width * 0.5
        
        return zone_low <= current_price <= zone_high
