"""
MT5 Connection Test & Debug
Tests MT5 connection and data fetching for all pairs
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import *
import MetaTrader5 as mt5

print("=" * 80)
print("MT5 CONNECTION & DATA TEST")
print("=" * 80)

# Test 1: MT5 Initialize
print("\n1️⃣ Testing MT5 Initialize...")
if not mt5.initialize():
    print(f"❌ FAILED: {mt5.last_error()}")
    print("\n⚠️ SOLUTIONS:")
    print("   - Make sure MetaTrader 5 is installed")
    print("   - Open MT5 application")
    print("   - Try restarting MT5")
    sys.exit(1)
else:
    print("✅ MT5 Initialized")

# Test 2: Login
print("\n2️⃣ Testing MT5 Login...")
broker_config = MT5_CONFIG.get(MT5_BROKER)
if not broker_config:
    print(f"❌ No config found for broker: {MT5_BROKER}")
    sys.exit(1)

print(f"   Broker: {MT5_BROKER}")
print(f"   Server: {broker_config['server']}")
print(f"   Login: {broker_config['login']}")

authorized = mt5.login(
    login=broker_config['login'],
    password=broker_config['password'],
    server=broker_config['server']
)

if not authorized:
    print(f"❌ LOGIN FAILED: {mt5.last_error()}")
    print("\n⚠️ SOLUTIONS:")
    print("   - Check login number is correct")
    print("   - Check password is correct")
    print("   - Check server name matches MT5 exactly")
    print(f"   - Current server: {broker_config['server']}")
    print("\n💡 To find correct server name:")
    print("   1. Open MT5")
    print("   2. Go to Tools → Options → Server")
    print("   3. Copy exact server name")
    mt5.shutdown()
    sys.exit(1)
else:
    account = mt5.account_info()
    print(f"✅ Login successful!")
    print(f"   Account: {account.login}")
    print(f"   Server: {account.server}")
    print(f"   Balance: ${account.balance:.2f}")
    print(f"   Currency: {account.currency}")

# Test 3: Check available symbols
print("\n3️⃣ Getting available symbols...")
all_symbols = mt5.symbols_get()
if all_symbols:
    print(f"✅ Found {len(all_symbols)} total symbols on broker")
else:
    print("⚠️ No symbols found")

# Test 4: Test each configured pair
print("\n4️⃣ Testing configured pairs...")
print(f"   Configured pairs: {len(ALL_PAIRS)}")
print()

successful_pairs = []
failed_pairs = []

for symbol in ALL_PAIRS:
    # Check if symbol exists
    symbol_info = mt5.symbol_info(symbol)
    
    if symbol_info is None:
        print(f"❌ {symbol} - NOT FOUND on broker")
        failed_pairs.append(symbol)
        continue
    
    # Check if visible
    if not symbol_info.visible:
        print(f"⚠️ {symbol} - Found but not visible, enabling...")
        if mt5.symbol_select(symbol, True):
            print(f"   ✅ Enabled {symbol}")
        else:
            print(f"   ❌ Failed to enable {symbol}")
            failed_pairs.append(symbol)
            continue
    
    # Try to fetch data
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 10)
    
    if rates is not None and len(rates) > 0:
        print(f"✅ {symbol} - OK (fetched {len(rates)} bars)")
        print(f"   Last price: {rates[-1]['close']:.5f}")
        successful_pairs.append(symbol)
    else:
        print(f"❌ {symbol} - No data available")
        failed_pairs.append(symbol)

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✅ Successful: {len(successful_pairs)}/{len(ALL_PAIRS)}")
if successful_pairs:
    print("   " + ", ".join(successful_pairs))

if failed_pairs:
    print(f"\n❌ Failed: {len(failed_pairs)}/{len(ALL_PAIRS)}")
    print("   " + ", ".join(failed_pairs))
    
    print("\n⚠️ COMMON ISSUES WITH FAILED PAIRS:")
    print("\n1. Symbol name different on your broker:")
    for symbol in failed_pairs:
        print(f"   - {symbol} might be named differently")
        print(f"     Try searching in MT5 Market Watch")
    
    print("\n2. Not available on your broker:")
    print("   Some brokers don't offer all pairs")
    print("   Example: Exness has XAUUSD, but maybe not BTCUSD")
    
    print("\n3. Need to enable in Market Watch:")
    print("   1. Open MT5")
    print("   2. Right-click Market Watch")
    print("   3. Click 'Show All'")
    print("   4. Find your symbols and enable them")
    
    print("\n💡 SOLUTIONS:")
    print("\nOption A: Find correct symbol names")
    print("   1. Open MT5 Market Watch")
    print("   2. Find symbols you want (Gold, EUR/USD, etc.)")
    print("   3. Note exact names (might be XAU/USD, GOLD, etc.)")
    print("   4. Update SYMBOL_MAP in config/config.py")
    
    print("\nOption B: Remove unavailable pairs")
    print("   Edit config/config.py and remove symbols you don't have")

print("\n" + "=" * 80)

# Test 5: Search for Gold (common issue)
print("\n5️⃣ Searching for Gold symbol...")
print("   Looking for: XAUUSD, GOLD, XAU/USD variations...")
gold_variations = ["XAUUSD", "GOLD", "XAU/USD", "XAUUSD.a", "XAUUSD.", "GOLDm"]
for var in gold_variations:
    info = mt5.symbol_info(var)
    if info:
        print(f"   ✅ Found: {var}")
        print(f"      Description: {info.description}")

print("\n" + "=" * 80)

# Cleanup
mt5.shutdown()
print("\n✅ Test complete!")
print("\nIf you had failed pairs, update config/config.py with correct symbol names")
print("or remove pairs your broker doesn't support.")
