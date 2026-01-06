# 🚀 COMPLETE MARKET SCANNER - SETUP GUIDE

## ✅ THIS IS THE COMPLETE, WORKING PACKAGE!

Everything is included and configured to work together:
- ✅ Multi-broker config (Exness, IC Markets, Deriv, OctaFX, AvaTrade)
- ✅ MT5 data fetcher (tries MT5 first, Yahoo fallback)
- ✅ Fixed dashboard generator
- ✅ Web server with placeholder
- ✅ All __init__.py files included
- ✅ Complete scanner logic
- ✅ Alerts (Email, Telegram, Desktop, Sound)

---

## 📁 INSTALLATION (3 Steps):

### **Step 1: Extract Package**

Extract to: `C:\2025_scanner\market_scanner\`

Your structure should be:
```
market_scanner/
├── main.py
├── requirements.txt
├── config/
│   ├── __init__.py
│   └── config.py  ← Multi-broker config!
├── data/
├── engine/
├── indicators/
├── alerts/
├── scanner/
└── output/
```

---

### **Step 2: Install Dependencies**

```bash
cd C:\2025_scanner\market_scanner
pip install -r requirements.txt
```

**Required packages:**
- MetaTrader5
- pandas
- numpy
- yfinance
- requests
- python-telegram-bot
- plyer

---

### **Step 3: Configure Your Broker**

Edit `config/config.py`:

**Line 13 - Set active broker:**
```python
MT5_BROKER = "Exness"  # ← Change this to your broker!
```

**Lines 18-56 - Update credentials:**
```python
MT5_CONFIG = {
    "Exness": {
        "login": 172512161,  # ← YOUR ACCOUNT NUMBER
        "password": "YOUR_PASSWORD",  # ← YOUR PASSWORD
        "server": "Exness-MT5Real2",  # ← YOUR SERVER
    },
    # ... other brokers
}
```

**Lines 142-149 - Email settings:**
```python
EMAIL_CONFIG = {
    "smtp_server": "mail.adekay.com",
    "smtp_port": 465,
    "sender_email": "emma@adekay.com",
    "sender_password": "YOUR_PASSWORD",  # ← UPDATE
    "recipient_email": "adekolagafat@gmail.com",
    "use_ssl": True,
}
```

**Lines 151-155 - Telegram settings:**
```python
TELEGRAM_CONFIG = {
    "bot_token": "YOUR_BOT_TOKEN",  # ← UPDATE
    "chat_id": "YOUR_CHAT_ID",  # ← UPDATE
}
```

---

## 🌐 MULTI-BROKER USAGE:

### **Switch Brokers (One Line!):**

Just change line 13 in `config/config.py`:

```python
MT5_BROKER = "Exness"  # Options: Exness, ICMarkets, Deriv, OctaFX, AvaTrade
```

**Scanner automatically uses correct symbol names!**

### **Broker Symbol Mapping:**

**Exness:**
- XAUUSDm, EURUSDm, US500m (with "m")

**IC Markets:**
- XAUUSD, EURUSD, US500 (standard)

**Deriv:**
- XAUUSD, EURUSD, BTCUSD (standard)

**OctaFX:**
- XAUUSD, EURUSD, NAS100 (standard)

**AvaTrade:**
- XAUUSD, EURUSD, SPX500 (clean names)

---

## 🔧 CRITICAL: MT5 CONNECTION

**BEFORE running scanner:**

1. **Open MetaTrader 5 application**
2. **Login to your account**
3. **Verify "Connected" status** (bottom right)
4. **THEN run scanner**

**Why?** Scanner needs MT5 running to fetch data!

---

## ⚡ QUICK START:

### **Test MT5 Connection:**
```bash
python test_mt5_connection.py
```

**Expected:**
```
✅ MT5 Initialized
✅ Login successful
✅ XAUUSDm - OK (fetched 10 bars)
✅ EURUSDm - OK (fetched 10 bars)
...
✅ Successful: 15/15
```

### **Test All Systems:**
```bash
python main.py --test
```

**Tests:**
- MT5 connection
- Email alerts
- Telegram alerts
- Desktop notifications
- Data fetching

### **Run Scanner:**
```bash
python main.py
```

**What happens:**
1. Connects to MT5
2. Opens browser at `localhost:8000`
3. Runs first scan (20-30 seconds)
4. Dashboard updates automatically
5. Scans every 60 minutes
6. Sends alerts for setups

---

## 📊 EXPECTED OUTPUT:

### **When Scanner Starts:**

```
================================================================================
ACTIVE BROKER: Exness
================================================================================
Pairs to scan: 15
  1. XAUUSDm
  2. EURUSDm
  ...

✅ Primary data source: MT5 (Exness)
Connected to MT5: Exness-MT5Real2, Login: 172512161
Balance: $34.63

🌐 DASHBOARD WEB SERVER STARTED
   URL: http://localhost:8000/dashboard.html
   Dashboard will update automatically
================================================================================

Running first scan...
Scanning XAUUSDm (1/15)...
  Fetching W1 data from MT5...
  Fetching D1 data from MT5...
  ✅ XAUUSDm: 45% probability

Scanning EURUSDm (2/15)...
  ✅ EURUSDm: 72% probability

...

Scan complete! 15/15 pairs analyzed in 28.5s
```

### **Dashboard Opens:**

Browser automatically opens to: `http://localhost:8000`

