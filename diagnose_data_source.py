"""
Check Data Source Priority - MT5 vs Yahoo
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("DATA SOURCE DIAGNOSTIC")
print("=" * 80)

# Check config
from config.config import *

print(f"\n1. MT5 Settings:")
print(f"   MT5_ENABLED: {MT5_ENABLED}")
print(f"   MT5_BROKER: {MT5_BROKER}")
print(f"   YAHOO_FINANCE_ENABLED: {YAHOO_FINANCE_ENABLED}")

# Check MT5 connection
print(f"\n2. Testing MT5 Connection:")
try:
    import MetaTrader5 as mt5
    
    if not mt5.initialize():
        print(f"   ❌ MT5 Initialize FAILED: {mt5.last_error()}")
        print(f"   This is why scanner uses Yahoo instead!")
    else:
        print(f"   ✅ MT5 Initialized")
        
        broker_config = MT5_CONFIG.get(MT5_BROKER)
        authorized = mt5.login(
            login=broker_config['login'],
            password=broker_config['password'],
            server=broker_config['server']
        )
        
        if not authorized:
            print(f"   ❌ MT5 Login FAILED: {mt5.last_error()}")
            print(f"   Scanner will fallback to Yahoo!")
        else:
            print(f"   ✅ MT5 Login successful")
            
            # Try to fetch one symbol
            symbol = "XAUUSDm"
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 10)
            
            if rates is None or len(rates) == 0:
                print(f"   ❌ Can't fetch {symbol} from MT5")
                print(f"   Error: {mt5.last_error()}")
                print(f"   Scanner will use Yahoo fallback")
            else:
                print(f"   ✅ MT5 can fetch {symbol} data!")
                print(f"   Got {len(rates)} bars")
                print(f"   Last price: {rates[-1]['close']:.2f}")
        
        mt5.shutdown()
        
except ImportError:
    print(f"   ❌ MetaTrader5 module not installed!")
    print(f"   Install: pip install MetaTrader5")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check data fetcher priority
print(f"\n3. Checking Data Fetcher:")
try:
    from data.data_fetcher import DataFetcher
    
    config_dict = {
        'MT5_ENABLED': MT5_ENABLED,
        'MT5_BROKER': MT5_BROKER,
        'MT5_CONFIG': MT5_CONFIG,
        'YAHOO_FINANCE_ENABLED': YAHOO_FINANCE_ENABLED,
        'SYMBOL_MAP': SYMBOL_MAP
    }
    
    fetcher = DataFetcher(config_dict)
    
    print(f"   MT5 connector initialized: {fetcher.mt5_connector is not None}")
    print(f"   Yahoo connector initialized: {fetcher.yahoo_fetcher is not None}")
    
    # Try to fetch data
    print(f"\n4. Testing Data Fetch for XAUUSDm:")
    data = fetcher.get_data('XAUUSDm', 'H1', bars=10)
    
    if data is None or len(data) == 0:
        print(f"   ❌ No data returned!")
    else:
        print(f"   ✅ Got {len(data)} bars")
        print(f"   Source: Check logs above to see if MT5 or Yahoo was used")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("DIAGNOSIS:")
print("=" * 80)

print("""
If you see:
  ❌ MT5 Initialize FAILED
  → MT5 is not running or not accessible
  → Solution: Open MT5 application

  ❌ MT5 Login FAILED
  → Wrong credentials or server
  → Solution: Check config.py credentials

  ❌ Can't fetch XAUUSDm from MT5
  → Symbol not found on broker
  → Solution: Symbol names are correct

  ✅ All tests pass but scanner still uses Yahoo
  → data_fetcher.py has a bug
  → Check data/data_fetcher.py priority logic
""")

print("=" * 80)
