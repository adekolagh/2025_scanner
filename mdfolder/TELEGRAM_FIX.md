# 📱 TELEGRAM BOT SETUP - STEP BY STEP

## ⚠️ Current Error:
```
Telegram API error: 400 - chat not found
```

**This means:** Your `chat_id` is wrong or you haven't started the bot.

---

## ✅ COMPLETE FIX:

### **Step 1: Create Bot (If Not Done)**

1. Open Telegram app
2. Search for: `@BotFather`
3. Send: `/newbot`
4. Follow instructions:
   - Bot name: `My Market Scanner`
   - Username: `my_scanner_bot` (must end with "bot")
5. Copy the **bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

---

### **Step 2: Start Your Bot**

**THIS IS CRITICAL - MUST DO THIS:**

1. Search for your bot in Telegram (the username you created)
2. Click on it
3. Press **START** button at bottom
4. Send any message like: `Hello`

**If you skip this step, you'll get "chat not found" error!**

---

### **Step 3: Get Your Chat ID**

**Method A: Use Bot (Easiest)**

1. Search for: `@userinfobot` in Telegram
2. Send it any message
3. It will reply with your chat ID (a number like: `123456789`)
4. Copy this number

**Method B: Use API (Alternative)**

1. Start your bot (see Step 2!)
2. Send it a message: `Hello scanner`
3. Open this URL in browser (replace YOUR_BOT_TOKEN):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. Look for: `"chat":{"id":123456789`
5. Copy the number after `"id":`

---

### **Step 4: Update Config**

Open `config/config.py`, find line ~148:

```python
TELEGRAM_CONFIG = {
    "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",  # Your bot token
    "chat_id": "123456789",  # YOUR CHAT ID (as string!)
}
```

**IMPORTANT:**
- `bot_token`: Full token from BotFather
- `chat_id`: Just the number (but as string with quotes!)

---

### **Step 5: Test**

```bash
cd C:\2025_scanner\market_scanner
python main.py --test
```

Look for:
```
3️⃣ Testing Telegram...
✅ Telegram message sent successfully
```

Check your phone - you should get a test message!

---

## 🔧 COMMON ISSUES:

### **"Unauthorized"**
- Bot token is wrong
- Copy entire token from BotFather
- Should be like: `123456789:ABCdefGHI...` (long string)

### **"Chat not found"**
- You didn't press START in your bot
- OR chat_id is wrong
- **Fix:** Open bot in Telegram, press START, get new chat_id

### **"Forbidden"**
- You blocked the bot
- **Fix:** Unblock it in Telegram settings

### **No error but no message**
- Check you're using correct Telegram account
- Try sending message to bot first
- Then get updates again

---

## ✅ QUICK TEST:

After updating config:

```python
# Test just Telegram
python -c "
from alerts.telegram_notifier import TelegramNotifier
from config.config import *

config = {
    'TELEGRAM_ENABLED': True,
    'TELEGRAM_CONFIG': TELEGRAM_CONFIG
}

bot = TelegramNotifier(config)
result = bot.send_test_message()
print('✅ Success!' if result else '❌ Failed')
"
```

Should send test message to your phone!

---

## 📝 EXAMPLE WORKING CONFIG:

```python
TELEGRAM_ENABLED = True
TELEGRAM_CONFIG = {
    "bot_token": "6789012345:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw",  # Example (yours will be different)
    "chat_id": "987654321",  # Your chat ID (no quotes on number, but config needs string)
}
```

---

## 🎯 CHECKLIST:

- [ ] Created bot with @BotFather
- [ ] Copied bot token
- [ ] **Opened bot and pressed START**
- [ ] Sent a message to bot
- [ ] Got chat ID (from @userinfobot or API)
- [ ] Updated config.py with both values
- [ ] Ran: `python main.py --test`
- [ ] Received test message on phone

**Once all checked, Telegram will work!** ✅
