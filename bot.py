import os
from binance.client import Client
from binance.enums import *
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from binance.enums import ORDER_TYPE_TAKE_PROFIT_LIMIT

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

client = Client(API_KEY, API_SECRET)
client.FUTURES_URL = "https://testnet.binancefuture.com/fapi"

SYMBOL = "BTCUSDT"
QUANTITY = 0.001  # Adjust this

# TP/SL prices (example values, you can adjust or make dynamic)
TP_PERCENT = 0.7  # 70% profit target
SL_PERCENT = 0.005  # 0.5% stop loss

def get_price():
    """Get current mark price"""
    ticker = client.futures_mark_price(symbol=SYMBOL)
    return float(ticker["markPrice"])

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

    # Calculate TP and SL prices depending on side
    if side == "long":
        tp_price = round(current_price * (1 + TP_PERCENT), 2)
        sl_price = round(current_price * (1 - SL_PERCENT), 2)
        tp_side = SIDE_SELL
        sl_side = SIDE_SELL
        position_side = "LONG"
    else:  # short
        tp_price = round(current_price * (1 - TP_PERCENT), 2)
        sl_price = round(current_price * (1 + SL_PERCENT), 2)
        tp_side = SIDE_BUY
        sl_side = SIDE_BUY
        position_side = "SHORT"

    # Place Take Profit order (STOP_MARKET with price)
    tp_order = client.futures_create_order(
        symbol=SYMBOL,
        side=tp_side,
        type=ORDER_TYPE_TAKE_PROFIT_LIMIT,
        quantity=QUANTITY,
        stopPrice=tp_price,
        closePosition=True,
        reduceOnly=True
    )

    # Place Stop Loss order (STOP_MARKET)
    sl_order = client.futures_create_order(
        symbol=SYMBOL,
        side=sl_side,
        type=ORDER_TYPE_STOP_MARKET,
        quantity=QUANTITY,
        stopPrice=sl_price,
        closePosition=True,
        reduceOnly=True
    )

    await update.message.reply_text(
        f"{position_side} order placed!\n"
        f"Entry Price: {current_price}\n"
        f"Take Profit: {tp_price}\n"
        f"Stop Loss: {sl_price}\n"
        f"Order ID: {order['orderId']}"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is live. Use /long or /short to trade with TP/SL.")

async def long_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ You've opened a LONG position.")
    await place_orders(update, context, "long")

async def short_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ You've opened a SHORT position.")
    await place_orders(update, context, "short")

async def close_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return

    # Get current position info
    positions = client.futures_position_information(symbol=SYMBOL)
    position_data = next(p for p in positions if p["symbol"] == SYMBOL)
    position_amt = float(position_data["positionAmt"])

    if position_amt == 0:
        await update.message.reply_text("No open position to close.")
        return

    side = SIDE_SELL if position_amt > 0 else SIDE_BUY
    quantity = abs(position_amt)

    # Send market close order
    close_order = client.futures_create_order(
        symbol=SYMBOL,
        side=side,
        type=ORDER_TYPE_MARKET,
        quantity=quantity,
        reduceOnly=True
    )

    await update.message.reply_text(
        f"Position closed.\nSide: {'LONG' if position_amt > 0 else 'SHORT'}\nQuantity: {quantity}\nOrder ID: {close_order['orderId']}"
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("long", long_command))
    app.add_handler(CommandHandler("short", short_command))
    app.add_handler(CommandHandler("close", close_position))
    app.run_polling()
