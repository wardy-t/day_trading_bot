import time
import logging
from core.vwap_signal_generator import generate_vwap_bounce_signal
from core.execution_engine import process_signal
from core.broker_interface import get_tradable_symbols

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ------------------------
# STEP 1: Define symbols
# ------------------------

USE_ALL_SYMBOLS = False

# Either use all tradable symbols, or a curated top 100
if USE_ALL_SYMBOLS:
    symbols = get_tradable_symbols()
else:
    symbols = [
        "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "GOOG", "TSLA", "BRK.B", "UNH",
        "LLY", "V", "JPM", "XOM", "MA", "AVGO", "JNJ", "PG", "HD", "MRK",
        "COST", "ABBV", "PEP", "ADBE", "KO", "CVX", "CRM", "WMT", "ACN", "MCD",
        "BAC", "TMO", "AMD", "LIN", "ABT", "NFLX", "INTC", "CSCO", "DHR", "CMCSA",
        "PFE", "NKE", "TXN", "VZ", "NEE", "PM", "ORCL", "WFC", "AMGN", "IBM",
        "RTX", "MS", "HON", "BA", "QCOM", "UNP", "MDT", "LOW", "INTU", "SPGI",
        "SCHW", "CAT", "GS", "PLD", "GE", "ISRG", "LMT", "T", "NOW", "AMT",
        "ADI", "GILD", "ELV", "BLK", "ZTS", "SYK", "MO", "MMC", "C", "MDLZ",
        "DE", "ADP", "CI", "CB", "REGN", "USB", "SO", "CL", "VRTX", "PGR",
        "TGT", "AXP", "APD", "BSX", "TJX", "DUK", "BDX", "ETN", "FIS", "PNC",
        "GIS", "HUM", "ICE", "ILMN", "INFO", "ITW", "JKHY", "KLAC", "KMB", "KMI",
        "KSS", "LHX", "LRCX", "LVS", "MAR", "MCHP", "MET", "MGM", "MSCI", "MTB",
        "MU", "MCO", "NAP", "NEM", "NI", "NOC", "NTRS", "ODFL", "OKE", "ORLY",
        "PAYX", "PNR", "PPG", "PSA", "PTON", "PXD", "QRVO", "RHI", "RJF", "ROL",
        "ROP", "RSG", "SBUX", "SIVB", "SNPS", "STT", "SWKS", "SYY", "TRV", "TROW",
        "TT", "TYL", "UDR", "VMC", "WAB", "WBA", "WDC", "WELL", "WMB", "WRB",
        "WU", "WY", "XLNX", "XRAY", "YUM", "ZBRA", "ZBH", "ZION", "AEP", "AES",
        "APTV", "BBY", "BLL", "CAH", "CHD", "CLX", "CMI", "CNP", "CNC", "COTY",
        "CPRT", "CXO", "D", "DAL", "DD", "DFS", "DTE", "ECL", "EMR", "ETR",
        "EW", "EXC", "EXR", "FAST", "FE", "FDX", "FLIR", "GLW", "GWW", "HAL",
        "HCA", "HES", "HLT", "HOLX", "HPE"
    ]

# -----------------------------
# STEP 2: Scanning loop
# -----------------------------

SCAN_INTERVAL = 5  # seconds (adjust for frequency)
logger.info("Starting VWAP bounce scanner...")

try:
    while True:
        for symbol in symbols:
            logger.info(f"Scanning symbol: {symbol}")
            signal = generate_vwap_bounce_signal(symbol)
            if signal:
                process_signal(signal)
        logger.info(f"Sleeping for {SCAN_INTERVAL} seconds...")
        time.sleep(SCAN_INTERVAL)

except KeyboardInterrupt:
    logger.info("Scanner manually stopped.")
except Exception as e:
    logger.exception(f"Unexpected error in scanner: {e}")