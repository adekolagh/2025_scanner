# 🚀 AUTO-BROKER FALLBACK - NEW FEATURE!

## ✅ WHAT CHANGED:

**Old behavior:**
```
Set: MT5_BROKER = "Exness"
Try: Exness
If fails: Use Yahoo Finance (FAILS because of symbol names)
Result: 0/15 pairs ❌
```

**New behavior:**
```
Set: MT5_BROKER = "Exness"
Try: Exness → FAILED
Try: ICMarkets → FAILED  
Try: Deriv → SUCCESS! ✅
Auto-map: XAUUSDm → XAUUSD (Exness to Deriv format)
Result: 15/15 pairs ✅
```

**Scanner now tries ALL brokers automatically!**

---

## 🎯 HOW IT WORKS:

Scanner tries brokers in this order:
1. **Your configured broker** (MT5_BROKER)
2. **All other brokers** you have credentials for
3. **Yahoo Finance** (last resort)

**First one that connects = WINS!**

---

## 📝 SETUP:

Add passwords for ALL brokers you have:

```python
# config/config.py

MT5_BROKER = "Exness"  # Preferred broker

MT5_CONFIG = {
    "Exness": {
        "login": 172512161,
        "password": "YOUR_PASSWORD",  # ← UPDATE!
        "server": "Exness-MT5Real2",
    },
    "ICMarkets": {
        "login": 11583834,
        "password": "YOUR_PASSWORD",  # ← UPDATE!
        "server": "ICMarketsSC-MT5-4",
    },
    # Add any others you have!
}
```

---

## ⚡ USAGE:

```bash
# 1. Open MT5 (any broker)
# 2. Run scanner
python main.py

# Scanner tries all brokers automatically!
```

---

## 📊 EXAMPLE OUTPUT:

```
🔍 Will try brokers in order: Exness, ICMarkets, Deriv

🔌 Attempting to connect to Exness...
❌ Exness failed

🔌 Attempting to connect to ICMarkets...
✅ Successfully connected to ICMarkets!
✅ PRIMARY DATA SOURCE: MT5 (ICMarkets)

🔄 Mapped XAUUSDm → XAUUSD
Scanning XAUUSD (1/15)...
✅ Data from MT5
```

**Auto-switched from Exness to ICMarkets!** ✅

---

## ✅ BENEFITS:

- **Reliable:** If one broker down → tries others
- **Automatic:** No manual switching needed
- **Smart:** Auto-converts symbol names
- **Transparent:** Full logging of what's happening

---

**NO MORE "NO DATA" ERRORS!** 🚀
