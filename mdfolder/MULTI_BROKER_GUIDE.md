# 🌐 MULTI-BROKER CONFIGURATION GUIDE

## ✅ UNIVERSAL CONFIG - WORKS WITH ALL YOUR BROKERS!

The new `config_universal.py` automatically uses the correct symbol names for whichever broker you choose!

---

## 🔄 HOW TO SWITCH BROKERS (ONE LINE!)

### **Just change this line in config.py:**

```python
MT5_BROKER = "Exness"  # Change to any broker below
```

**Options:**
- `"Exness"` → Uses XAUUSDm, EURUSDm (with "m")
- `"ICMarkets"` → Uses XAUUSD, EURUSD (standard)
- `"Deriv"` → Uses XAUUSD, EURUSD (standard)
- `"OctaFX"` → Uses XAUUSD, EURUSD (standard)
- `"AvaTrade"` → Uses XAUUSD, SPX500 (clean names)

**That's it!** Scanner automatically uses correct names! 🎯

---

## 📊 SYMBOL MAPPING BY BROKER

### **🟢 EXNESS (Your Current)**
```python
Gold: XAUUSDm    (adds "m")
EUR/USD: EURUSDm
S&P 500: US500m
Bitcoin: BTCUSDm
```

### **🟢 IC MARKETS**
```python
Gold: XAUUSD     (standard)
EUR/USD: EURUSD
S&P 500: US500
Bitcoin: N/A (not available)
```

### **🟢 DERIV**
```python
Gold: XAUUSD
EUR/USD: EURUSD
S&P 500: US500
Bitcoin: BTCUSD  (available!)
```

### **🟢 OCTAFX**
```python
Gold: XAUUSD
EUR/USD: EURUSD
S&P 500: US500
NASDAQ: NAS100
```

### **🟢 AVATRADE**
```python
Gold: XAUUSD
EUR/USD: EURUSD
S&P 500: SPX500  (different!)
Bitcoin: BTCUSD
```

---

## 🚀 QUICK BROKER SWITCH EXAMPLE

### **Currently using Exness, want to try IC Markets:**

**Step 1:** Open `config/config.py`

**Step 2:** Change this line:
```python
MT5_BROKER = "Exness"  # FROM THIS
```

To:
```python
MT5_BROKER = "ICMarkets"  # TO THIS
```

**Step 3:** Run scanner:
```bash
python main.py
```

**That's it!** Scanner now uses IC Markets symbols automatically! ✅

---

## 🔍 HOW IT WORKS

The config has a **BROKER_SYMBOLS** dictionary:

```python
BROKER_SYMBOLS = {
    "Exness": {
        "GOLD": "XAUUSDm",
        "EURUSD": "EURUSDm",
        ...
    },
    "ICMarkets": {
        "GOLD": "XAUUSD",
        "EURUSD": "EURUSD",
        ...
    },
    ...
}
```

When you run the scanner:
1. Reads `MT5_BROKER` setting
2. Loads correct symbols from `BROKER_SYMBOLS[MT5_BROKER]`
3. Scans with those symbols
4. Everything works! 🎯

---

## ⚙️ MULTI-BROKER SETUP

Want to trade with multiple brokers simultaneously? No problem!

### **Option 1: Multiple Config Files**

```bash
config/
├── config_exness.py
├── config_icmarkets.py
└── config_deriv.py
```

Run with:
```bash
python main.py --config config_exness.py
```

### **Option 2: Environment Variable**

Set in terminal:
```bash
# Windows
set SCANNER_BROKER=ICMarkets
python main.py

# Linux/Mac
export SCANNER_BROKER=ICMarkets
python main.py
```

---

## 🧪 TESTING EACH BROKER

### **Test Exness:**
```python
# In config.py
MT5_BROKER = "Exness"
```
```bash
python test_mt5_connection.py
```

Should show:
```
✅ XAUUSDm - OK
✅ EURUSDm - OK
```

### **Test IC Markets:**
```python
# In config.py
MT5_BROKER = "ICMarkets"
```
```bash
python test_mt5_connection.py
```

Should show:
```
✅ XAUUSD - OK
✅ EURUSD - OK
```

---

## 📋 BROKER COMPARISON

