"""
Find Correct Trading Symbols - All Brokers
Shows exact matches for Gold, EUR/USD, etc.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import *
import MetaTrader5 as mt5

print("=" * 80)
print("FINDING CORRECT SYMBOL NAMES")
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

# Get all symbols
all_symbols = mt5.symbols_get()
symbol_list = [(s.name, s.description) for s in all_symbols]

print(f"\n✅ Found {len(symbol_list)} symbols")
print("\n" + "=" * 80)
print("SEARCHING FOR EXACT MATCHES")
print("=" * 80)

# Define what we're looking for with exact patterns
targets = {
    "Gold (XAU/USD)": ["XAUUSDm", "XAUUSD", "XAU/USD", "GOLD"],
    "Silver (XAG/USD)": ["XAGUSDm", "XAGUSD", "XAG/USD", "SILVER"],
    "EUR/USD": ["EURUSDm", "EURUSD", "EUR/USD"],
    "GBP/USD": ["GBPUSDm", "GBPUSD", "GBP/USD"],
    "USD/JPY": ["USDJPYm", "USDJPY", "USD/JPY"],
    "AUD/USD": ["AUDUSDm", "AUDUSD", "AUD/USD"],
    "USD/CAD": ["USDCADm", "USDCAD", "USD/CAD"],
    "USD/CHF": ["USDCHFm", "USDCHF", "USD/CHF"],
    "NZD/USD": ["NZDUSDm", "NZDUSD", "NZD/USD"],
    "EUR/GBP": ["EURGBPm", "EURGBP", "EUR/GBP"],
    "Oil (WTI)": ["USOILm", "USOIL", "WTI", "CLm", "CL-"],
    "Oil (Brent)": ["UKOUSDm", "UKOUSD", "BRENT"],
    "Natural Gas": ["XNGUSDm", "XNGUSD", "NGm", "NATGAS"],
    "S&P 500": ["US500m", "US500", "SPX500", "SP500"],
    "NASDAQ": ["USTECm", "USTEC", "NAS100", "NDX"],
    "Dow Jones": ["US30m", "US30", "DJ30", "DJI"],
    "Bitcoin": ["BTCUSDm", "BTCUSD", "BTC/USD"],
}

found = {}

for name, patterns in targets.items():
    for pattern in patterns:
        for symbol, desc in symbol_list:
            # Exact match
            if symbol == pattern:
                print(f"✅ {name}: {symbol}")
                print(f"   Description: {desc}")
                found[name] = symbol
                break
        if name in found:
            break
    
    if name not in found:
        print(f"❌ {name}: Not found on this broker")

print("\n" + "=" * 80)
print("COMPLETE LIST OF ALL FOREX PAIRS ON YOUR BROKER")
print("=" * 80)
print("\nShowing all forex pairs (for reference):\n")

forex_pairs = []
for symbol, desc in symbol_list:
    # Common forex patterns
    if any(x in symbol.upper() for x in ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD']):
        # Must have exactly one of each currency (proper pair)
        if symbol.endswith('m') or '/' in symbol or len(symbol) == 6:
            if 'vs' in desc.lower() or '/' in symbol:
                forex_pairs.append((symbol, desc))

# Sort and show top 30
forex_pairs = sorted(forex_pairs)[:30]
for symbol, desc in forex_pairs:
    print(f"   {symbol:20s} - {desc}")

print("\n" + "=" * 80)
print("RECOMMENDED CONFIG FOR YOUR BROKER")
print("=" * 80)

if found:
    print("\n# Copy this to config/config.py:\n")
    
    print("TRENDING_PAIRS = [")
    for name in ["Gold (XAU/USD)", "Silver (XAG/USD)", "Oil (WTI)", "Natural Gas", 
                 "S&P 500", "NASDAQ", "Dow Jones", "Bitcoin"]:
        if name in found:
            print(f'    "{found[name]}",  # {name}')
    print("]")
    print()
    
    print("RANGING_PAIRS = [")
    for name in ["EUR/USD", "EUR/GBP", "USD/CHF"]:
        if name in found:
            print(f'    "{found[name]}",  # {name}')
    print("]")
    print()
    
    print("MIXED_PAIRS = [")
    for name in ["GBP/USD", "AUD/USD", "USD/CAD", "NZD/USD"]:
        if name in found:
            print(f'    "{found[name]}",  # {name}')
    print("]")
    print()
    
    print("ALL_PAIRS = TRENDING_PAIRS + RANGING_PAIRS + MIXED_PAIRS")

print("\n" + "=" * 80)
print("CAN'T FIND A SYMBOL?")
print("=" * 80)
print("\n1. Open MT5 → Market Watch")
print("2. Right-click → Show All")
print("3. Find the symbol you want")
print("4. Look at the exact name (case-sensitive!)")
print("5. Add it to config.py manually")
print("\nOR search the complete symbol list above!")

mt5.shutdown()
