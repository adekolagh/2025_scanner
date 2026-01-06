# 🏦 COMPLETE BROKER SYMBOL REFERENCE

## Symbol Names by Broker

---

## 🟢 EXNESS (Your Current Broker)

**Pattern:** Add "m" suffix to everything

### Working Config:
```python
TRENDING_PAIRS = [
    "XAUUSDm",   # Gold
    "XAGUSDm",   # Silver
    "USOILm",    # Oil WTI
    "XNGUSDm",   # Natural Gas
    "US500m",    # S&P 500
    "USTECm",    # NASDAQ
    "US30m",     # Dow Jones
    "BTCUSDm",   # Bitcoin
]

RANGING_PAIRS = [
    "EURUSDm",   # EUR/USD
    "EURGBPm",   # EUR/GBP
    "USDCHFm",   # USD/CHF
]

MIXED_PAIRS = [
    "GBPUSDm",   # GBP/USD
    "AUDUSDm",   # AUD/USD
    "USDCADm",   # USD/CAD
    "NZDUSDm",   # NZD/USD
]
```

**Note:** Some symbols like Oil Brent not available on Exness.

---

## 🟢 IC MARKETS

**Pattern:** Standard names, NO suffix

### Working Config:
```python
TRENDING_PAIRS = [
    "XAUUSD",    # Gold
    "XAGUSD",    # Silver
    "USOIL",     # Oil WTI (or "WTI")
    "NATGAS",    # Natural Gas (or "NG")
    "US500",     # S&P 500 (or "SPX500")
    "USTEC",     # NASDAQ (or "NAS100")
    "US30",      # Dow Jones (or "DJ30")
    # No Bitcoin on IC Markets
]

RANGING_PAIRS = [
    "EURUSD",    # EUR/USD
    "EURGBP",    # EUR/GBP
    "USDCHF",    # USD/CHF
]

MIXED_PAIRS = [
    "GBPUSD",    # GBP/USD
    "AUDUSD",    # AUD/USD
    "USDCAD",    # USD/CAD
    "NZDUSD",    # NZD/USD
]
```

**IC Markets Notes:**
- Clean standard names
- No crypto available
- Some brokers use alternative names (check MT5)

---

## 🟢 DERIV

**Pattern:** Standard or descriptive

### Typical Config:
```python
TRENDING_PAIRS = [
    "XAUUSD",    # Gold (or "frxXAUUSD")
    "XAGUSD",    # Silver (or "frxXAGUSD")
    # Oil: Check if "USOIL" or "WTI"
    # Indices: "US SPX 500" or similar
    "BTCUSD",    # Bitcoin (available!)
]

RANGING_PAIRS = [
    "EURUSD",    # EUR/USD (or "frxEURUSD")
    "EURGBP",    # EUR/GBP
    "USDCHF",    # USD/CHF
]

MIXED_PAIRS = [
    "GBPUSD",    # GBP/USD
    "AUDUSD",    # AUD/USD
    "USDCAD",    # USD/CAD
    "NZDUSD",    # NZD/USD
]
```

**Deriv Notes:**
- May use "frx" prefix for forex
- May use descriptive names like "US SPX 500"
- Bitcoin available
- Check exact names in MT5

---

## 🟢 OCTAFX

**Pattern:** Standard names

### Typical Config:
```python
TRENDING_PAIRS = [
    "XAUUSD",    # Gold
    "XAGUSD",    # Silver
    "USOIL",     # Oil (or "CL")
    "US500",     # S&P 500
    "NAS100",    # NASDAQ
    "US30",      # Dow Jones
    # Check if Bitcoin available
]

RANGING_PAIRS = [
    "EURUSD",
    "EURGBP",
    "USDCHF",
]

MIXED_PAIRS = [
    "GBPUSD",
    "AUDUSD",
    "USDCAD",
    "NZDUSD",
]
```

**OctaFX Notes:**
- Standard forex names
- Check indices names (may vary)
- Crypto limited

---

## 🟢 AVATRADE

**Pattern:** Clean standard

### Typical Config:
```python
TRENDING_PAIRS = [
    "XAUUSD",    # Gold
    "XAGUSD",    # Silver
    "USOIL",     # Oil
    "SPX500",    # S&P 500
    "NAS100",    # NASDAQ
    "BTCUSD",    # Bitcoin (if available)
]

RANGING_PAIRS = [
    "EURUSD",
    "EURGBP",
    "USDCHF",
]

MIXED_PAIRS = [
    "GBPUSD",
    "AUDUSD",
    "USDCAD",
    "NZDUSD",
]
```

**AvaTrade Notes:**
- Clean names
- Check if crypto available
- Indices may use full names

---

## 🔍 HOW TO FIND YOUR BROKER'S EXACT NAMES

