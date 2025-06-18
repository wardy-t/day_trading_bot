from core.broker_interface import connect, get_account

if connect():
    account = get_account()
    print("✅ Connected to Alpaca.")
    print("Account ID:", account.account_number)
    print("Equity:", account.equity)
    print("Buying Power:", account.buying_power)
else:
    print("❌ Connection failed.")