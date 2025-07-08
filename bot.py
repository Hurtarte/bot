from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from binance.client import Client
from config import BINANCE_API_KEY, BINANCE_API_SECRET, TELEGRAM_BOT_TOKEN

# Binance Futures client
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
client.FUTURES_URL = 'https://testnet.binancefuture.com'
#client.FUTURES_URL = 'https://fapi.binance.com'

# Telegram command: /buy BTCUSDT 0.001
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = context.args[0].upper()
        quantity = float(context.args[1])
        order = client.futures_create_order(
            symbol=symbol,
            side='BUY',
            type='MARKET',
            quantity=quantity
        )
        await update.message.reply_text(f"Buy order placed: {order['orderId']}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Telegram command: /sell BTCUSDT 0.001
async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = context.args[0].upper()
        quantity = float(context.args[1])
        order = client.futures_create_order(
            symbol=symbol,
            side='SELL',
            type='MARKET',
            quantity=quantity
        )
        await update.message.reply_text(f"Sell order placed: {order['orderId']}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Telegram Bot initialization
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("buy", buy))
app.add_handler(CommandHandler("sell", sell))

if __name__ == "__main__":
    app.run()
