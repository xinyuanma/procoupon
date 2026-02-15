"""Main entry point for ProCoupon bot."""
import logging
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import config
from database import init_db, add_coupon, get_valid_coupon_by_brand, add_user

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "Welcome to ProCoupon! 🎟️\n\n"
        "I can help you find coupon codes for your favorite brands.\n"
        "Use /help to see all available commands."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await update.message.reply_text(
        "Available commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/nike - Get Nike coupon code\n\n"
        "More brands coming soon!"
    )


async def nike_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /nike command - returns Nike coupon code."""
    user = update.effective_user
    add_user(user.id, user.username)

    coupon = get_valid_coupon_by_brand("Nike")

    if coupon:
        await update.message.reply_text(
            f"🎯 *Nike Coupon*\n\n"
            f"Code: `{coupon['code']}`\n"
            f"{coupon.get('description', '')}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "Sorry, no Nike coupon available at the moment. Check back later!"
        )


def main():
    """Start the bot."""
    # Initialize database
    init_db()

    # Add a default Nike coupon if none exists
    coupon = get_coupon_by_brand("Nike")
    if not coupon:
        add_coupon(
            "Nike",
            "NIKE25SAVE",
            "25% off your order",
            (datetime.now() + timedelta(days=30)).isoformat()
        )
        logger.info("Added default Nike coupon")

    # Create the Application
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("nike", nike_command))

    # Run the bot
    logger.info("Starting ProCoupon bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
