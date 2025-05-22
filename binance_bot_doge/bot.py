import time
from datetime import datetime, timedelta
from config import *
from binance_api import get_current_price, buy_market, sell_market, get_balance
from utils import percent_change, log_trade

# --- Load last buy from logs/trades.log
def load_last_buy():
    try:
        with open("logs/trades.log", "r") as f:
            lines = f.readlines()
            for line in reversed(lines):
                if "BUY DOGEUSDT" in line:
                    parts = line.strip().split("|")
                    price = float(parts[-1].split("=")[-1])
                    print(f"🔁 Відновлено останню покупку: {price}")
                    return price
    except:
        pass
    return None

print("📈 Binance Bot запущено")

last_buy_price = load_last_buy()
has_position = last_buy_price is not None
last_buy_time = None

while True:
    time.sleep(INTERVAL_SECONDS)
    current_price = get_current_price(SYMBOL)
    print(f"💰 Поточна ціна {SYMBOL}: {current_price}")

    usdt = get_balance('USDT')
    print(f"💵 Поточний баланс USDT: {usdt}")
    coin = SYMBOL.replace('USDT', '')
    asset_qty = get_balance(coin)

    # Якщо є позиція — перевіряємо на прибуток або збиток
    if has_position:
        change = percent_change(last_buy_price, current_price)
        estimated_profit = (asset_qty * current_price) - (asset_qty * last_buy_price)

        print(f"📊 Зміна після купівлі: {change:.2f}% | Приблизний результат: {estimated_profit:.4f} USDT")

        # Продати при прибутку
        if change >= PROFIT_THRESHOLD_PERCENT:
            print("✅ Досягнуто цілі по прибутку. Продаємо.")
            result = sell_market(SYMBOL, asset_qty)
            log_trade("SELL (profit)", SYMBOL, asset_qty, current_price)
            has_position = False

        # Продати при стоп-лоссі
        elif change <= -2.5:
            print("🛑 Спрацював стоп-лосс. Продаємо.")
            result = sell_market(SYMBOL, asset_qty)
            log_trade("SELL (stoploss)", SYMBOL, asset_qty, current_price)
            has_position = False

        else:
            print("⏳ Очікуємо кращого моменту...")

    # Якщо немає позиції — чекаємо просадки
    else:
        ref_price = current_price * (1 + (MIN_CHANGE_PERCENT / 100))
        print(f"🔎 Референсна ціна для купівлі: {ref_price}")

        if (
            current_price <= ref_price and
            usdt >= TRADE_AMOUNT_USDT and
            (last_buy_time is None or datetime.now() - last_buy_time >= timedelta(hours=1))
        ):
            print(f"🟢 Купуємо {coin}...")
            result = buy_market(SYMBOL, TRADE_AMOUNT_USDT)
            last_buy_price = current_price
            log_trade("BUY", SYMBOL, result.get("executedQty", 0), current_price)
            has_position = True
            last_buy_time = datetime.now()
        else:
            print("📉 Умови для купівлі не виконані або ще не минула година.")