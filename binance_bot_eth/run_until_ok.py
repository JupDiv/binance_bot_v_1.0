import subprocess
import time

MAX_RETRIES = 1000  # Максимальна кількість спроб
DELAY_SECONDS = 15  # Затримка між спробами в секундах

for attempt in range(1, MAX_RETRIES + 1):
    print(f"🔁 Спроба запуску #{attempt}")
    try:
        result = subprocess.run(["python", "bot.py"], check=True, cwd="binance_bot_eth")
        print("✅ Бот завершився без помилок.")
        break
    except subprocess.CalledProcessError as e:
        print(f"❌ Помилка запуску: {e}. Пробуємо знову через {DELAY_SECONDS} сек...")
        time.sleep(DELAY_SECONDS)