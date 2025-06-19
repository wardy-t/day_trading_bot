import time
import logging
from core.vwap_signal_generator import generate_vwap_bounce_signal
from core.execution_engine import process_signal

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ------------------------
# STEP 1: Define symbols
# ------------------------
symbols = ["AAPL", "MSFT", "TSLA", "NVDA", "AMD",
    "GOOGL", "META", "AMZN", "NFLX", "INTC",
    "CRM", "SHOP", "BABA", "NKE", "UBER",
    "DIS", "PYPL", "QCOM", "MU", "F"
    ]  # You can add more manually for now

# -----------------------------
# STEP 2: Scanning loop
# -----------------------------

SCAN_INTERVAL = 60  # seconds (adjust for frequency)
logger.info("Starting VWAP bounce scanner...")

try:
    while True:
        for symbol in symbols:
            signal = generate_vwap_bounce_signal(symbol)
            if signal:
                process_signal(signal)
        logger.info(f"Sleeping for {SCAN_INTERVAL} seconds...")
        time.sleep(SCAN_INTERVAL)

except KeyboardInterrupt:
    logger.info("Scanner manually stopped.")
except Exception as e:
    logger.exception(f"Unexpected error in scanner: {e}")