from datetime import datetime

def log_trade(action, symbol, qty, price):
    with open("logs/trades.log", "a") as f:
        f.write(f"{datetime.now()} | {action} {symbol} | qty={qty} | price={price}\n")

def percent_change(old, new):
    return ((new - old) / old) * 100