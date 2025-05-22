import subprocess
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(BASE_DIR, 'venv', 'bin', 'python')

scripts = {
    "ETH": os.path.join(BASE_DIR, "binance_bot_eth", "run_until_ok.py"),
    "DOGE": os.path.join(BASE_DIR, "binance_bot_doge", "run_until_ok.py"),
    "TELEGRAM": os.path.join(BASE_DIR, "telegram_bot.py")
}

logs_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)

for name, path in scripts.items():
    log_file = os.path.join(logs_dir, f"{name.lower()}_log.txt")
    with open(log_file, "w") as log:
        print(f"🚀 Запускаю {name} бота за шляхом: {path}")
        print(f"➡️ Команда: {[VENV_PYTHON, path]}")
        subprocess.Popen([VENV_PYTHON, path], stdout=log, stderr=log)

print("✅ Усі боти запущено у фоні.")