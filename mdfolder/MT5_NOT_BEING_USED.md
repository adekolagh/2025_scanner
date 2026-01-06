# 🚨 CRITICAL: MT5 NOT BEING USED!

## ❌ THE PROBLEM:

Your logs show:
```
WARNING - No data for GC=F W1  ← Trying Yahoo Finance!
ERROR - $XAUUSDM: possibly delisted
```

**Scanner is using Yahoo Finance instead of MT5!**

Even though:
- ✅ MT5 is installed
- ✅ You're logged in
- ✅ test_mt5_connection.py works

**The scanner is NOT using MT5!**

---

## 🎯 WHY THIS HAPPENS:

When scanner starts, MT5 connection **fails silently**, so it falls back to Yahoo.

**Possible reasons:**
1. MT5 not running when scanner starts
2. MT5 connection fails in scanner context
3. Credentials/config issue in scanner

---

## ✅ IMMEDIATE FIX (3 Steps):

### **Step 1: Ensure MT5 is Running FIRST**

**BEFORE running scanner:**
1. Open MetaTrader 5 application
2. Login to your account
3. Check "Connected" status (bottom right)
4. **THEN** run scanner

```bash
# MT5 must be running BEFORE this!
python main.py
```

---

### **Step 2: Run Diagnostic**

```bash
python diagnose_data_source.py
```

**This will show:**
- ✅ If MT5 initializes
- ✅ If MT5 login works
- ✅ If MT5 can fetch data
- ❌ Exact error if MT5 fails

**Share the output with me!**

---

### **Step 3: Check Logs at Scanner Start**

When you run `python main.py`, look for these lines:

**GOOD:**
```
✅ Primary data source: MT5 (Exness)
Connected to MT5: Exness-MT5Real2, Login: 172512161
```

**BAD:**
```
⚠️ MT5 connection failed, will use Yahoo Finance
```

**If you see BAD, MT5 didn't connect!**

---

## 🔧 COMMON FIXES:

### **Fix 1: MT5 Not Running**

**Problem:** Scanner starts before MT5
**Solution:**
1. Open MT5 **FIRST**
2. Login
3. **THEN** run scanner

### **Fix 2: MT5 Closes After Test**

**Problem:** You run test script, MT5 connects, then closes
**Solution:** Keep MT5 **OPEN** while running scanner

### **Fix 3: Wrong Broker Config**

**Problem:** Config has wrong credentials
**Solution:** Verify in config.py:
```python
MT5_CONFIG = {
    "Exness": {
        "login": 172512161,  # YOUR ACTUAL LOGIN
        "password": "YOUR_ACTUAL_PASSWORD",
        "server": "Exness-MT5Real2",  # EXACT SERVER NAME
    }
}
```

### **Fix 4: MT5 Library Issue**

**Problem:** MetaTrader5 Python package not working
**Solution:**
```bash
pip uninstall MetaTrader5
pip install MetaTrader5 --upgrade
```

---

## 📊 EXPECTED VS ACTUAL:

### **Expected (MT5 Working):**
```
Starting scan...
✅ Primary data source: MT5 (Exness)
Scanning XAUUSDm (1/15)...
  Fetching W1 data from MT5...
  Fetching D1 data from MT5...
  ✅ XAUUSDm: 45% probability
```

### **Actual (MT5 Not Working):**
```
Starting scan...
⚠️ MT5 connection failed, will use Yahoo Finance
Scanning XAUUSDm (1/15)...
  WARNING - No data for GC=F W1  ← Trying Yahoo!
  ERROR - $XAUUSDM: possibly delisted  ← Yahoo fails!
  ❌ No data for XAUUSDm from any source
```

---

## 🧪 DIAGNOSTIC WORKFLOW:

### **Step 1: Check MT5 Status**
```
1. Is MT5 application running? YES/NO
2. Are you logged in? YES/NO
3. Shows "Connected" in bottom right? YES/NO
```

### **Step 2: Test MT5 Connection**
```bash
python test_mt5_connection.py
```

**Should show:**
```
✅ MT5 Initialized
✅ Login successful
✅ XAUUSDm - OK (fetched 10 bars)
```

### **Step 3: Test Data Fetcher**
```bash
python diagnose_data_source.py
```

**Should show:**
```
✅ MT5 Initialized
✅ MT5 Login successful
✅ MT5 can fetch XAUUSDm data!
```

### **Step 4: Run Scanner with Logging**
```bash
python main.py
```

**Watch for:**
```
✅ Primary data source: MT5 (Exness)  ← GOOD!
```

OR

```
⚠️ MT5 connection failed  ← BAD!
```

---

## 🔍 IF DIAGNOSTIC SHOWS MT5 WORKS BUT SCANNER DOESN'T:

This means MT5 works in isolation but fails in scanner context.

**Possible causes:**
1. **Timing:** Scanner starts before MT5 fully initializes
2. **Multiple connections:** MT5 only allows one connection at a time
3. **State:** MT5 connection gets lost between test and scanner

**Solution:**
Add connection retry in scanner:

Edit `data/data_fetcher.py` line ~45:

```python
def _init_mt5(self):
    """Initialize MT5 connection with retry"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            mt5_config = self.config.get('MT5_CONFIG', {}).get(self.broker)
            if mt5_config is None:
                logger.error(f"No MT5 config for broker: {self.broker}")
                return
            
            self.mt5 = MT5Connector(mt5_config)
            self.mt5_connected = self.mt5.connect()
            
            if self.mt5_connected:
                self.primary_source = "MT5"
                logger.info(f"✅ Primary data source: MT5 ({self.broker})")
                return
            else:
                logger.warning(f"MT5 connection attempt {attempt+1}/{max_retries} failed")
                import time
                time.sleep(2)  # Wait 2 seconds before retry
                
        except Exception as e:
            logger.error(f"MT5 initialization error (attempt {attempt+1}): {e}")
    
    logger.warning("⚠️ MT5 connection failed after retries, will use Yahoo Finance")
    self.mt5_connected = False
    self.primary_source = "Yahoo Finance"
```

---

## ✅ VERIFICATION CHECKLIST:

- [ ] MT5 application is **OPEN**
- [ ] You are **LOGGED IN** to MT5
- [ ] MT5 shows "**Connected**" status
- [ ] `python test_mt5_connection.py` shows ✅ all green
- [ ] `python diagnose_data_source.py` shows ✅ MT5 works
- [ ] `python main.py` logs show "✅ Primary data source: MT5"
- [ ] Scanner logs show data being fetched (not "No data" errors)
- [ ] Dashboard shows actual trade setups

---

## 🎯 QUICK TEST:

Run this single command to see MT5 status:

```bash
python -c "import MetaTrader5 as mt5; print('✅ MT5 OK' if mt5.initialize() else '❌ MT5 FAIL')"
```

**If shows ❌:** MT5 is not accessible - open MT5 app first!

---

## 📁 FILES TO RUN:

1. **diagnose_data_source.py** - Shows if MT5 is being used
2. **test_mt5_connection.py** - Tests MT5 symbols
3. Then: **python main.py** - Run scanner

---

**MOST COMMON SOLUTION:**

```
1. Open MT5 application
2. Login to account
3. Wait for "Connected" status
4. Run: python main.py
```

**MT5 MUST be running BEFORE scanner starts!** 🎯