| Feature | Exness | IC Markets | Deriv | OctaFX | AvaTrade |
|---------|--------|------------|-------|--------|----------|
| **Gold** | XAUUSDm | XAUUSD | XAUUSD | XAUUSD | XAUUSD |
| **EUR/USD** | EURUSDm | EURUSD | EURUSD | EURUSD | EURUSD |
| **S&P 500** | US500m | US500 | US500 | US500 | SPX500 |
| **NASDAQ** | USTECm | USTEC | USTEC | NAS100 | NAS100 |
| **Bitcoin** | BTCUSDm | ❌ | BTCUSD | ❌ | BTCUSD |
| **Naming** | Add "m" | Standard | Standard | Standard | Clean |

---

## 🆘 TROUBLESHOOTING

### **Symbol Not Found After Switch?**

Run this to find exact names for YOUR broker:
```bash
python find_correct_symbols.py
```

Then update `BROKER_SYMBOLS` in config:
```python
BROKER_SYMBOLS = {
    "YourBroker": {
        "GOLD": "YOUR_EXACT_SYMBOL_NAME",
        ...
    }
}
```

### **Can't Connect to New Broker?**

Check credentials in `MT5_CONFIG`:
```python
MT5_CONFIG = {
    "ICMarkets": {
        "login": YOUR_ACCOUNT,
        "password": "YOUR_PASSWORD",
        "server": "YOUR_SERVER",  # Check MT5 for exact name!
    }
}
```

---

## 💡 BEST PRACTICES

### **1. Test Before Switching**
```bash
python test_mt5_connection.py
```

### **2. Keep Separate Accounts**
Don't mix live/demo in same config:
```python
# Good
MT5_BROKER = "Exness"  # Live
# or
MT5_BROKER = "ExnessDemo"  # Demo

# Bad
MT5_BROKER = "Exness"  # Switching between live/demo
```

### **3. Backup Config**
Before major changes:
```bash
copy config.py config_backup.py
```

### **4. Document Custom Symbols**
If you find different names:
```python
# Add comment explaining
BROKER_SYMBOLS = {
    "MyBroker": {
        "GOLD": "GOLD.a",  # Note: Uses .a suffix
    }
}
```

---

## 🎯 RECOMMENDED SETUP

For multiple brokers, create profiles:

```python
# At top of config.py
ACTIVE_PROFILE = "EXNESS_LIVE"  # Change this to switch!

PROFILES = {
    "EXNESS_LIVE": {
        "broker": "Exness",
        "login": 172512161,
    },
    "IC_MARKETS_DEMO": {
        "broker": "ICMarkets",
        "login": 11583834,
    },
    "DERIV_LIVE": {
        "broker": "Deriv",
        "login": 21819122,
    }
}

# Load active profile
profile = PROFILES[ACTIVE_PROFILE]
MT5_BROKER = profile["broker"]
```

---

## ✅ MIGRATION CHECKLIST

When switching brokers:

- [ ] Update `MT5_BROKER` in config
- [ ] Verify login credentials
- [ ] Test connection: `python test_mt5_connection.py`
- [ ] Check symbol availability
- [ ] Update custom symbols if needed
- [ ] Run test scan: `python main.py --test`
- [ ] Verify dashboard shows data
- [ ] Start live scanning!

---

## 🔄 EXAMPLE: SWITCHING WORKFLOW

### **Morning: Trade Exness**
```python
MT5_BROKER = "Exness"
```
```bash
python main.py
```
Dashboard: `localhost:8000`

### **Afternoon: Switch to IC Markets**
```python
MT5_BROKER = "ICMarkets"
```
```bash
# Stop Exness scanner (Ctrl+C)
python main.py
```
Dashboard: `localhost:8000` (same URL, different data!)

---

## 📊 FALLBACK: YAHOO FINANCE

If MT5 fails, scanner uses Yahoo Finance automatically:
```python
YAHOO_FINANCE_ENABLED = True
```

Works regardless of broker! ✅

---

## 🎉 SUMMARY

**Old Way:**
- Manually edit 50+ lines
- Copy/paste symbol names
- Break things
- Frustration 😤

**New Way:**
- Change ONE line: `MT5_BROKER = "NewBroker"`
- Run scanner
- Works perfectly 🎯

---

**The universal config makes multi-broker trading EASY!** 🚀

Just set `MT5_BROKER` and go!
