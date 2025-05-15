import ccxt
import pandas as pd
import time

# Подключение к Bybit фьючерсы
exchange = ccxt.bybit({'options': {'defaultType': 'future'}})

# Загружаем рынки
markets = exchange.load_markets()
usdt_pairs = [s for s in markets if s.endswith('/USDT')]

# Берём 50 пар (или сколько нужно — можешь изменить)
symbols = usdt_pairs[:50]

# Скачиваем исторические цены
def get_closes(symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=500)
        closes = [candle[4] for candle in ohlcv]  # close
        return closes
    except Exception as e:
        print(f"{symbol} — ошибка: {e}")
        return None

# Собираем данные
data = {}
for symbol in symbols:
    print(f"Загружаю {symbol}...")
    closes = get_closes(symbol)
    if closes and len(closes) == 500:
        data[symbol] = closes
    time.sleep(1.2)  # пауза чтобы не отрубили API

# Строим таблицу
df = pd.DataFrame(data)
print("\n🎯 Таблица закрытий сформирована:")
print(df.tail())

# Расчёт корреляции
corr = df.corr(method='pearson')

# Поиск низкокоррелированных пар
low_corr_pairs = []

symbols = corr.columns
for i in range(len(symbols)):
    for j in range(i + 1, len(symbols)):
        a = symbols[i]
        b = symbols[j]
        val = corr.loc[a, b]
        if abs(val) < 0.3:
            low_corr_pairs.append((a, b, round(val, 3)))

# Вывод
print("\n🧊 Пары с низкой корреляцией (|corr| < 0.3):")
for a, b, c in sorted(low_corr_pairs, key=lambda x: abs(x[2])):
    print(f"{a} — {b} : {c}")