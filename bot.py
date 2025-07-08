from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from binance.client import Client
from config import BINANCE_API_KEY, BINANCE_API_SECRET, TELEGRAM_BOT_TOKEN

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
client.FUTURES_URL = 'https://testnet.binancefuture.com'

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = context.args[0].upper()
        quantity = float(context.args[1])
        leverage = int(context.args[2]) if len(context.args) > 2 else 20  # Default 20x

        # Set leverage
        client.futures_change_leverage(symbol=symbol, leverage=leverage)

        order = client.futures_create_order(
            symbol=symbol,
            side='BUY',
            type='MARKET',
            quantity=quantity
        )
        await update.message.reply_text(
            f"✅ Buy order placed: {order['orderId']}\n🔧 Leverage: {leverage}x"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error placing buy order: {e}")

async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = context.args[0].upper()
        quantity = float(context.args[1])
        leverage = int(context.args[2]) if len(context.args) > 2 else 20  # Default 20x

        # Set leverage
        client.futures_change_leverage(symbol=symbol, leverage=leverage)

        order = client.futures_create_order(
            symbol=symbol,
            side='SELL',
            type='MARKET',
            quantity=quantity
        )
        await update.message.reply_text(
            f"✅ Sell order placed: {order['orderId']}\n🔧 Leverage: {leverage}x"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error placing sell order: {e}")

# Optional /leverage command still available if you want to set it manually
async def leverage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = context.args[0].upper()
        lev = int(context.args[1])
        response = client.futures_change_leverage(symbol=symbol, leverage=lev)
        await update.message.reply_text(f"⚙️ Leverage for {symbol} set to {response['leverage']}x")
    except Exception as e:
        await update.message.reply_text(f"❌ Error setting leverage: {e}")

# Bot setup
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("buy", buy))
app.add_handler(CommandHandler("sell", sell))
app.add_handler(CommandHandler("leverage", leverage))

if __name__ == "__main__":
    app.run_polling()
