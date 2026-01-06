# 📊 BROKER SYMBOL NAMING REFERENCE

## Common Symbol Naming Across Brokers

Different brokers use different naming conventions. Here's what to expect:

---

## 🏦 EXNESS

**Pattern:** Usually adds "m" suffix (mini/standard lots)

**Common Symbols:**
- Gold: `XAUUSDm`
- Silver: `XAGUSDm`
- EUR/USD: `EURUSDm`
- GBP/USD: `GBPUSDm`
- Oil (WTI): `USOILm`
- S&P 500: `US500m` or `SPX500m`
- NASDAQ: `USTECm` or `NAS100m`
- Bitcoin: `BTCUSDm`

---

## 🏦 IC MARKETS

**Pattern:** Standard names, sometimes with suffixes

**Common Symbols:**
- Gold: `XAUUSD` or `GOLD`
- Silver: `XAGUSD` or `SILVER`
- EUR/USD: `EURUSD`
- GBP/USD: `GBPUSD`
- Oil (WTI): `USOIL` or `WTI`
- S&P 500: `US500` or `SPX500`
- NASDAQ: `USTEC` or `NAS100`
- Bitcoin: May not be available

---

## 🏦 DERIV

**Pattern:** Uses descriptive names

**Common Symbols:**
- Gold: `XAUUSD` or `Gold`
- Silver: `XAGUSD` or `Silver`
- EUR/USD: `EURUSD` or `EUR/USD`
- GBP/USD: `GBPUSD` or `GBP/USD`
- Oil: `WTI` or `Crude Oil`
- Indices: Named like `US SPX 500`, `US Tech 100`
- Bitcoin: `BTCUSD` or `BTC/USD`

---

## 🏦 OCTAFX

**Pattern:** Standard forex naming

**Common Symbols:**
- Gold: `XAUUSD`
- Silver: `XAGUSD`
- EUR/USD: `EURUSD`
- GBP/USD: `GBPUSD`
- Oil (WTI): `USOIL` or `CL`
- Indices: `US500`, `NAS100`, `US30`
- Bitcoin: May vary or not available

---

## 🏦 AVATRADE

**Pattern:** Clean standard names

**Common Symbols:**
- Gold: `XAUUSD`
- Silver: `XAGUSD`
- EUR/USD: `EURUSD`
- GBP/USD: `GBPUSD`
- Oil (WTI): `USOIL`
- S&P 500: `SPX500`
- NASDAQ: `NAS100`
- Bitcoin: `BTCUSD`

---

## 🔍 HOW TO FIND YOUR BROKER'S SYMBOLS

### Method 1: Use Our Script
```bash
python find_correct_symbols.py
```

### Method 2: Check MT5 Manually
1. Open MetaTrader 5
2. Right-click on "Market Watch"
3. Select "Show All"
4. Scroll through the list
5. Note the EXACT names (case-sensitive!)

### Method 3: Search in MT5
1. Press `Ctrl+U` in MT5
2. Go to "Symbols" tab
3. Search for what you want (Gold, EUR, etc.)
4. Check the exact symbol name

---

## ⚠️ COMMON VARIATIONS

### Gold (XAU/USD):
- `XAUUSD` ← Most common
- `XAUUSDm` ← Exness
- `GOLD` ← Some brokers
- `XAU/USD` ← Descriptive format

### EUR/USD:
- `EURUSD` ← Most common
- `EURUSDm` ← Exness
- `EUR/USD` ← Descriptive format
- `EURUSD.` ← Some add dot suffix

### Oil (WTI):
- `USOIL` ← Common
- `USOILm` ← Exness
- `WTI` ← Some brokers
- `CL` or `CLm` ← Futures style

### S&P 500:
- `US500` ← Common
- `US500m` ← Exness
- `SPX500` ← Alternative
- `SP500` ← Short form

### NASDAQ:
- `USTEC` ← Common
- `USTECm` ← Exness
- `NAS100` ← Alternative
- `NDX` ← Some brokers

---

## 📝 TIPS FOR FINDING SYMBOLS

### 1. Check Suffix Patterns
Some brokers add:
- `m` = mini/standard lots (Exness)
- `.` = dot suffix (some brokers)
- `_x100m` = multiplied contracts (Exness indices)

### 2. Search by Description
In MT5 Market Watch, symbols have descriptions:
- Look for "Gold vs US Dollar"
- Look for "Euro vs US Dollar"
- Easier than guessing symbol names!

### 3. Enable in Market Watch
Symbol exists but not showing?
1. Right-click Market Watch
2. Click "Symbols"
3. Find your symbol
4. Click "Show" button

### 4. Check Categories
MT5 organizes by categories:
- Forex Major
- Forex Minor
- Forex Exotic
- Commodities
- Indices
- Cryptocurrencies

---

## 🎯 WHAT TO DO NOW

1. **Run the corrected script:**
   ```bash
   python find_correct_symbols.py
   ```

2. **Copy the output** to `config/config.py`

3. **Verify in MT5:**
   - Open each symbol in MT5
   - Make sure it shows price data
   - Check it's the right instrument!

4. **Test the scanner:**
   ```bash
   python main.py --test
   ```

---

## ❓ STILL CAN'T FIND A SYMBOL?

### Option 1: It's Not Available
Your broker might not offer that instrument.
- Example: Not all brokers have Bitcoin
- Example: Some don't have Natural Gas

**Solution:** Remove it from config or choose alternative

### Option 2: Different Name
Your broker uses a completely different name.

**Solution:** 
1. Open MT5
2. Search for the instrument manually
3. Copy EXACT name
4. Add to config.py

### Option 3: Need to Request Access
Some brokers require you to request access to certain instruments.

**Solution:** Contact broker support

---

## 🚀 QUICK REFERENCE

**For Exness (Your Broker):**
- Add "m" to standard names
- Example: `EURUSD` → `EURUSDm`
- Example: `XAUUSD` → `XAUUSDm`

**Test It:**
```python
# In your config.py
TRENDING_PAIRS = [
    "XAUUSDm",    # Gold
    "EURUSDm",    # EUR/USD (if you want trending EUR)
]
```

**Run Scanner:**
```bash
python main.py
```

Should work! ✅
