import time
import datetime
import pytz
import logging
from alpaca_trade_api.rest import REST, TimeFrame
from core.utils import calculate_vwap, calculate_rsi
from core.broker_interface import api

logger = logging.getLogger(__name__)

MARKET_TZ = pytz.timezone("America/New_York")
START_TIME = datetime.time(hour=9, minute=45)
END_TIME = datetime.time(hour=11, minute=30)

def is_market_open_now():
    now = datetime.datetime.now(MARKET_TZ).time()
    return START_TIME <= now <= END_TIME

def generate_vwap_bounce_signal(symbol: str, max_retries: int = 3):
    if not is_market_open_now():
        logger.info("Outside preferred VWAP bounce window")
        return None

    for attempt in range(1, max_retries + 1):
        try:
            bars = api.get_bars(symbol, TimeFrame.Minute, limit=50, feed='iex').df
            if bars.empty:
                logger.warning(f"No bar data for {symbol}")
                return None

            # Fix: Reset index to expose 'timestamp' as a column
            bars.reset_index(inplace=True)
            bars.set_index('timestamp', inplace=True)
            bars.sort_index(inplace=True)

            price = bars['close'].iloc[-1]
            vwap = calculate_vwap(bars)
            rsi = calculate_rsi(bars['close'])
            volume = bars['volume'].iloc[-1]
            avg_volume = bars['volume'].rolling(10).mean().iloc[-1]

            if price > vwap and bars['low'].iloc[-2] < vwap < bars['close'].iloc[-1]:
                if rsi < 45 and volume > avg_volume:
                    stop_loss = round(vwap * 0.995, 2)
                    risk_per_share = abs(price - stop_loss)
                    take_profit = round(price + (1.5 * risk_per_share), 2)

                    signal = {
                        "symbol": symbol,
                        "side": "buy",
                        "stop_loss": stop_loss,
                        "take_profit": take_profit,
                        "confidence": 0.85,
                        "setup_tag": "VWAP Bounce"
                    }
                    logger.info(f"Generated VWAP bounce signal: {signal}")
                    return signal

            return None  # No signal condition met

        except Exception as e:
            logger.warning(f"[Attempt {attempt}] Error for {symbol}: {e}")
            if attempt < max_retries:
                wait_time = attempt * 2
                logger.info(f"Retrying {symbol} in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed all {max_retries} attempts for {symbol}")

    return None