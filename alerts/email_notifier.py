"""
Email Notifier
Sends email alerts via SMTP
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Send email alerts"""
    
    def __init__(self, config: Dict):
        """
        Initialize email notifier
        
        Args:
            config: Configuration dictionary with email settings
        """
        self.enabled = config.get('EMAIL_ENABLED', False)
        
        if not self.enabled:
            logger.info("Email alerts disabled")
            return
        
        email_config = config.get('EMAIL_CONFIG', {})
        self.smtp_server = email_config.get('smtp_server', '')
        self.smtp_port = email_config.get('smtp_port', 465)
        self.sender_email = email_config.get('sender_email', '')
        self.sender_password = email_config.get('sender_password', '')
        self.recipient_email = email_config.get('recipient_email', '')
        self.use_ssl = email_config.get('use_ssl', True)
        
        logger.info(f"Email notifier initialized: {self.sender_email} -> {self.recipient_email}")
    
    def send_alert(self, subject: str, message: str) -> bool:
        """
        Send email alert
        
        Args:
            subject: Email subject
            message: Email body (plain text)
            
        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(message, 'plain'))
            
            # Send email
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def send_alerts_batch(self, alerts: Dict[str, List[Dict]], alert_messages: Dict[str, List[str]]) -> bool:
        """
        Send batch of alerts in one email
        
        Args:
            alerts: Dictionary of alerts by level
            alert_messages: Dictionary of formatted messages by level
            
        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            total_alerts = sum(len(alerts[key]) for key in alerts)
            
            if total_alerts == 0:
                return False
            
            # Create subject
            subject = f"🚨 Market Scanner: {total_alerts} Alert{'s' if total_alerts > 1 else ''}"
            
            # Create body
            body = "LIVERMORE MARKET SCANNER ALERTS\n"
            body += "=" * 50 + "\n\n"
            
            # Big Bang alerts
            if alerts.get('big_bang'):
                body += "💥 BIG BANG - ENTER NOW!\n"
                body += "-" * 50 + "\n"
                for msg in alert_messages.get('big_bang', []):
                    body += msg + "\n\n"
            
            # Almost Ready alerts
            if alerts.get('almost_ready'):
                body += "🟠 ALMOST READY - Prepare\n"
                body += "-" * 50 + "\n"
                for msg in alert_messages.get('almost_ready', []):
                    body += msg + "\n\n"
            
            # Get Ready alerts
            if alerts.get('get_ready'):
                body += "🟡 GET READY - Building\n"
                body += "-" * 50 + "\n"
                for msg in alert_messages.get('get_ready', []):
                    body += msg + "\n\n"
            
            body += "=" * 50 + "\n"
            body += "This is an automated alert from your Market Scanner.\n"
            body += "Review the dashboard for complete details.\n"
            
            return self.send_alert(subject, body)
            
        except Exception as e:
            logger.error(f"Error sending batch email: {e}")
            return False
    
    def send_test_email(self) -> bool:
        """
        Send test email to verify configuration
        
        Returns:
            bool: True if successful
        """
        if not self.enabled:
            logger.warning("Email is disabled")
            return False
        
        subject = "🧪 Market Scanner Test Email"
        message = """
This is a test email from your Market Scanner.

If you received this, your email configuration is working correctly!

Configuration:
- SMTP Server: {}
- Port: {}
- Sender: {}
- Recipient: {}

You will receive alerts when setups reach:
- 60%: GET READY
- 70%: ALMOST READY  
- 80%: BIG BANG (Enter now!)

Happy Trading! 🚀
""".format(self.smtp_server, self.smtp_port, self.sender_email, self.recipient_email)
        
        return self.send_alert(subject, message)
