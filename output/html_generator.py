"""
HTML Dashboard Generator
Creates beautiful HTML dashboard from scan results
"""

import logging
from typing import Dict, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class HTMLGenerator:
    """Generate HTML dashboard"""
    
    def __init__(self, config: Dict):
        """
        Initialize HTML generator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.output_path = config.get('HTML_OUTPUT_PATH', 'output/dashboard.html')
        self.auto_refresh = config.get('HTML_AUTO_REFRESH', True)
        self.refresh_seconds = config.get('HTML_REFRESH_SECONDS', 300)
    
    def generate_dashboard(self, scan_results: List[Dict], data_source_info: Dict) -> str:
        """
        Generate complete HTML dashboard
        
        Args:
            scan_results: List of scan results
            data_source_info: Information about data sources
            
        Returns:
            Path to generated HTML file
        """
        try:
            logger.info(f"Generating dashboard with {len(scan_results)} scan results")
            
            # Sort results by probability
            sorted_results = sorted(scan_results, key=lambda x: x['probability']['probability'], reverse=True)
            
            # Categorize setups (MATCH CONSOLE OUTPUT - show all, mark confirmation status)
            big_bang = [r for r in sorted_results if r['probability']['probability'] >= 80]  # Removed m15_confirmed requirement
            almost_ready = [r for r in sorted_results if 70 <= r['probability']['probability'] < 80]
            get_ready = [r for r in sorted_results if 60 <= r['probability']['probability'] < 70]
            forming = [r for r in sorted_results if 40 <= r['probability']['probability'] < 60]
            
            logger.info(f"Categories: BIG BANG={len(big_bang)}, ALMOST={len(almost_ready)}, GET READY={len(get_ready)}, FORMING={len(forming)}")
            
            # Generate HTML
            html = self._generate_html(big_bang, almost_ready, get_ready, forming, data_source_info)
            logger.info(f"Generated HTML length: {len(html):,} characters")
            
            # Write to file
            output_file = Path(self.output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write HTML content
            logger.info(f"Writing dashboard to: {output_file.absolute()}")
            output_file.write_text(html, encoding='utf-8')
            
            # Verify file was written
            if output_file.exists():
                file_size = output_file.stat().st_size
                logger.info(f"✅ Dashboard generated: {output_file} ({file_size:,} bytes)")
            else:
                logger.error(f"❌ Failed to write dashboard file!")
                return None
            
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error generating dashboard: {e}")
            return None
    
    def _generate_html(self, big_bang: List, almost_ready: List, get_ready: List, forming: List, data_source: Dict) -> str:
        """Generate complete HTML content"""
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        refresh_meta = f'<meta http-equiv="refresh" content="{self.refresh_seconds}">' if self.auto_refresh else ''
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Market Scanner - Livermore Swing Setups</title>
    {refresh_meta}
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0e27;
            color: #ffffff;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header-info {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 15px;
            flex-wrap: wrap;
        }}
        
        .data-source {{
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 0.9em;
        }}
        
        .section {{
            background: #1a1f3a;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }}
        
        .section-header {{
            font-size: 1.8em;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section-header.big-bang {{
            color: #00ff00;
        }}
        
        .section-header.almost-ready {{
            color: #ffaa00;
        }}
        
        .section-header.get-ready {{
            color: #ffff00;
        }}
        
        .section-header.forming {{
            color: #00ccff;
        }}
        
        .pair-card {{
            background: #252b4a;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 5px solid;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .pair-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }}
        
        .pair-card.big-bang {{
            border-color: #00ff00;
            background: linear-gradient(90deg, #252b4a 0%, #1a3a1a 100%);
        }}
        
        .pair-card.almost-ready {{
            border-color: #ffaa00;
        }}
        
        .pair-card.get-ready {{
            border-color: #ffff00;
        }}
        
        .pair-card.forming {{
            border-color: #00ccff;
        }}
        
        .pair-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }}
        
        .pair-name {{
            font-size: 1.5em;
            font-weight: bold;
        }}
        
        .pair-probability {{
            font-size: 2em;
            font-weight: bold;
        }}
        
        .pair-status {{
            font-size: 1.2em;
            padding: 5px 15px;
            border-radius: 20px;
            background: rgba(255,255,255,0.1);
        }}
        
        .pair-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .detail-item {{
            background: rgba(0,0,0,0.2);
            padding: 12px;
            border-radius: 8px;
        }}
        
        .detail-label {{
            font-size: 0.85em;
            color: #aaaaaa;
            margin-bottom: 5px;
        }}
        
        .detail-value {{
            font-size: 1.1em;
            font-weight: bold;
        }}
        
        .detail-value.bullish {{
            color: #00ff00;
        }}
        
        .detail-value.bearish {{
            color: #ff3333;
        }}
        
        .no-setups {{
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 1.2em;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .pair-details {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 MARKET SCANNER - Livermore Swing Setups</h1>
            <div class="header-info">
                <div>Last Scan: <strong>{current_time}</strong></div>
                <div class="data-source">
                    📊 Data Source: <strong>{data_source.get('primary_source', 'Unknown')}</strong>
                </div>
                <div>Auto-refresh: <strong>{'✅ ON' if self.auto_refresh else '❌ OFF'}</strong></div>
            </div>
        </div>
        
        {self._generate_section(big_bang, "💥 BIG BANG - ENTER NOW!", "big-bang")}
        {self._generate_section(almost_ready, "🟠 ALMOST READY - Prepare", "almost-ready")}
        {self._generate_section(get_ready, "🟡 GET READY - Building", "get-ready")}
        {self._generate_section(forming, "🔵 FORMING - Early Stage", "forming")}
        
        <div class="footer">
            <p>Livermore Market Scanner | Generated: {current_time}</p>
            <p>Total Setups: {len(big_bang + almost_ready + get_ready + forming)}</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_section(self, results: List[Dict], title: str, css_class: str) -> str:
        """Generate section HTML"""
        
        if not results:
            return f"""
        <div class="section">
            <div class="section-header {css_class}">{title}</div>
            <div class="no-setups">No setups in this category</div>
        </div>