### Method 1: Use Our Script (Best!)
```bash
python find_correct_symbols.py
```

This automatically searches YOUR broker and shows exact names!

### Method 2: MT5 Manual Check
1. Open MetaTrader 5
2. Press `Ctrl+U` (or Tools → Options)
3. Go to "Symbols" tab
4. Search for instrument
5. Note EXACT name (case-sensitive!)

### Method 3: Market Watch
1. Right-click Market Watch
2. Click "Show All"
3. Scroll through categories:
   - Forex Major
   - Forex Minor
   - Commodities
   - Indices
   - Crypto
4. Note exact symbol names

---

## 📋 COMMON SYMBOL VARIATIONS

### Gold:
- `XAUUSD` ← Most brokers
- `XAUUSDm` ← Exness
- `GOLD` ← Some brokers
- `frxXAUUSD` ← Deriv style

### EUR/USD:
- `EURUSD` ← Standard
- `EURUSDm` ← Exness
- `frxEURUSD` ← Deriv style
- `EUR/USD` ← Descriptive

### S&P 500:
- `US500` ← Common
- `US500m` ← Exness
- `SPX500` ← Alternative
- `SP500` ← Short
- `US SPX 500` ← Descriptive

### Oil (WTI):
- `USOIL` ← Common
- `USOILm` ← Exness
- `WTI` ← Abbreviated
- `CL` ← Futures style

---

## 🎯 QUICK REFERENCE TABLE

| Instrument | Exness | IC Markets | Deriv | Others |
|------------|--------|------------|-------|--------|
| Gold | XAUUSDm | XAUUSD | XAUUSD | XAUUSD |
| Silver | XAGUSDm | XAGUSD | XAGUSD | XAGUSD |
| EUR/USD | EURUSDm | EURUSD | EURUSD | EURUSD |
| GBP/USD | GBPUSDm | GBPUSD | GBPUSD | GBPUSD |
| Oil WTI | USOILm | USOIL | Check | USOIL |
| S&P 500 | US500m | US500 | Check | US500/SPX500 |
| NASDAQ | USTECm | USTEC | Check | NAS100 |
| Bitcoin | BTCUSDm | N/A | BTCUSD | Varies |

---

## ⚙️ CONFIG TEMPLATE FOR ANY BROKER

```python
# 1. Find your symbols (run: python find_correct_symbols.py)
# 2. Replace with YOUR broker's exact names below:

TRENDING_PAIRS = [
    "YOUR_GOLD_SYMBOL",      # e.g., XAUUSDm or XAUUSD
    "YOUR_SILVER_SYMBOL",    # e.g., XAGUSDm or XAGUSD
    "YOUR_OIL_SYMBOL",       # e.g., USOILm or USOIL
    "YOUR_GAS_SYMBOL",       # e.g., XNGUSDm or NATGAS
    "YOUR_SP500_SYMBOL",     # e.g., US500m or US500
    "YOUR_NASDAQ_SYMBOL",    # e.g., USTECm or USTEC
    "YOUR_DOW_SYMBOL",       # e.g., US30m or US30
    "YOUR_BTC_SYMBOL",       # e.g., BTCUSDm or BTCUSD (if available)
]

RANGING_PAIRS = [
    "YOUR_EURUSD_SYMBOL",    # e.g., EURUSDm or EURUSD
    "YOUR_EURGBP_SYMBOL",    # e.g., EURGBPm or EURGBP
    "YOUR_USDCHF_SYMBOL",    # e.g., USDCHFm or USDCHF
]

MIXED_PAIRS = [
    "YOUR_GBPUSD_SYMBOL",    # e.g., GBPUSDm or GBPUSD
    "YOUR_AUDUSD_SYMBOL",    # e.g., AUDUSDm or AUDUSD
    "YOUR_USDCAD_SYMBOL",    # e.g., USDCADm or USDCAD
    "YOUR_NZDUSD_SYMBOL",    # e.g., NZDUSDm or NZDUSD
]
```

---

## 🚀 SWITCHING BROKERS?

If you switch from Exness to IC Markets:

**Old (Exness):**
```python
"XAUUSDm"
"EURUSDm"
```

**New (IC Markets):**
```python
"XAUUSD"
"EURUSD"
```

Just **remove the "m"** suffix!

---

## ✅ VERIFICATION STEPS

After updating config:

1. **Save config.py**
2. **Run test:**
   ```bash
   python test_mt5_connection.py
   ```
3. **Should see:**
   ```
   ✅ XAUUSDm - OK (fetched 10 bars)
   ✅ EURUSDm - OK (fetched 10 bars)
   ```
4. **If "NOT FOUND":**
   - Symbol name wrong
   - Not available on broker
   - Need to enable in MT5

---

**Remember:** When in doubt, run `python find_correct_symbols.py` to see YOUR broker's exact names! 🎯
