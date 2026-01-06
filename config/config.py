# ═══════════════════════════════════════════════════════════════════════════════
# MARKET SCANNER CONFIGURATION - ALL BROKERS WORKING
# Just change MT5_BROKER line to switch brokers!
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# ACTIVE BROKER - CHANGE THIS LINE TO SWITCH BROKERS!
# ═══════════════════════════════════════════════════════════════════════════════

MT5_ENABLED = True
MT5_BROKER = "ICMarkets"  # ← CHANGE THIS: "Exness", "ICMarkets", "Deriv", "OctaFX", "AvaTrade"

# ═══════════════════════════════════════════════════════════════════════════════
# BROKER CREDENTIALS
# ═══════════════════════════════════════════════════════════════════════════════

MT5_CONFIG = {
    "Exness": {
        "login": 172512161,
        "password": "2103@Faith",  # YOUR PASSWORD
        "server": "Exness-MT5Real2",
        "timeout": 60000,
        "portable": False
    },
    "ICMarkets": {
        "login": 11583834,
        "password": "2103@Faith",  # YOUR PASSWORD
        "server": "ICMarketsSC-MT5-4",
        "timeout": 60000,
        "portable": True
    },
    "Deriv": {
        "login": 21819122,
        "password": "2103@Faith",  # YOUR PASSWORD
        "server": "DerivVU-Server",
        "timeout": 60000,
        "portable": False
    },
    "OctaFX": {
        "login": 12345678,
        "password": "YourPassword123",  # YOUR PASSWORD
        "server": "OctaFX-Real",
        "timeout": 60000,
        "portable": False
    },
    "AvaTrade": {
        "login": 95077701,
        "password": "2103@Faith",  # YOUR PASSWORD
        "server": "AvaTradeMarkets-Real 1-MT5",
        "timeout": 60000,
        "portable": False
    }
}

YAHOO_FINANCE_ENABLED = False

# ═══════════════════════════════════════════════════════════════════════════════
# SYMBOL NAMES BY BROKER (AUTO-SELECTED BASED ON MT5_BROKER)
# ═══════════════════════════════════════════════════════════════════════════════

BROKER_SYMBOLS = {
    "Exness": {
        # Exness adds "m" suffix
        "TRENDING": ["XAUUSDm", "XAGUSDm", "USOILm", "XNGUSDm", "US500m", "USTECm", "US30m", "BTCUSDm"],
        "RANGING": ["EURUSDm", "EURGBPm", "USDCHFm", "USDJPY"],
        "MIXED": ["GBPUSDm", "AUDUSDm", "USDCADm", "NZDUSDm"]
    },
    "ICMarkets": {
        # IC Markets standard names
        "TRENDING": ["XAUUSD", "XAGUSD", "USOIL", "NATGAS", "US500", "USTEC", "US30"],
        "RANGING": ["EURUSD", "EURGBP", "USDCHF", "USDJPY"],
        "MIXED": ["GBPUSD", "AUDUSD", "USDCAD", "NZDUSD"]
    },
    "Deriv": {
        # Deriv standard names
        "TRENDING": ["XAUUSD", "XAGUSD", "USOIL", "US500", "USTEC", "US30", "BTCUSD"],
        "RANGING": ["EURUSD", "EURGBP", "USDCHF"],
        "MIXED": ["GBPUSD", "AUDUSD", "USDCAD", "NZDUSD"]
    },
    "OctaFX": {
        # OctaFX standard names
        "TRENDING": ["XAUUSD", "XAGUSD", "USOIL", "NATGAS", "US500", "NAS100", "US30"],
        "RANGING": ["EURUSD", "EURGBP", "USDCHF", "USDJPY"],
        "MIXED": ["GBPUSD", "AUDUSD", "USDCAD", "NZDUSD"]
    },
    "AvaTrade": {
        # AvaTrade clean names
        "TRENDING": ["XAUUSD", "XAGUSD", "USOIL", "NATGAS", "SPX500", "NAS100", "US30", "BTCUSD"],
        "RANGING": ["EURUSD", "EURGBP", "USDCHF"],
        "MIXED": ["GBPUSD", "AUDUSD", "USDCAD", "NZDUSD"]
    }
}

# Auto-select symbols for active broker
_broker_config = BROKER_SYMBOLS.get(MT5_BROKER, BROKER_SYMBOLS["Exness"])
TRENDING_PAIRS = _broker_config["TRENDING"]
RANGING_PAIRS = _broker_config["RANGING"]
MIXED_PAIRS = _broker_config["MIXED"]
ALL_PAIRS = TRENDING_PAIRS + RANGING_PAIRS + MIXED_PAIRS

