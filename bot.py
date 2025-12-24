import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from tivara_core import generate_signals

BOT_TOKEN = os.getenv("BOT_TOKEN")

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🤖 تیوارا V3 – هیولا فعال شد\n\n"
        "تحلیل چند تایم‌فریم و Bias واقعی\n"
        "مثال:\n/analyze BTCUSDT"
    )

def analyze(update: Update, context: CallbackContext):
    try:
        symbol = context.args[0].upper()
        r = generate_signals(symbol)

        msg = f"🧠 Tivara V3 – Ultimate Crypto Bot\n\n"
        msg += f"Symbol: {r['symbol']}\nBias: {r['bias']}\nEntry: {r['entry']}\nSL: {r['SL']}\nTP: {r['TP']}\nConfidence: {r['confidence']}\n\n"
        for tf, v in r["timeframes"].items():
            a = v["analysis"]
            msg += f"--- {tf} ---\nTrend: {a['trend']}, RSI: {a['rsi']} ({a['momentum']}), ATR: {a['atr']}, Volume: {a['volume']}\nMarket Structure: {v['market_structure']}\n\n"

        update.message.reply_text(msg)

    except Exception as e:
        update.message.reply_text("❌ دستور اشتباه\nمثال:\n/analyze BTCUSDT")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("analyze", analyze))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
