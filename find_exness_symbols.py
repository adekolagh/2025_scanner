"""
Find Actual Symbol Names on Your Exness Broker
Searches for Gold, EUR/USD, Oil, etc. and shows exact names
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import *
import MetaTrader5 as mt5

print("=" * 80)
print("FINDING YOUR EXNESS SYMBOL NAMES")
print("=" * 80)

# Initialize and login
mt5.initialize()
broker_config = MT5_CONFIG.get(MT5_BROKER)
mt5.login(
    login=broker_config['login'],
    password=broker_config['password'],
    server=broker_config['server']
)

print(f"\n✅ Connected to {MT5_BROKER}")
print(f"   Server: {broker_config['server']}")
print(f"   Account: {broker_config['login']}")

# Get all symbols
all_symbols = mt5.symbols_get()
symbol_names = [s.name for s in all_symbols]

print(f"\n✅ Found {len(symbol_names)} symbols on your broker")
print("\nSearching for common trading symbols...\n")

# Search patterns
searches = {
    "GOLD": ["XAU", "GOLD"],
    "SILVER": ["XAG", "SILVER"],
    "EUR/USD": ["EUR", "EURUSD"],
    "GBP/USD": ["GBP", "GBPUSD"],
    "USD/JPY": ["JPY", "USDJPY"],
    "AUD/USD": ["AUD", "AUDUSD"],
    "USD/CAD": ["CAD", "USDCAD"],
    "USD/CHF": ["CHF", "USDCHF"],
    "NZD/USD": ["NZD", "NZDUSD"],
    "EUR/GBP": ["EURGBP"],
    "OIL (WTI)": ["USOIL", "WTI", "CL"],
    "OIL (Brent)": ["BRENT", "UKOUSD"],
    "NATURAL GAS": ["NATGAS", "NG"],
    "S&P 500": ["US500", "SPX", "SP500"],
    "NASDAQ": ["NAS100", "NDX", "USTEC"],
    "DOW JONES": ["US30", "DJI", "DJ30"],
    "BITCOIN": ["BTC", "BITCOIN"],
}

found_symbols = {}

for name, patterns in searches.items():
    matches = []
    for pattern in patterns:
        for symbol in symbol_names:
            if pattern.upper() in symbol.upper() and symbol not in matches:
                matches.append(symbol)
    
    if matches:
        print(f"✅ {name}:")
        for match in matches[:3]:  # Show top 3 matches
            info = mt5.symbol_info(match)
            if info:
                print(f"   → {match} ({info.description})")
                found_symbols[name] = match
        print()
    else:
        print(f"❌ {name}: Not found")
        print()

# Generate config
print("\n" + "=" * 80)
print("UPDATED CONFIG FOR YOUR BROKER")
print("=" * 80)
print("\nCopy this to your config/config.py:\n")

print("# ══════════════════════════════════════════════════════════════")
print("# PAIRS TO MONITOR (Updated for Your Exness Broker)")
print("# ══════════════════════════════════════════════════════════════")
print()

if found_symbols:
    # Trending pairs
    print("TRENDING_PAIRS = [")
    trending = ["GOLD", "SILVER", "OIL (WTI)", "OIL (Brent)", "NATURAL GAS", 
                "S&P 500", "NASDAQ", "DOW JONES", "BITCOIN"]
    for t in trending:
        if t in found_symbols:
            print(f'    "{found_symbols[t]}",  # {t}')
    print("]")
    print()
    
    # Ranging pairs
    print("RANGING_PAIRS = [")
    ranging = ["EUR/USD", "EUR/GBP", "USD/CHF"]
    for r in ranging:
        if r in found_symbols:
            print(f'    "{found_symbols[r]}",  # {r}')
    print("]")
    print()
    
    # Mixed pairs
    print("MIXED_PAIRS = [")
    mixed = ["GBP/USD", "AUD/USD", "USD/CAD", "NZD/USD"]
    for m in mixed:
        if m in found_symbols:
            print(f'    "{found_symbols[m]}",  # {m}')
    print("]")
    print()
    
    # All pairs
    print("ALL_PAIRS = TRENDING_PAIRS + RANGING_PAIRS + MIXED_PAIRS")
    print()
    
    # Symbol map
    print("# Symbol mapping (if needed)")
    print("SYMBOL_MAP = {")
    for orig_name, exness_name in found_symbols.items():
        simple = orig_name.replace("/", "").replace(" ", "").replace("(", "").replace(")", "")
        if simple != exness_name:
            print(f'    "{simple}": "{exness_name}",')
    print("}")

else:
    print("⚠️ No symbols found. Your broker might use very different naming.")
    print("\n💡 Manual approach:")
    print("1. Open MT5")
    print("2. Right-click Market Watch → Show All")
    print("3. Scroll through and note the names you want to trade")
    print("4. Add them to config.py manually")

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)
print("\n1. Copy the config above")
print("2. Open: C:\\2025_scanner\\market_scanner\\config\\config.py")
print("3. Replace TRENDING_PAIRS, RANGING_PAIRS, MIXED_PAIRS sections")
print("4. Save the file")
print("5. Run: python main.py")
print("\n✅ Scanner will work with correct symbol names!")

mt5.shutdown()
