import os
from binance.client import Client
from binance.enums import *
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

# Binance client setup
client = Client(API_KEY, API_SECRET)
client.FUTURES_URL = "https://testnet.binancefuture.com/fapi"

# Bot configuration
SYMBOL = "BTCUSDT"
QUANTITY = 0.001  # Adjust based on your test account
TP_PERCENT = 0.01  # 1% take profit
SL_PERCENT = 0.005  # 0.5% stop loss

# Get current market price
def get_price():
    ticker = client.futures_mark_price(symbol=SYMBOL)
    return float(ticker["markPrice"])

# Place long/short orders with TP and SL
async def place_orders(update: Update, context: ContextTypes.DEFAULT_TYPE, side: str):
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return

    current_price = get_price()

    # Place main market order
    order = client.futures_create_order(
        symbol=SYMBOL,
        side=SIDE_BUY if side == "long" else SIDE_SELL,
        type=ORDER_TYPE_MARKET,
        quantity=QUANTITY
    )

    order_id = order['orderId']

    # Determine TP and SL
    if side == "long":
        tp_price = round(current_price * (1 + TP_PERCENT), 2)
        sl_price = round(current_price * (1 - SL_PERCENT), 2)
        tp_side = SIDE_SELL
        sl_side = SIDE_SELL
        position_side = "LONG"
    else:
        tp_price = round(current_price * (1 - TP_PERCENT), 2)
        sl_price = round(current_price * (1 + SL_PERCENT), 2)
        tp_side = SIDE_BUY
        sl_side = SIDE_BUY
        position_side = "SHORT"

    # Take Profit
    client.futures_create_order(
        symbol=SYMBOL,
        side=tp_side,
        type=ORDER_TYPE_TAKE_PROFIT_MARKET,
        quantity=QUANTITY,
        stopPrice=tp_price,
        closePosition=True,
        reduceOnly=True
    )

    # Stop Loss
    client.futures_create_order(
        symbol=SYMBOL,
        side=sl_side,
        type=ORDER_TYPE_STOP_MARKET,
        quantity=QUANTITY,
        stopPrice=sl_price,
        closePosition=True,
        reduceOnly=True
    )

    # Confirmation message
    await update.message.reply_text(
        f"{position_side} order placed!\n"
        f"Order ID: {order_id}\n"
        f"Entry Price: {current_price}\n"
        f"Take Profit at: {tp_price}\n"
        f"Stop Loss at: {sl_price}"
    )

# Handle /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot is live. Use /long or /short to trade with TP/SL. Use /close to close any open position.")

# Handle /long
async def long_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ You've opened a LONG position.")
    await place_orders(update, context, "long")

# Handle /short
async def short_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ You've opened a SHORT position.")
    await place_orders(update, context, "short")

# Handle /close
async def close_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return

    positions = client.futures_position_information(symbol=SYMBOL)
    position_data = next(p for p in positions if p["symbol"] == SYMBOL)
    position_amt = float(position_data["positionAmt"])

    if position_amt == 0:
        await update.message.reply_text("❌ No open position to close.")
        return

    side = SIDE_SELL if position_amt > 0 else SIDE_BUY
    quantity = abs(position_amt)

    # Close with market order
    close_order = client.futures_create_order(
        symbol=SYMBOL,
        side=side,
        type=ORDER_TYPE_MARKET,
        quantity=quantity,
        reduceOnly=True
    )

    await update.message.reply_text(
        f"✅ Closed position: {'LONG' if position_amt > 0 else 'SHORT'}\n"
        f"Quantity: {quantity}\n"
        f"Order ID: {close_order['orderId']}"
    )

# Start bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("long", long_command))
    app.add_handler(CommandHandler("short", short_command))
    app.add_handler(CommandHandler("close", close_position))
    app.run_polling()
