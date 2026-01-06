"""
Desktop Notifier
Sends desktop pop-up notifications
"""

import logging
from typing import Dict, List

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    logging.warning("plyer not installed - desktop notifications disabled")

logger = logging.getLogger(__name__)


class DesktopNotifier:
    """Send desktop notifications"""
    
    def __init__(self, config: Dict):
        """
        Initialize desktop notifier
        
        Args:
            config: Configuration dictionary
        """
        self.enabled = config.get('DESKTOP_ALERTS_ENABLED', False) and PLYER_AVAILABLE
        
        if not self.enabled:
            if not PLYER_AVAILABLE:
                logger.info("Desktop alerts disabled (plyer not available)")
            else:
                logger.info("Desktop alerts disabled in config")
        else:
            logger.info("Desktop notifier initialized")
    
    def send_notification(self, title: str, message: str, timeout: int = 10) -> bool:
        """
        Send desktop notification
        
        Args:
            title: Notification title
            message: Notification message
            timeout: Display duration in seconds
            
        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            notification.notify(
                title=title,
                message=message,
                app_name='Market Scanner',
                timeout=timeout
            )
            
            logger.info(f"Desktop notification sent: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending desktop notification: {e}")
            return False
    
    def send_alert(self, result: Dict, level: str) -> bool:
        """
        Send formatted desktop alert
        
        Args:
            result: Scan result dictionary
            level: Alert level
            
        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            symbol = result['symbol']
            prob = result['probability']['probability']
            direction = result['probability']['setup_direction']
            
            # Format based on level
            if level == 'big_bang':
                title = f"💥 BIG BANG: {symbol}"
                message = f"{direction} at {prob:.0f}%\nENTER NOW!"
                timeout = 30  # Longer for entry signals
            elif level == 'almost_ready':
                title = f"🟠 ALMOST READY: {symbol}"
                message = f"{direction} at {prob:.0f}%\nPrepare for entry"
                timeout = 20
            else:  # get_ready
                title = f"🟡 GET READY: {symbol}"
                message = f"{direction} at {prob:.0f}%\nSetup building"
                timeout = 15
            
            return self.send_notification(title, message, timeout)
            
        except Exception as e:
            logger.error(f"Error formatting desktop alert: {e}")
            return False
    
    def send_alerts_batch(self, alerts: Dict[str, List[Dict]]) -> bool:
        """
        Send batch of alerts
        
        Args:
            alerts: Dictionary of alerts by level
            
        Returns:
            bool: True if any sent successfully
        """
        if not self.enabled:
            return False
        
        sent_count = 0
        
        # Send Big Bang alerts first (most important)
        for result in alerts.get('big_bang', []):
            if self.send_alert(result, 'big_bang'):
                sent_count += 1
        
        # Send Almost Ready alerts
        for result in alerts.get('almost_ready', []):
            if self.send_alert(result, 'almost_ready'):
                sent_count += 1
        
        # Send Get Ready alerts
        for result in alerts.get('get_ready', []):
            if self.send_alert(result, 'get_ready'):
                sent_count += 1
        
        logger.info(f"Desktop: Sent {sent_count} notifications")
        return sent_count > 0
    
    def send_test_notification(self) -> bool:
        """
        Send test notification
        
        Returns:
            bool: True if successful
        """
        if not self.enabled:
            logger.warning("Desktop notifications disabled")
            return False
        
        return self.send_notification(
            title="🧪 Market Scanner Test",
            message="Desktop notifications are working!\n\nYou'll receive alerts when setups reach 60%, 70%, and 80%.",
            timeout=10
        )
