import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from binance.client import Client
from binance.enums import *

# === CONFIG ===
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEGRAM_USER_ID = 5597787935  # Replace with your own Telegram user ID
BINANCE_API_KEY = '018167649290c65467f1d01a01c86bca35c753200f86e608bee839766027075f'
BINANCE_API_SECRET = '0b4dd75240e85334577ef40102c668cfe542b2ed694975f14e732f6dade8cf36'

# Initialize Binance Testnet Client
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
client.API_URL = client.FUTURES_URL

logging.basicConfig(level=logging.INFO)

# === Function to execute trade ===
async def place_order(symbol, side):
    try:
        # Set leverage
        client.futures_change_leverage(symbol=symbol, leverage=20)

        # Get quantity (hardcoded or calculated based on balance)
        qty = 0.01  # Example: 0.01 BTC

        order = client.futures_create_order(
            symbol=symbol,
            side=SIDE_BUY if side == "buy" else SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=qty
        )
        return f"✅ Order placed: {side.upper()} {qty} {symbol}"
    except Exception as e:
        return f"❌ Error: {e}"

# === Telegram Command Handler ===
async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != TELEGRAM_USER_ID:
        await update.message.reply_text("🚫 Unauthorized")
        return

    if len(context.args) != 2:
        await update.message.reply_text("Usage: /buy BTCUSDT or /sell ETHUSDT")
        return

    command = update.message.text.lower()
    action = command.split()[0][1:]  # 'buy' or 'sell'
    symbol = context.args[1].upper()

    result = await place_order(symbol, action)
    await update.message.reply_text(result)

# === Main Bot Setup ===
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("buy", trade))
    app.add_handler(CommandHandler("sell", trade))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
