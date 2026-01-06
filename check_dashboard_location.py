"""
Quick Check - Where is dashboard.html?
"""

import os
from pathlib import Path

print("=" * 80)
print("DASHBOARD FILE LOCATION CHECK")
print("=" * 80)

# Check current directory
print(f"\nCurrent directory: {os.getcwd()}")

# Check if output folder exists
output_dir = Path("output")
if output_dir.exists():
    print(f"\n✅ Output directory exists: {output_dir.absolute()}")
    
    # List files in output
    files = list(output_dir.glob("*"))
    if files:
        print(f"\nFiles in output directory ({len(files)} files):")
        for f in files:
            print(f"   - {f.name}")
            if f.name == "dashboard.html":
                print(f"     ✅ FOUND dashboard.html!")
                print(f"     Size: {f.stat().st_size} bytes")
                import datetime
                mod_time = datetime.datetime.fromtimestamp(f.stat().st_mtime)
                print(f"     Modified: {mod_time}")
    else:
        print("\n❌ Output directory is EMPTY!")
else:
    print(f"\n❌ Output directory does NOT exist!")
    print(f"   Expected: {output_dir.absolute()}")

# Check if dashboard.html exists specifically
dashboard_path = Path("output/dashboard.html")
if dashboard_path.exists():
    print(f"\n✅ Dashboard file exists!")
    print(f"   Path: {dashboard_path.absolute()}")
else:
    print(f"\n❌ Dashboard file NOT FOUND!")
    print(f"   Expected: {dashboard_path.absolute()}")
    print("\n   SOLUTION: Run a scan first!")
    print("   Command: python main.py --manual")

print("\n" + "=" * 80)
print("WEB SERVER CHECK")
print("=" * 80)

# Check what directory web server uses
try:
    from config.config import *
    from output.web_server import DashboardServer
    
    server = DashboardServer(port=8000, output_dir='output')
    print(f"\nWeb server configured to serve from:")
    print(f"   {server.output_dir}")
    print(f"   Looking for: {server.output_dir}/dashboard.html")
    
    if (server.output_dir / "dashboard.html").exists():
        print("   ✅ File exists at this location!")
    else:
        print("   ❌ File NOT at this location!")
        
except Exception as e:
    print(f"\n⚠️ Could not check web server config: {e}")

print("\n" + "=" * 80)
print("SOLUTION")
print("=" * 80)
print("""
If dashboard.html is missing:

1. Run a scan first:
   python main.py --manual

2. Wait for scan to complete

3. Check output/dashboard.html exists

4. Then open: http://localhost:8000/dashboard.html

OR just run:
   python main.py
   
   (Web server starts automatically AND runs first scan)
""")