"""
        
        cards_html = ""
        for result in results:
            cards_html += self._generate_pair_card(result, css_class)
        
        return f"""
        <div class="section">
            <div class="section-header {css_class}">{title}</div>
            {cards_html}
        </div>
"""
    
    def _generate_pair_card(self, result: Dict, css_class: str) -> str:
        """Generate individual pair card"""
        
        symbol = result['symbol']
        prob = result['probability']['probability']
        direction = result['probability']['setup_direction']
        classification = result['classification']
        
        entry = result['current_price']
        stop = result['risk']['initial_stop']
        target = result['risk']['targets'].get('r3_target', 0)
        
        htf_momentum = result['combined_momentum']
        htf_aligned = '✅' if result['htf_aligned'] else '⚠️'
        m15_confirmed = '✅' if result['probability'].get('m15_confirmed') else '⏳'
        
        time_at_level = result['probability']['time_at_level']
        eta = result['timing']['eta_message']
        
        direction_color = 'bullish' if direction == 'LONG' else 'bearish'
        
        return f"""
            <div class="pair-card {css_class}">
                <div class="pair-header">
                    <div class="pair-name">{symbol}</div>
                    <div class="pair-probability">{prob:.0f}%</div>
                    <div class="pair-status">{result['status']['emoji']} {result['status']['message']}</div>
                </div>
                
                <div class="pair-details">
                    <div class="detail-item">
                        <div class="detail-label">Direction</div>
                        <div class="detail-value {direction_color}">{direction}</div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="detail-label">Entry</div>
                        <div class="detail-value">{entry:.5f}</div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="detail-label">Stop Loss</div>
                        <div class="detail-value">{stop:.5f}</div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="detail-label">Target (+3R)</div>
                        <div class="detail-value">{target:.5f}</div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="detail-label">Pair Type</div>
                        <div class="detail-value">{classification}</div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="detail-label">HTF Momentum</div>
                        <div class="detail-value">{htf_momentum:.0f}%</div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="detail-label">HTF Aligned</div>
                        <div class="detail-value">{htf_aligned}</div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="detail-label">15M Confirmed</div>
                        <div class="detail-value">{m15_confirmed}</div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="detail-label">Time at Level</div>
                        <div class="detail-value">{time_at_level} bars</div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="detail-label">ETA to Entry</div>
                        <div class="detail-value">{eta}</div>
                    </div>
                </div>
            </div>
"""