Shows:
- 💥 BIG BANG (80%+) - Enter now!
- 🟠 ALMOST READY (70-79%)
- 🟡 GET READY (60-69%)
- 🔵 FORMING (40-59%)

Each setup shows:
- Symbol, Probability, Direction
- Entry, Stop Loss, Target
- HTF alignment, M15 confirmation
- ETA to entry

---

## 🎯 TROUBLESHOOTING:

### **Issue 1: "No data for XAUUSDm from any source"**

**Cause:** MT5 not connected

**Solution:**
1. Open MT5 application
2. Login
3. Verify "Connected"
4. Re-run scanner

### **Issue 2: "404 - File not found"**

**Cause:** Browser opened before first scan completed

**Solution:**
1. Wait 30 seconds
2. Press F5 to refresh
3. Dashboard appears!

### **Issue 3: "ModuleNotFoundError: No module named 'config.config'"**

**Cause:** Missing __init__.py files

**Solution:**
1. Verify `config/__init__.py` exists
2. Verify `data/__init__.py` exists
3. Re-extract complete package

### **Issue 4: Console shows "⚠️ MT5 connection failed"**

**Cause:** MT5 not running or credentials wrong

**Solution:**
1. Check MT5 is open and logged in
2. Verify credentials in `config/config.py`
3. Check server name matches MT5 exactly

---

## 📋 CONFIGURATION OPTIONS:

### **Scanning Settings:**

```python
SCAN_INTERVAL_MINUTES = 60  # How often to scan
AUTO_SCAN_ENABLED = True    # Auto-scan or manual only
```

### **Risk Management:**

```python
ACCOUNT_SIZE = 10000       # Your account size
RISK_PER_TRADE = 1.0       # Risk % per trade
```

### **Probability Thresholds:**

```python
PROB_GET_READY = 60        # 60%+ = GET READY
PROB_ALMOST_READY = 70     # 70%+ = ALMOST READY
PROB_BIG_BANG = 80         # 80%+ = BIG BANG
```

### **Alerts:**

```python
EMAIL_ENABLED = True
TELEGRAM_ENABLED = True
DESKTOP_ALERTS_ENABLED = True
SOUND_ALERTS_ENABLED = False  # Requires MP3 files
```

---

## 🔄 SWITCHING BROKERS:

### **Example: Switch from Exness to IC Markets**

**Step 1:** Edit `config/config.py` line 13:
```python
MT5_BROKER = "ICMarkets"  # Changed from "Exness"
```

**Step 2:** Update credentials (lines 23-29):
```python
"ICMarkets": {
    "login": YOUR_IC_ACCOUNT,
    "password": "YOUR_PASSWORD",
    "server": "ICMarketsSC-MT5-4",
}
```

**Step 3:** Open IC Markets MT5, login

**Step 4:** Run scanner:
```bash
python main.py
```

**Scanner now uses IC Markets symbols automatically!**

---

## 📊 WHAT THE SCANNER DOES:

### **For Each Symbol:**

1. **Fetches data** from MT5 (5 timeframes: W1, D1, H4, H1, M15)
2. **Calculates Murrey Math** levels
3. **Analyzes momentum** (RSI, ADX, EMA)
4. **Detects volume** spikes and springs
5. **Computes probability** (0-100%)
6. **Calculates risk** (entry, stop, targets)
7. **Estimates timing** (ETA to entry)
8. **Generates alerts** if thresholds met

### **Outputs:**

- **HTML Dashboard** at `output/dashboard.html`
- **Web Server** at `http://localhost:8000`
- **Email alerts** for 60%+ setups
- **Telegram messages**
- **Desktop notifications**
- **Log file** at `logs/scanner.log`

---

## ✅ VERIFICATION CHECKLIST:

Before first run:

- [ ] Extracted to `C:\2025_scanner\market_scanner\`
- [ ] Installed requirements: `pip install -r requirements.txt`
- [ ] Updated `config/config.py` with credentials
- [ ] Set `MT5_BROKER` to your broker
- [ ] MT5 application is **OPEN** and **LOGGED IN**
- [ ] Ran: `python test_mt5_connection.py` (shows ✅)
- [ ] Ready to run: `python main.py`

After first run:

- [ ] Console shows: "✅ Primary data source: MT5"
- [ ] Console shows: "Scan complete! 15/15 pairs analyzed"
- [ ] Browser opened to `localhost:8000`
- [ ] Dashboard shows setups
- [ ] No errors in console

---

## 🎯 SUMMARY:

**This is the COMPLETE, WORKING package!**

**What's included:**
- ✅ Multi-broker config (5 brokers ready!)
- ✅ MT5 connector with Yahoo fallback
- ✅ Complete scanner engine
- ✅ Fixed dashboard generator
- ✅ Web server with placeholder
- ✅ All alerts working
- ✅ All __init__.py files
- ✅ Complete documentation

**How to use:**
1. Extract package
2. Install requirements
3. Update config.py
4. Open MT5
5. Run: `python main.py`
6. Dashboard opens automatically!

**To switch brokers:**
1. Change one line: `MT5_BROKER = "NewBroker"`
2. Run scanner
3. Works with new broker!

---

**EVERYTHING WORKS TOGETHER NOW!** 🚀

Just extract, configure, and run!
