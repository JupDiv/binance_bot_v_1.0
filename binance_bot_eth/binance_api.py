import time, hmac, hashlib, requests, urllib.parse, os
from dotenv import load_dotenv
load_dotenv()


API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")


BASE_URL = 'https://api.binance.com'

# Отримати мінімальну кількість (LOT_SIZE) для пари
def get_lot_size(symbol):
    exchange_info = requests.get(f'{BASE_URL}/api/v3/exchangeInfo?symbol={symbol}').json()
    filters = exchange_info['symbols'][0]['filters']
    for f in filters:
        if f['filterType'] == 'LOT_SIZE':
            print(f"🔎 LOT_SIZE для {symbol}: minQty={f['minQty']}, stepSize={f['stepSize']}")
            return f
    return None

# Підпис запиту
def create_signature(query_string):
    return hmac.new(API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

# GET/POST/DELETE запити

def signed_request(method, path, params=None):
    if params is None:
        params = {}
    params['timestamp'] = int(time.time() * 1000)
    query_string = urllib.parse.urlencode(params)
    signature = create_signature(query_string)
    headers = {'X-MBX-APIKEY': API_KEY}
    url = f"{BASE_URL}{path}?{query_string}&signature={signature}"
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            print(f"❌ Невідомий метод запиту: {method}")
            return {"error": "Unknown method"}

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"❌ Помилка HTTP-запиту ({method} {path}):", e)
        if response := getattr(e, 'response', None):
            try:
                return response.json()
            except Exception:
                return {"error": "Неможливо розпарсити відповідь"}
        return {"error": "Невідома помилка запиту"}

# Публічна ціна

def get_current_price(symbol):
    r = requests.get(f'{BASE_URL}/api/v3/ticker/price?symbol={symbol}')
    return float(r.json()['price'])

# Ордери

FEE_RATE = 0.001

def buy_market(symbol, amount_usdt):
    price = get_current_price(symbol)
    lot_filter = get_lot_size(symbol)
    min_qty = float(lot_filter['minQty'])
    step_size = float(lot_filter['stepSize'])

    raw_qty = (amount_usdt / price) * (1 - FEE_RATE)
    steps = int(raw_qty / step_size)
    qty = max(round(steps * step_size, 8), min_qty)

    print(f"🧾 Формуємо ордер на купівлю: qty={qty}, min={min_qty}, step={step_size}, raw={raw_qty}")

    return signed_request('POST', '/api/v3/order', {
        'symbol': symbol,
        'side': 'BUY',
        'type': 'MARKET',
        'quantity': qty
    })

def sell_market(symbol, quantity):
    lot_filter = get_lot_size(symbol)
    min_qty = float(lot_filter['minQty'])
    step_size = float(lot_filter['stepSize'])
    steps = int(quantity / step_size)
    qty = max(round(steps * step_size, 8), min_qty)
    return signed_request('POST', '/api/v3/order', {
        'symbol': symbol,
        'side': 'SELL',
        'type': 'MARKET',
        'quantity': qty
    })

def get_balance(asset):
    response = signed_request('GET', '/api/v3/account')
    print("🔍 Відповідь від Binance на /account:", response)
    if 'balances' not in response:
        print("❌ balances не знайдено! Можлива помилка:", response.get("msg", ""))
        return 0.0
    balances = response['balances']
    return float(next((b for b in balances if b['asset'] == asset), {'free': 0})['free'])

if __name__ == '__main__':
    get_lot_size('BTCUSDT')