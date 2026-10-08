"""Admin setup flow for Telegram bot configuration."""

from telegram import Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from app.config import ADMIN_ID

(
    SETUP_TOKEN,
    SETUP_ADMIN_ID,
    SETUP_OLT_HOST,
    SETUP_OLT_USER,
    SETUP_OLT_PASS,
) = range(5)


async def start_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point for the admin setup conversation."""
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Anda bukan admin untuk bot ini.")
        return ConversationHandler.END

    await update.message.reply_text(
        "⚙️ Setup konfigurasi bot\n\n"
        "Masukkan BOT_TOKEN:"
    )
    return SETUP_TOKEN


async def save_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save bot token from user input."""
    context.user_data["BOT_TOKEN"] = update.message.text.strip()
    await update.message.reply_text("Masukkan ADMIN_ID:")
    return SETUP_ADMIN_ID


async def save_admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save admin ID from user input."""
    context.user_data["ADMIN_ID"] = update.message.text.strip()
    await update.message.reply_text("Masukkan OLT_HOST:")
    return SETUP_OLT_HOST


async def save_olt_host(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save OLT host from user input."""
    context.user_data["OLT_HOST"] = update.message.text.strip()
    await update.message.reply_text("Masukkan OLT_USERNAME:")
    return SETUP_OLT_USER


async def save_olt_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save OLT username from user input."""
    context.user_data["OLT_USERNAME"] = update.message.text.strip()
    await update.message.reply_text("Masukkan OLT_PASSWORD:")
    return SETUP_OLT_PASS


async def save_olt_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save OLT password and write configuration to .env."""
    context.user_data["OLT_PASSWORD"] = update.message.text.strip()

    env_lines = [
        f"BOT_TOKEN={context.user_data['BOT_TOKEN']}",
        f"ADMIN_ID={context.user_data['ADMIN_ID']}",
        f"OLT_HOST={context.user_data['OLT_HOST']}",
        f"OLT_USERNAME={context.user_data['OLT_USERNAME']}",
        f"OLT_PASSWORD={context.user_data['OLT_PASSWORD']}",
    ]

    with open(".env", "w", encoding="utf-8") as f:
        f.write("\n".join(env_lines) + "\n")

    await update.message.reply_text(
        "✅ Setup selesai.\n\n"
        "File .env berhasil dibuat dan disimpan.\n"
        "Silakan restart bot agar config diterapkan."
    )
    return ConversationHandler.END


async def cancel_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel setup flow."""
    await update.message.reply_text("❌ Setup dibatalkan.")
    return ConversationHandler.END


setup_handler = ConversationHandler(
    entry_points=[CommandHandler("admin_setup", start_setup)],
    states={
        SETUP_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_token)],
        SETUP_ADMIN_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_admin_id)],
        SETUP_OLT_HOST: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_olt_host)],
        SETUP_OLT_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_olt_user)],
        SETUP_OLT_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_olt_pass)],
    },
    fallbacks=[CommandHandler("cancel", cancel_setup)],
)
