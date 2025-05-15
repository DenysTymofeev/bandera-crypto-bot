from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import ccxt
import pandas as pd
import time

# ВСТАВЬ СЮДА СВОЙ ТОКЕН
TOKEN = "7671481125:AAGXfUMmnqxejJO_qKVtgPXp_yJSo57-E2Q"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот работает. Напиши /pairs")

async def pairs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Секунду, ищу пары...")

    exchange = ccxt.bybit({'options': {'defaultType': 'future'}})
    markets = exchange.load_markets()
    usdt_pairs = [s for s in markets if s.endswith('/USDT')]
    symbols = usdt_pairs[:50]

    def get_closes(symbol):
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=500)
            return [c[4] for c in ohlcv]
        except:
            return None

    data = {}
    for symbol in symbols:
        closes = get_closes(symbol)
        if closes and len(closes) == 500:
            data[symbol] = closes
        time.sleep(1.2)

    df = pd.DataFrame(data)
    corr = df.corr()
    result = []

    for i in range(len(corr.columns)):
        for j in range(i + 1, len(corr.columns)):
            a = corr.columns[i]
            b = corr.columns[j]
            val = corr.loc[a, b]
            if abs(val) < 0.3:
                if a == "USDC/USDT":
                    result.append((b, a, round(val, 3)))
                elif b == "USDC/USDT":
                    result.append((a, b, round(val, 3)))
                else:
                    result.append((a, b, round(val, 3)))

    if result:
        text = "🧊 Пары с корреляцией ниже 0.3:\n\n"
        for a, b, c in result:
            text += f"{a} — {b} : {c}\n"
        await update.message.reply_text(text[:4096])
    else:
        await update.message.reply_text("Не нашёл таких пар.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("pairs", pairs))

print("Бот запущен. Пиши ему в Telegram.")
app.run_polling()
