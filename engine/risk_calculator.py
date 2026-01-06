"""
Risk Calculator
Calculates stops, targets, position sizing based on Livermore strategy
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict
from indicators.technical_indicators import TechnicalIndicators

logger = logging.getLogger(__name__)


class RiskCalculator:
    """Calculate trade risk parameters"""
    
    def __init__(self, config: Dict):
        """
        Initialize risk calculator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.account_size = config.get('ACCOUNT_SIZE', 10000)
        self.risk_percent = config.get('RISK_PER_TRADE', 1.0)
        self.move_to_be_at = config.get('MOVE_TO_BE_AT_R', 2.0)
        self.start_trail_at = config.get('START_TRAIL_AT_R', 3.0)
    
    def calculate_risk_parameters(self, symbol: str, probability_result: Dict, 
                                  pair_classification: str, daily_df: pd.DataFrame,
                                  combined_momentum: float) -> Dict:
        """
        Calculate complete risk parameters for a setup
        
        Args:
            symbol: Trading symbol
            probability_result: Results from probability engine
            pair_classification: TRENDING, RANGING, or MIXED
            daily_df: Daily timeframe DataFrame
            combined_momentum: Combined momentum score (0-100)
            
        Returns:
            Dictionary with all risk parameters
        """
        try:
            if probability_result['setup_type'] == 0:
                return self._empty_risk()
            
            # Get ATR multipliers based on pair type
            atr_multipliers = self.config.get('ATR_MULTIPLIERS', {}).get(
                pair_classification,
                {'stop': 2.25, 'trail': 1.75, 'target': 7.0}
            )
            
            stop_multiplier = atr_multipliers['stop']
            trail_multiplier = atr_multipliers['trail']
            base_target_multiplier = atr_multipliers['target']
            
            # Calculate Daily ATR
            daily_atr = TechnicalIndicators.calculate_atr(daily_df, period=14)
            
            if daily_atr == 0:
                logger.warning(f"ATR is zero for {symbol}")
                return self._empty_risk()
            
            # Get entry parameters
            entry_price = probability_result['current_price']
            setup_type = probability_result['setup_type']
            
            # Calculate stop distance
            stop_distance = daily_atr * stop_multiplier
            
            # Calculate initial stop
            if setup_type == 1:  # Long
                initial_stop = entry_price - stop_distance
            else:  # Short
                initial_stop = entry_price + stop_distance
            
            # Calculate position size (1% risk)
            risk_amount = self.account_size * (self.risk_percent / 100.0)
            position_size = risk_amount / abs(stop_distance)
            
            # Adjust target multiplier based on momentum
            if combined_momentum >= 85:
                momentum_target_mult = base_target_multiplier * 1.2
            elif combined_momentum >= 75:
                momentum_target_mult = base_target_multiplier
            elif combined_momentum >= 65:
                momentum_target_mult = base_target_multiplier * 0.8
            else:
                momentum_target_mult = base_target_multiplier * 0.6
            
            # Calculate targets
            targets = self._calculate_targets(
                entry_price, stop_distance, momentum_target_mult, 
                daily_atr, setup_type, pair_classification
            )
            
            # Calculate trailing parameters
            trail_distance = daily_atr * trail_multiplier
            trail_start_price = targets['r3_target']  # Start trailing at +3R
            
            # Calculate R:R ratios
            r_ratios = {}
            for key, target_price in targets.items():
                if target_price > 0:
                    if setup_type == 1:
                        r_ratio = (target_price - entry_price) / stop_distance
                    else:
                        r_ratio = (entry_price - target_price) / stop_distance
                    r_ratios[key] = r_ratio
            
            # Expected hold duration (based on pair type and momentum)
            expected_duration = self._estimate_hold_duration(
                pair_classification, combined_momentum
            )
            
            return {
                'pair_type': pair_classification,
                'daily_atr': daily_atr,
                'entry_price': entry_price,
                'setup_type': setup_type,
                'setup_direction': 'LONG' if setup_type == 1 else 'SHORT',
                
                # Stop loss
                'stop_multiplier': stop_multiplier,
                'stop_distance': stop_distance,
                'initial_stop': initial_stop,
                
                # Position sizing
                'account_size': self.account_size,
                'risk_percent': self.risk_percent,
                'risk_amount': risk_amount,
                'position_size': position_size,
                
                # Targets
                'target_multiplier': momentum_target_mult,
                'targets': targets,
                'r_ratios': r_ratios,
                
                # Trailing
                'trail_multiplier': trail_multiplier,
                'trail_distance': trail_distance,
                'trail_start_at_r': self.start_trail_at,
                'trail_start_price': trail_start_price,
                'move_to_be_at_r': self.move_to_be_at,
                
                # Expectations
                'expected_duration_days': expected_duration,
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk parameters for {symbol}: {e}")
            return self._empty_risk()
    
    def _calculate_targets(self, entry_price: float, stop_distance: float, 
                          target_multiplier: float, daily_atr: float, 
                          setup_type: int, pair_type: str) -> Dict:
        """Calculate multiple target levels"""
        
        if setup_type == 1:  # Long
            # R-based targets
            r3_target = entry_price + (stop_distance * 3)  # Conservative +3R
            r5_target = entry_price + (stop_distance * 5)  # Expected +5R
            
            # ATR-based elite target
            elite_target = entry_price + (daily_atr * target_multiplier)
            
        else:  # Short
            r3_target = entry_price - (stop_distance * 3)
            r5_target = entry_price - (stop_distance * 5)
            elite_target = entry_price - (daily_atr * target_multiplier)
        
        # Expected hit probabilities (based on historical data)
        if pair_type == "TRENDING":
            r3_prob = 85  # 85% probability of hitting +3R
            r5_prob = 65
            elite_prob = 40
        elif pair_type == "RANGING":
            r3_prob = 80
            r5_prob = 50
            elite_prob = 25
        else:  # MIXED
            r3_prob = 82
            r5_prob = 58
            elite_prob = 32
        
        return {
            'r3_target': r3_target,
            'r3_probability': r3_prob,
            'r5_target': r5_target,
            'r5_probability': r5_prob,
            'elite_target': elite_target,
            'elite_probability': elite_prob,
        }
    
    def _estimate_hold_duration(self, pair_type: str, momentum: float) -> int:
        """
        Estimate expected hold duration in days
        
        Args:
            pair_type: TRENDING, RANGING, or MIXED
            momentum: Combined momentum score (0-100)
            
        Returns:
            Expected duration in days
        """
        base_duration = {
            'TRENDING': 12,  # 12 days average for trending
            'RANGING': 6,    # 6 days for ranging
            'MIXED': 9       # 9 days for mixed
        }
        
        duration = base_duration.get(pair_type, 9)
        
        # Adjust based on momentum
        if momentum >= 85:
            duration = int(duration * 1.2)  # Stronger moves take longer
        elif momentum < 70:
            duration = int(duration * 0.8)  # Weaker moves exit faster
        
        return duration
    
    def _empty_risk(self) -> Dict:
        """Return empty risk parameters"""
        return {
            'pair_type': 'UNKNOWN',
            'daily_atr': 0,
            'entry_price': 0,
            'setup_type': 0,
            'setup_direction': 'NONE',
            'stop_multiplier': 0,
            'stop_distance': 0,
            'initial_stop': 0,
            'account_size': self.account_size,
            'risk_percent': self.risk_percent,
            'risk_amount': 0,
            'position_size': 0,
            'target_multiplier': 0,
            'targets': {},
            'r_ratios': {},
            'trail_multiplier': 0,
            'trail_distance': 0,
            'trail_start_at_r': self.start_trail_at,
            'trail_start_price': 0,
            'move_to_be_at_r': self.move_to_be_at,
            'expected_duration_days': 0,
        }