# Symbol mapping for Yahoo Finance fallback
SYMBOL_MAP = {
    "XAUUSD": "GC=F", "XAUUSDm": "GC=F",
    "XAGUSD": "SI=F", "XAGUSDm": "SI=F",
    "USOIL": "CL=F", "USOILm": "CL=F",
    "NATGAS": "NG=F", "XNGUSDm": "NG=F",
    "EURUSD": "EURUSD=X", "EURUSDm": "EURUSD=X",
    "GBPUSD": "GBPUSD=X", "GBPUSDm": "GBPUSD=X",
    "USDJPY": "USDJPY=X", "USDJPYm": "USDJPY=X",
    "AUDUSD": "AUDUSD=X", "AUDUSDm": "AUDUSD=X",
    "USDCAD": "USDCAD=X", "USDCADm": "USDCAD=X",
    "USDCHF": "USDCHF=X", "USDCHFm": "USDCHF=X",
    "NZDUSD": "NZDUSD=X", "NZDUSDm": "NZDUSD=X",
    "EURGBP": "EURGBP=X", "EURGBPm": "EURGBP=X",
    "US500": "^GSPC", "US500m": "^GSPC", "SPX500": "^GSPC",
    "NAS100": "^IXIC", "USTEC": "^IXIC", "USTECm": "^IXIC",
    "US30": "^DJI", "US30m": "^DJI",
    "BTCUSD": "BTC-USD", "BTCUSDm": "BTC-USD",
}

# ═══════════════════════════════════════════════════════════════════════════════
# TIMEFRAMES
# ═══════════════════════════════════════════════════════════════════════════════

PRIMARY_TIMEFRAME = "1H"
HTF_TIMEFRAMES = ["W1", "D1", "H4"]
LTF_TIMEFRAME = "M15"

# ═══════════════════════════════════════════════════════════════════════════════
# SCANNING SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

SCAN_INTERVAL_MINUTES = 60
AUTO_SCAN_ENABLED = True
FORCE_SCAN_KEY = "F5"
LOOKBACK_BARS = 1000

# ═══════════════════════════════════════════════════════════════════════════════
# RISK MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

ACCOUNT_SIZE = 10000
RISK_PER_TRADE = 1.0

ATR_MULTIPLIERS = {
    "TRENDING": {"stop": 3.0, "trail": 2.5, "target": 10.0},
    "RANGING": {"stop": 1.75, "trail": 1.25, "target": 5.0},
    "MIXED": {"stop": 2.25, "trail": 1.75, "target": 7.0}
}

MOVE_TO_BE_AT_R = 2.0
START_TRAIL_AT_R = 3.0

# ═══════════════════════════════════════════════════════════════════════════════
# PROBABILITY THRESHOLDS
# ═══════════════════════════════════════════════════════════════════════════════

PROB_GET_READY = 60
PROB_ALMOST_READY = 70
PROB_BIG_BANG = 80
MIN_TIME_AT_LEVEL = 10
MIN_HTF_MOMENTUM = 70

# ═══════════════════════════════════════════════════════════════════════════════
# ALERT SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

EMAIL_ENABLED = True
EMAIL_CONFIG = {
    "smtp_server": "mail.adekay.com",
    "smtp_port": 465,
    "sender_email": "emma@adekay.com",
    "sender_password": "2103@Faith",  # YOUR PASSWORD
    "recipient_email": "adekolagafat@gmail.com",
    "use_ssl": True,
}

TELEGRAM_ENABLED = True
TELEGRAM_CONFIG = {
    "bot_token": "8553277592:AAHWSdeJPt0KFnQJFjGTZIkxNwlSQF1EsWg",
    "chat_id": "6984434604",
}

DESKTOP_ALERTS_ENABLED = True

SOUND_ALERTS_ENABLED = False
SOUND_CONFIG = {
    "get_ready_sound": "sounds/get_ready.mp3",
    "almost_ready_sound": "sounds/almost_ready.mp3",
    "big_bang_sound": "sounds/big_bang.mp3",
    "volume": 0.8
}

ALERT_COOLDOWN_MINUTES = 60

# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

HTML_OUTPUT_PATH = "dashboard.html"
HTML_AUTO_REFRESH = True
HTML_REFRESH_SECONDS = 300
DEFAULT_SORT_BY = "probability"
DEFAULT_SORT_ORDER = "desc"
SHOW_ONLY_ACTIVE = False

# ═══════════════════════════════════════════════════════════════════════════════
# ADVANCED SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

CLASSIFICATION_METHOD = "MANUAL"
AUTO_CLASSIFICATION_THRESHOLDS = {
    "TRENDING": {"min_weekly_adx": 30, "min_range_pct": 12.0},
    "RANGING": {"max_weekly_adx": 22, "max_range_pct": 6.0}
}

HISTORICAL_TRACKING_ENABLED = False
DATABASE_PATH = "database/scanner_history.db"
MAX_HISTORY_PER_PAIR = 50

LOG_LEVEL = "INFO"
LOG_TO_FILE = True
LOG_FILE_PATH = "logs/scanner.log"

MURREY_FRAME = 64
MURREY_MULTIPLIER = 1.5
MURREY_IGNORE_WICKS = True
VOLUME_SPIKE_THRESHOLD = 1.5
SPRING_MAX_BARS = 3
USE_MULTIPROCESSING = False
MAX_WORKERS = 4
CACHE_ENABLED = False
CACHE_EXPIRY_MINUTES = 15
TIMEZONE = "UTC"

# ═══════════════════════════════════════════════════════════════════════════════
# SHOW CONFIGURATION ON IMPORT
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n{'='*80}")
print(f"ACTIVE BROKER: {MT5_BROKER}")
print(f"{'='*80}")
print(f"Pairs to scan: {len(ALL_PAIRS)}")
for i, pair in enumerate(ALL_PAIRS, 1):
    print(f"  {i}. {pair}")
print(f"{'='*80}\n")
