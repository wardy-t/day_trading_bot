from core.broker_interface import connect, get_account
from core.execution_engine import process_signal

if connect():
    account = get_account()
    print("✅ Connected to Alpaca.")
    print("Account ID:", account.account_number)
    print("Equity:", account.equity)
    print("Buying Power:", account.buying_power)
else:
    print("❌ Connection failed.")


if connect():
    # -------------------------------
    # TEST SIGNAL — adjust as needed
    # -------------------------------
    signal = {
        "symbol": "AAPL",
        "side": "buy",
        "confidence": 0.85,            # Optional but included
        "stop_loss": 169.00,           # Set this below current price
        "setup_tag": "VWAP Bounce"
    }

    process_signal(signal)
else:
    print("❌ Connection to Alpaca failed.")