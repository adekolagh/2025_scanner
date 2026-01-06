"""
Market Scanner - Main Application
Livermore Swing Trading Setup Scanner

Usage:
    python main.py              # Run with auto-scan
    python main.py --manual     # Run manual scan only
    python main.py --test       # Test all systems
"""

import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import configuration
from config.config import *

# Import components
from scanner.scanner import Scanner
from scanner.alert_manager import AlertManager
from scanner.scheduler import ScanScheduler
from output.html_generator import HTMLGenerator
from output.web_server import DashboardServer
from alerts.email_notifier import EmailNotifier
from alerts.telegram_notifier import TelegramNotifier
from alerts.desktop_notifier import DesktopNotifier
from alerts.sound_player import SoundPlayer


# Setup logging
def setup_logging(config):
    """Configure logging with Windows UTF-8 support"""
    log_level = config.get('LOG_LEVEL', 'INFO')
    log_to_file = config.get('LOG_TO_FILE', True)
    log_file = config.get('LOG_FILE_PATH', 'logs/scanner.log')
    
    # Create logs directory
    if log_to_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Fix Windows console encoding for emojis
    if sys.platform == 'win32':
        try:
            # Try to set console to UTF-8
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            # If reconfigure fails, continue without it
            pass
    
    # Create handlers
    handlers = []
    
    # Console handler with UTF-8 support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)
    
    # File handler with UTF-8 encoding
    if log_to_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8', errors='replace')
        file_handler.setLevel(getattr(logging, log_level))
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        handlers=handlers,
        force=True
    )
    
    return logging.getLogger(__name__)


