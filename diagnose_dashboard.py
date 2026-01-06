"""
Diagnostic: Check Console vs Dashboard Data Mismatch
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("CONSOLE vs DASHBOARD DATA DIAGNOSTIC")
print("=" * 80)

# Check if dashboard.html exists
dashboard_path = Path("output/dashboard.html")
if not dashboard_path.exists():
    print("\n❌ Dashboard file not found!")
    print(f"   Expected: {dashboard_path.absolute()}")
    sys.exit(1)

print(f"\n✅ Dashboard found: {dashboard_path.absolute()}")

# Read dashboard content
with open(dashboard_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("\n" + "=" * 80)
print("WHAT'S IN THE DASHBOARD HTML:")
print("=" * 80)

# Check for data
if "No setups found" in content or "no setups" in content.lower():
    print("\n⚠️ Dashboard shows: NO SETUPS")
else:
    print("\n✅ Dashboard has setup data")

# Check for specific symbols
symbols = ["XAUUSD", "EURUSD", "GBPUSD", "AUDUSD", "BTCUSD", 
           "XAUUSDm", "EURUSDm", "GBPUSDm", "AUDUSDm", "BTCUSDm"]
print("\n" + "=" * 80)
print("SYMBOLS IN DASHBOARD:")
print("=" * 80)
found_symbols = []
for symbol in symbols:
    if symbol in content:
        found_symbols.append(symbol)
        print(f"✅ {symbol}")

if not found_symbols:
    print("❌ NO SYMBOLS FOUND IN DASHBOARD!")

# Check timestamp
import re
timestamp_match = re.search(r'Last Updated: ([^<]+)', content)
if timestamp_match:
    print(f"\n⏰ Dashboard timestamp: {timestamp_match.group(1)}")
else:
    print("\n⚠️ No timestamp found in dashboard")

# Check for probability scores
prob_pattern = r'(\d+)%'
probabilities = re.findall(prob_pattern, content)
if probabilities:
    print(f"\n📊 Probability scores found: {len(probabilities)}")
    print(f"   Scores: {', '.join(probabilities[:10])}...")
else:
    print("\n❌ No probability scores found!")

# Check for common issues
print("\n" + "=" * 80)
print("COMMON ISSUES CHECK:")
print("=" * 80)

issues = []

if "No setups" in content:
    issues.append("❌ Dashboard shows 'No setups found'")
    
if not found_symbols:
    issues.append("❌ No symbol names in dashboard")
    
if not probabilities:
    issues.append("❌ No probability scores")

if "BIG BANG" not in content and "ALMOST READY" not in content and "GET READY" not in content:
    issues.append("❌ No alert sections rendered")

if issues:
    print("\n🚨 ISSUES DETECTED:")
    for issue in issues:
        print(f"   {issue}")
else:
    print("\n✅ Dashboard structure looks OK")

print("\n" + "=" * 80)
print("POSSIBLE CAUSES:")
print("=" * 80)
print("""
1. Dashboard generated BEFORE scan completed
2. Dashboard using old/cached data
3. HTML generator not receiving scan results
4. Browser showing cached version
5. Scan results not being passed to HTML generator

SOLUTIONS:
1. Check browser shows latest (Ctrl+F5 to force refresh)
2. Check dashboard file modification time
3. Re-run scanner and watch when dashboard generates
4. Check console shows same data being written to HTML
""")

# Check file modification time
import datetime
mod_time = datetime.datetime.fromtimestamp(dashboard_path.stat().st_mtime)
print(f"\n📅 Dashboard file last modified: {mod_time}")
print(f"   Current time: {datetime.datetime.now()}")
print(f"   Age: {datetime.datetime.now() - mod_time}")

print("\n" + "=" * 80)
