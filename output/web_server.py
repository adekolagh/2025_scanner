"""
Web Server for Dashboard
Serves the HTML dashboard at localhost
"""

import logging
import threading
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

logger = logging.getLogger(__name__)


class DashboardHandler(SimpleHTTPRequestHandler):
    """Custom handler for dashboard serving"""
    
    def __init__(self, *args, directory=None, **kwargs):
        self.directory = directory
        super().__init__(*args, directory=directory, **kwargs)
    
    def log_message(self, format, *args):
        """Suppress HTTP server logs (optional)"""
        # Comment this out if you want to see HTTP requests
        pass
    
    def end_headers(self):
        """Add headers to prevent caching"""
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Expires', '0')
        super().end_headers()


class DashboardServer:
    """Web server for dashboard"""
    
    def __init__(self, port=8000, output_dir='output'):
        """
        Initialize dashboard server
        
        Args:
            port: Port to serve on (default 8000)
            output_dir: Directory containing dashboard.html
        """
        self.port = port
        self.output_dir = Path(output_dir).resolve()
        self.server = None
        self.server_thread = None
        self.is_running = False
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Dashboard server initialized on port {port}")
    
    def start(self, open_browser=True):
        """
        Start the web server in background thread
        
        Args:
            open_browser: If True, automatically open browser
        """
        try:
            # Create placeholder dashboard if it doesn't exist
            dashboard_file = self.output_dir / "dashboard.html"
            if not dashboard_file.exists():
                placeholder_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="5">
    <title>Market Scanner - Starting...</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0e27;
            color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .loading {
            text-align: center;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .spinner {
            border: 4px solid rgba(255,255,255,0.3);
            border-top: 4px solid #ffffff;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        h1 { font-size: 2em; margin-bottom: 20px; }
        p { font-size: 1.2em; opacity: 0.9; }
    </style>
</head>
<body>
    <div class="loading">
        <h1>🔍 Market Scanner</h1>
        <div class="spinner"></div>
        <p>Running first scan...</p>
        <p>This page will refresh automatically.</p>
        <p><small>Usually takes 20-30 seconds</small></p>
    </div>
</body>
</html>
"""
                dashboard_file.write_text(placeholder_html, encoding='utf-8')
                logger.info("Created placeholder dashboard")
            
            # Change to output directory
            os.chdir(self.output_dir)
            
            # Create handler with directory
            handler = lambda *args, **kwargs: DashboardHandler(
                *args, 
                directory=str(self.output_dir),
                **kwargs
            )
            
            # Create server
            self.server = HTTPServer(('localhost', self.port), handler)
            
            # Start server in background thread
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            self.is_running = True
            
            dashboard_url = f"http://localhost:{self.port}/dashboard.html"
            
            logger.info("=" * 80)
            logger.info("🌐 DASHBOARD WEB SERVER STARTED")
            logger.info("=" * 80)
            logger.info(f"   URL: {dashboard_url}")
            logger.info(f"   Auto-refresh: Every 5 minutes")
            logger.info(f"   Scanner updates: Every 1 hour")
            logger.info("=" * 80)
            
            print("\n" + "=" * 80)
            print("🌐 DASHBOARD LIVE AT:")
            print(f"   👉 {dashboard_url}")
            print("=" * 80)
            print("   The dashboard will update automatically as scanner runs.")
            print("   Leave this page open in your browser!")
            print("=" * 80 + "\n")
            
            # Open browser automatically
            if open_browser:
                logger.info("Opening dashboard in browser...")
                threading.Timer(2.0, lambda: webbrowser.open(dashboard_url)).start()
            
            return dashboard_url
            
        except Exception as e:
            logger.error(f"Error starting web server: {e}")
            return None
    
    def stop(self):
        """Stop the web server"""
        if self.server and self.is_running:
            self.server.shutdown()
            self.is_running = False
            logger.info("Dashboard server stopped")
    
    def get_url(self):
        """Get dashboard URL"""
        if self.is_running:
            return f"http://localhost:{self.port}/dashboard.html"
        return None
