

import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from binance_bot_eth.binance_api import get_balance, get_current_price, sell_market
from binance_bot_eth.config import SYMBOL

# Додай TELEGRAM_TOKEN у .env
TOKEN = os.getenv("TELEGRAM_TOKEN")  
# Щоб ніхто сторонній не керував
ALLOWED_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))  

coin = SYMBOL.replace("USDT", "")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    usdt = get_balance("USDT")
    asset = get_balance(coin)
    await update.message.reply_text(f"💵 USDT: {usdt}\n🪙 {coin}: {asset}")

async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    qty = get_balance(coin)
    if qty > 0:
        result = sell_market(SYMBOL, qty)
        await update.message.reply_text(f"✅ Продано {qty} {coin} за {get_current_price(SYMBOL)} USDT")
    else:
        await update.message.reply_text("❌ Недостатньо балансу для продажу")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    price = get_current_price(SYMBOL)
    await update.message.reply_text(f"📈 Поточна ціна {SYMBOL}: {price}")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("sell", sell))
    app.add_handler(CommandHandler("status", status))

    print("🤖 Telegram бот запущено")
    await app.run_polling()

if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())