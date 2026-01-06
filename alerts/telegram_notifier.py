"""
Telegram Bot Notifier
Sends alerts via Telegram
"""

import logging
import requests
from typing import Dict, List

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send Telegram alerts"""
    
    def __init__(self, config: Dict):
        """
        Initialize Telegram notifier
        
        Args:
            config: Configuration dictionary with Telegram settings
        """
        self.enabled = config.get('TELEGRAM_ENABLED', False)
        
        if not self.enabled:
            logger.info("Telegram alerts disabled")
            return
        
        telegram_config = config.get('TELEGRAM_CONFIG', {})
        self.bot_token = telegram_config.get('bot_token', '')
        self.chat_id = telegram_config.get('chat_id', '')
        
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram bot_token or chat_id not configured")
            self.enabled = False
            return
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        logger.info(f"Telegram notifier initialized (Chat ID: {self.chat_id})")
    
    def send_message(self, message: str) -> bool:
        """
        Send Telegram message
        
        Args:
            message: Message text
            
        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            url = f"{self.api_url}/sendMessage"
            
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                logger.info("Telegram message sent successfully")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def send_alert(self, result: Dict, level: str) -> bool:
        """
        Send formatted alert for a setup
        
        Args:
            result: Scan result dictionary
            level: Alert level ('get_ready', 'almost_ready', 'big_bang')
            
        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            symbol = result['symbol']
            prob = result['probability']['probability']
            direction = result['probability']['setup_direction']
            entry = result['current_price']
            stop = result['risk']['initial_stop']
            target = result['risk']['targets'].get('r3_target', 0)
            
            # Format based on level
            if level == 'big_bang':
                header = "💥 <b>BIG BANG ENTRY SIGNAL!</b>"
                action = "🚀 ENTER NOW!"
            elif level == 'almost_ready':
                header = "🟠 <b>ALMOST READY</b>"
                action = "⏰ Prepare for entry"
            else:  # get_ready
                header = "🟡 <b>GET READY</b>"
                action = "👀 Setup building"
            
            message = f"""{header}

📊 <b>Pair:</b> {symbol}
📈 <b>Direction:</b> {direction}
🎯 <b>Probability:</b> {prob:.0f}%

{action}

<b>Trade Setup:</b>
Entry: {entry:.5f}
Stop: {stop:.5f}
Target: {target:.5f}

<b>Risk:</b> ${result['risk']['risk_amount']:.2f}
<b>Position:</b> {result['risk']['position_size']:.2f} lots

<b>Momentum:</b> {result['combined_momentum']:.0f}%
<b>HTF Aligned:</b> {'✅' if result['htf_aligned'] else '⚠️'}
<b>15M Confirmed:</b> {'✅' if result['probability'].get('m15_confirmed') else '⏳'}

⏱ Time at Level: {result['probability']['time_at_level']} bars
📅 ETA: {result['timing']['eta_message']}
"""
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error formatting Telegram alert: {e}")
            return False
    
    def send_alerts_batch(self, alerts: Dict[str, List[Dict]]) -> bool:
        """
        Send batch of alerts
        
        Args:
            alerts: Dictionary of alerts by level
            
        Returns:
            bool: True if all sent successfully
        """
        if not self.enabled:
            return False
        
        success_count = 0
        total_count = 0
        
        # Send Big Bang alerts (most important)
        for result in alerts.get('big_bang', []):
            if self.send_alert(result, 'big_bang'):
                success_count += 1
            total_count += 1
        
        # Send Almost Ready alerts
        for result in alerts.get('almost_ready', []):
            if self.send_alert(result, 'almost_ready'):
                success_count += 1
            total_count += 1
        
        # Send Get Ready alerts
        for result in alerts.get('get_ready', []):
            if self.send_alert(result, 'get_ready'):
                success_count += 1
            total_count += 1
        
        logger.info(f"Telegram: Sent {success_count}/{total_count} alerts")
        return success_count == total_count
    
    def send_summary(self, summary_text: str) -> bool:
        """
        Send summary message
        
        Args:
            summary_text: Summary text
            
        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            return False
        
        message = f"<b>📊 Market Scanner Update</b>\n\n{summary_text}"
        return self.send_message(message)
    
    def send_test_message(self) -> bool:
        """
        Send test message to verify configuration
        
        Returns:
            bool: True if successful
        """
        if not self.enabled:
            logger.warning("Telegram is disabled")
            return False
        
        message = """<b>🧪 Market Scanner Test</b>

This is a test message from your Market Scanner bot.

If you received this, your Telegram configuration is working correctly! ✅

You will receive alerts when setups reach:
• 60%: 🟡 GET READY
• 70%: 🟠 ALMOST READY  
• 80%: 💥 BIG BANG (Enter now!)

Happy Trading! 🚀
"""
        
        return self.send_message(message)
    
    def get_chat_id(self) -> str:
        """
        Helper method to get chat ID
        Call this after sending /start to your bot
        
        Returns:
            Instructions for getting chat ID
        """
        return f"""
To get your Telegram Chat ID:

1. Send /start to your bot: @YourBotName
2. Visit this URL in your browser:
   {self.api_url}/getUpdates

3. Look for "chat":{"id": YOUR_CHAT_ID}
4. Copy the chat ID and add it to config.py

Current bot token: {self.bot_token[:10]}...
"""
