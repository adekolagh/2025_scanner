"""
Entry Timer
Estimates when a setup will reach entry threshold (80%+)
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EntryTimer:
    """Estimate time until entry signal"""
    
    # Status levels
    STATUS_NONE = "NONE"
    STATUS_SPOTTED = "SPOTTED"
    STATUS_FORMING = "FORMING"
    STATUS_GET_READY = "GET_READY"
    STATUS_BUILDING = "BUILDING"
    STATUS_ALMOST_READY = "ALMOST_READY"
    STATUS_BIG_BANG = "BIG_BANG"
    
    def __init__(self, config: Dict):
        """
        Initialize entry timer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.prob_get_ready = config.get('PROB_GET_READY', 60)
        self.prob_almost_ready = config.get('PROB_ALMOST_READY', 70)
        self.prob_big_bang = config.get('PROB_BIG_BANG', 80)
    
    def get_status(self, probability: float, m15_confirmed: bool = False) -> Dict:
        """
        Get current setup status
        
        Args:
            probability: Current probability score (0-100)
            m15_confirmed: Whether 15M confirms entry
            
        Returns:
            Dictionary with status info
        """
        if probability >= self.prob_big_bang and m15_confirmed:
            status = self.STATUS_BIG_BANG
            emoji = "💥"
            color = "green"
            message = "ENTER NOW!"
        elif probability >= self.prob_big_bang:
            status = self.STATUS_ALMOST_READY
            emoji = "🟠"
            color = "orange"
            message = "Almost ready - waiting for 15M confirmation"
        elif probability >= self.prob_almost_ready:
            status = self.STATUS_ALMOST_READY
            emoji = "🟠"
            color = "orange"
            message = "ALMOST READY - Prepare"
        elif probability >= self.prob_get_ready and probability < 65:
            status = self.STATUS_GET_READY
            emoji = "🟡"
            color = "yellow"
            message = "GET READY - Building"
        elif probability >= 65:
            status = self.STATUS_BUILDING
            emoji = "🟡"
            color = "yellow"
            message = "BUILDING - Getting stronger"
        elif probability >= 40:
            status = self.STATUS_FORMING
            emoji = "🔵"
            color = "blue"
            message = "FORMING - Early stage"
        elif probability >= 20:
            status = self.STATUS_SPOTTED
            emoji = "🔵"
            color = "lightblue"
            message = "SPOTTED - Just entered zone"
        else:
            status = self.STATUS_NONE
            emoji = "⚪"
            color = "gray"
            message = "No setup"
        
        return {
            'status': status,
            'emoji': emoji,
            'color': color,
            'message': message,
            'probability': probability
        }
    
    def estimate_time_to_entry(self, current_probability: float, time_at_level: int, 
                               historical_avg_time: Optional[int] = None) -> Dict:
        """
        Estimate time until 80%+ entry signal
        
        Args:
            current_probability: Current probability score
            time_at_level: Bars already spent at level
            historical_avg_time: Historical average time to entry (optional)
            
        Returns:
            Dictionary with time estimates
        """
        try:
            if current_probability >= self.prob_big_bang:
                return {
                    'eta_bars': 0,
                    'eta_hours': 0,
                    'eta_message': "Ready NOW!",
                    'estimated_entry_time': datetime.now()
                }
            
            # Use historical average if available
            if historical_avg_time and historical_avg_time > 0:
                avg_time = historical_avg_time
            else:
                # Default: based on typical progression
                # 40% -> 80% typically takes 12-16 bars (12-16 hours on 1H chart)
                avg_time = 14
            
            # Calculate progression rate
            # Assume linear progression from current to 80%
            points_needed = self.prob_big_bang - current_probability
            
            if current_probability >= 70:
                # Close to entry - fast progression (1-2 hours)
                eta_bars = max(1, int(points_needed / 8))
            elif current_probability >= 60:
                # Building phase (2-6 hours)
                eta_bars = max(2, int(points_needed / 5))
            elif current_probability >= 50:
                # Early phase (6-12 hours)
                eta_bars = max(6, int(points_needed / 3))
            else:
                # Very early (12-24 hours)
                eta_bars = max(12, int(points_needed / 2))
            
            # Adjust based on time already spent
            if time_at_level >= 10:
                # Already accumulating - faster progression
                eta_bars = int(eta_bars * 0.7)
            
            # Convert to hours (assuming 1H timeframe)
            eta_hours = eta_bars
            
            # Estimate entry time
            estimated_time = datetime.now() + timedelta(hours=eta_hours)
            
            # Format message
            if eta_hours < 2:
                eta_message = f"Very soon (~{eta_hours}h)"
            elif eta_hours < 6:
                eta_message = f"Within {eta_hours} hours"
            elif eta_hours < 24:
                eta_message = f"Within {eta_hours} hours ({eta_hours//24} day)"
            else:
                days = eta_hours // 24
                eta_message = f"~{days} day{'s' if days > 1 else ''}"
            
            return {
                'eta_bars': eta_bars,
                'eta_hours': eta_hours,
                'eta_message': eta_message,
                'estimated_entry_time': estimated_time,
                'time_already_spent': time_at_level
            }
            
        except Exception as e:
            logger.error(f"Error estimating entry time: {e}")
            return {
                'eta_bars': 0,
                'eta_hours': 0,
                'eta_message': "Unknown",
                'estimated_entry_time': None,
                'time_already_spent': 0
            }
    
    def get_progression_stage(self, probability: float) -> str:
        """
        Get which stage of progression the setup is in
        
        Returns:
            Stage description
        """
        if probability >= self.prob_big_bang:
            return "Stage 5/5: Entry Signal (80%+)"
        elif probability >= self.prob_almost_ready:
            return "Stage 4/5: Almost Ready (70-79%)"
        elif probability >= self.prob_get_ready:
            return "Stage 3/5: Get Ready (60-69%)"
        elif probability >= 50:
            return "Stage 2/5: Forming (50-59%)"
        elif probability >= 40:
            return "Stage 1/5: Spotted (40-49%)"
        else:
            return "Stage 0/5: Too Early (<40%)"