class MarketScanner:
    """Main Market Scanner Application"""
    
    def __init__(self, config_dict):
        """
        Initialize market scanner
        
        Args:
            config_dict: Configuration dictionary from config.py
        """
        self.config = config_dict
        self.logger = setup_logging(config_dict)
        
        self.logger.info("=" * 80)
        self.logger.info("MARKET SCANNER - Livermore Swing Trading System")
        self.logger.info("=" * 80)
        
        # Initialize components
        self.logger.info("Initializing components...")
        
        self.scanner = Scanner(config_dict)
        self.alert_manager = AlertManager(config_dict)
        self.html_generator = HTMLGenerator(config_dict)
        
        # Initialize web server
        self.web_server = DashboardServer(
            port=8000,
            output_dir='output'
        )
        
        # Initialize alert systems
        self.email_notifier = EmailNotifier(config_dict)
        self.telegram_notifier = TelegramNotifier(config_dict)
        self.desktop_notifier = DesktopNotifier(config_dict)
        self.sound_player = SoundPlayer(config_dict)
        
        self.logger.info("✅ All components initialized")
    
    def run_scan(self):
        """Execute a single scan cycle"""
        try:
            self.logger.info("\n" + "🔍 STARTING SCAN CYCLE " + "=" * 60)
            
            # Step 1: Scan all pairs
            scan_results = self.scanner.scan_all_pairs()
            
            if not scan_results:
                self.logger.warning("No valid scan results")
                return
            
            self.logger.info(f"✅ Scanned {len(scan_results)} pairs")
            
            # Step 2: Check for alerts
            alerts = self.alert_manager.check_alerts(scan_results)
            
            total_alerts = sum(len(alerts[key]) for key in alerts)
            if total_alerts > 0:
                self.logger.info(f"\n🚨 {total_alerts} NEW ALERT{'S' if total_alerts > 1 else ''}!")
                
                # Prepare alert messages
                alert_messages = {
                    'big_bang': [self.alert_manager.format_alert_message(r, 'big_bang') for r in alerts.get('big_bang', [])],
                    'almost_ready': [self.alert_manager.format_alert_message(r, 'almost_ready') for r in alerts.get('almost_ready', [])],
                    'get_ready': [self.alert_manager.format_alert_message(r, 'get_ready') for r in alerts.get('get_ready', [])]
                }
                
                # Send alerts through all channels
                self._send_alerts(alerts, alert_messages)
            else:
                self.logger.info("ℹ️ No new alerts")
            
            # Step 3: Generate HTML dashboard
            self.logger.info("\n📊 Generating HTML dashboard...")
            data_source = self.scanner.data_fetcher.get_source_info()
            dashboard_path = self.html_generator.generate_dashboard(scan_results, data_source)
            
            if dashboard_path:
                self.logger.info(f"✅ Dashboard: {dashboard_path}")
            
            # Step 4: Print summary
            self._print_summary(scan_results, alerts)
            
            self.logger.info("\n" + "✅ SCAN CYCLE COMPLETE " + "=" * 60 + "\n")
            
        except Exception as e:
            self.logger.error(f"Error in scan cycle: {e}", exc_info=True)
    
    def _send_alerts(self, alerts: dict, alert_messages: dict):
        """Send alerts through all configured channels"""
        
        # Email alerts
        if self.config.get('EMAIL_ENABLED'):
            self.logger.info("📧 Sending email alerts...")
            self.email_notifier.send_alerts_batch(alerts, alert_messages)
        
        # Telegram alerts
        if self.config.get('TELEGRAM_ENABLED'):
            self.logger.info("💬 Sending Telegram alerts...")
            self.telegram_notifier.send_alerts_batch(alerts)
        
        # Desktop notifications
        if self.config.get('DESKTOP_ALERTS_ENABLED'):
            self.logger.info("🔔 Sending desktop notifications...")
            self.desktop_notifier.send_alerts_batch(alerts)
        
        # Sound alerts
        if self.config.get('SOUND_ALERTS_ENABLED'):
            self.logger.info("🔊 Playing sound alert...")
            self.sound_player.play_alerts_batch(alerts)
    
    def _print_summary(self, scan_results: list, alerts: dict):
        """Print scan summary to console"""
        
        # Count setups by category
        big_bang = [r for r in scan_results if r['probability']['probability'] >= 80 and r['probability'].get('m15_confirmed')]
        almost_ready = [r for r in scan_results if 70 <= r['probability']['probability'] < 80]
        get_ready = [r for r in scan_results if 60 <= r['probability']['probability'] < 70]
        forming = [r for r in scan_results if 40 <= r['probability']['probability'] < 60]
        
        print("\n" + "=" * 80)
        print("SCAN SUMMARY")
        print("=" * 80)
        print(f"Total Pairs Analyzed: {len(scan_results)}")
        print(f"\n💥 BIG BANG (80%+ & Confirmed): {len(big_bang)}")
        if big_bang:
            for r in big_bang[:5]:  # Show top 5
                print(f"   • {r['symbol']}: {r['probability']['probability']:.0f}% {r['probability']['setup_direction']}")
        
        print(f"\n🟠 ALMOST READY (70-79%): {len(almost_ready)}")
        if almost_ready:
            for r in almost_ready[:5]:
                print(f"   • {r['symbol']}: {r['probability']['probability']:.0f}% {r['probability']['setup_direction']}")
        
        print(f"\n🟡 GET READY (60-69%): {len(get_ready)}")
        if get_ready:
            for r in get_ready[:5]:
                print(f"   • {r['symbol']}: {r['probability']['probability']:.0f}% {r['probability']['setup_direction']}")
        
        print(f"\n🔵 FORMING (40-59%): {len(forming)}")
        
        # Alert summary
        total_new_alerts = sum(len(alerts[key]) for key in alerts)
        if total_new_alerts > 0:
            print(f"\n🚨 NEW ALERTS: {total_new_alerts}")
            print(self.alert_manager.get_alert_summary(alerts))
        
        print("=" * 80 + "\n")
    
    def test_all_systems(self):
        """Test all systems"""
        self.logger.info("\n" + "🧪 TESTING ALL SYSTEMS " + "=" * 60)
        
        # Test data connection
        self.logger.info("\n1️⃣ Testing data connection...")
        data_info = self.scanner.data_fetcher.get_source_info()
        self.logger.info(f"   Primary source: {data_info.get('primary_source')}")
        self.logger.info(f"   MT5 connected: {data_info.get('mt5_connected')}")
        self.logger.info(f"   Yahoo fallback: {data_info.get('fallback_available')}")
        
        # Test email
        self.logger.info("\n2️⃣ Testing email...")
        if self.config.get('EMAIL_ENABLED'):
            self.email_notifier.send_test_email()
        else:
            self.logger.info("   Email disabled")
        
        # Test Telegram
        self.logger.info("\n3️⃣ Testing Telegram...")
        if self.config.get('TELEGRAM_ENABLED'):
            self.telegram_notifier.send_test_message()
        else:
            self.logger.info("   Telegram disabled")
        
        # Test desktop notifications
        self.logger.info("\n4️⃣ Testing desktop notifications...")
        if self.config.get('DESKTOP_ALERTS_ENABLED'):
            self.desktop_notifier.send_test_notification()
        else:
            self.logger.info("   Desktop notifications disabled")
        
        # Test sound
        self.logger.info("\n5️⃣ Testing sound alerts...")
        if self.config.get('SOUND_ALERTS_ENABLED'):
            self.sound_player.test_sounds()
        else:
            self.logger.info("   Sound alerts disabled")
        
        self.logger.info("\n✅ SYSTEM TEST COMPLETE " + "=" * 60 + "\n")
    
    def run_with_scheduler(self):
        """Run with automatic scheduling"""
        
        # Start web server
        self.web_server.start(open_browser=True)
        
        # Create scheduler
        scheduler = ScanScheduler(self.config, self.run_scan)
        
        try:
            # Start scheduler (runs first scan immediately)
            scheduler.start(run_immediate=True)
            
        except KeyboardInterrupt:
            self.logger.info("\n\n👋 Shutting down...")
        finally:
            self.cleanup()
    
    def run_manual(self):
        """Run single manual scan"""
        # Start web server
        self.web_server.start(open_browser=True)
        
        try:
            self.run_scan()
            
            # Keep server running so user can view dashboard
            print("\n" + "=" * 80)
            print("✅ Scan complete! Dashboard is live at:")
            print(f"   👉 {self.web_server.get_url()}")
            print("\nPress Ctrl+C to stop the server and exit.")
            print("=" * 80 + "\n")
            
            # Keep running until user stops
            import time
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\nStopping...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup and disconnect"""
        self.logger.info("Cleaning up...")
        self.scanner.disconnect()
        self.web_server.stop()
        self.logger.info("✅ Cleanup complete")


def main():
    """Main entry point"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Market Scanner - Livermore Swing Trading System')
    parser.add_argument('--manual', action='store_true', help='Run manual scan only (no auto-scheduling)')
    parser.add_argument('--test', action='store_true', help='Test all systems')
    args = parser.parse_args()
    
    # Create configuration dictionary from config.py
    config_dict = {
        # MT5 Settings
        'MT5_ENABLED': MT5_ENABLED,
        'MT5_BROKER': MT5_BROKER,
        'MT5_CONFIG': MT5_CONFIG,
        'YAHOO_FINANCE_ENABLED': YAHOO_FINANCE_ENABLED,
        
        # Pairs
        'ALL_PAIRS': ALL_PAIRS,
        'TRENDING_PAIRS': TRENDING_PAIRS,
        'RANGING_PAIRS': RANGING_PAIRS,
        'MIXED_PAIRS': MIXED_PAIRS,
        'SYMBOL_MAP': SYMBOL_MAP,
        
        # Scanning
        'LOOKBACK_BARS': LOOKBACK_BARS,
        'SCAN_INTERVAL_MINUTES': SCAN_INTERVAL_MINUTES,
        'AUTO_SCAN_ENABLED': AUTO_SCAN_ENABLED and not args.manual,
        
        # Risk Management
        'ACCOUNT_SIZE': ACCOUNT_SIZE,
        'RISK_PER_TRADE': RISK_PER_TRADE,
        'ATR_MULTIPLIERS': ATR_MULTIPLIERS,
        'MOVE_TO_BE_AT_R': MOVE_TO_BE_AT_R,
        'START_TRAIL_AT_R': START_TRAIL_AT_R,
        
        # Probability
        'PROB_GET_READY': PROB_GET_READY,
        'PROB_ALMOST_READY': PROB_ALMOST_READY,
        'PROB_BIG_BANG': PROB_BIG_BANG,
        'MIN_TIME_AT_LEVEL': MIN_TIME_AT_LEVEL,
        'MIN_HTF_MOMENTUM': MIN_HTF_MOMENTUM,
        
        # Classification
        'CLASSIFICATION_METHOD': CLASSIFICATION_METHOD,
        'AUTO_CLASSIFICATION_THRESHOLDS': AUTO_CLASSIFICATION_THRESHOLDS,
        
        # Alerts
        'EMAIL_ENABLED': EMAIL_ENABLED,
        'EMAIL_CONFIG': EMAIL_CONFIG,
        'TELEGRAM_ENABLED': TELEGRAM_ENABLED,
        'TELEGRAM_CONFIG': TELEGRAM_CONFIG,
        'DESKTOP_ALERTS_ENABLED': DESKTOP_ALERTS_ENABLED,
        'SOUND_ALERTS_ENABLED': SOUND_ALERTS_ENABLED,
        'SOUND_CONFIG': SOUND_CONFIG,
        'ALERT_COOLDOWN_MINUTES': ALERT_COOLDOWN_MINUTES,
        
        # Output
        'HTML_OUTPUT_PATH': HTML_OUTPUT_PATH,
        'HTML_AUTO_REFRESH': HTML_AUTO_REFRESH,
        'HTML_REFRESH_SECONDS': HTML_REFRESH_SECONDS,
        
        # Technical
        'MURREY_FRAME': MURREY_FRAME,
        'MURREY_MULTIPLIER': MURREY_MULTIPLIER,
        'MURREY_IGNORE_WICKS': MURREY_IGNORE_WICKS,
        'VOLUME_SPIKE_THRESHOLD': VOLUME_SPIKE_THRESHOLD,
        'SPRING_MAX_BARS': 3,
        
        # Logging
        'LOG_LEVEL': LOG_LEVEL,
        'LOG_TO_FILE': LOG_TO_FILE,
        'LOG_FILE_PATH': LOG_FILE_PATH,
    }
    
    # Initialize scanner
    app = MarketScanner(config_dict)
    
    # Run based on mode
    if args.test:
        app.test_all_systems()
    elif args.manual:
        print("\n🔍 Running MANUAL scan...")
        app.run_manual()
    else:
        print("\n🔄 Running with AUTO-SCHEDULER...")
        print(f"   Scan interval: {SCAN_INTERVAL_MINUTES} minutes")
        print(f"   Dashboard: http://localhost:8000/dashboard.html")
        print(f"   Press Ctrl+C to stop\n")
        app.run_with_scheduler()


if __name__ == "__main__":
    main()
