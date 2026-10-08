"""Main bot application"""

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from handlers.start import start, access_callback
from handlers.setup import setup_handler
from handlers.mikrotik import (
    menu_handler as mikrotik_handler,
    callback_handler as mikrotik_callback_handler,
)
from handlers.olt import (
    menu_handler as olt_handler,
    callback_handler as olt_callback_handler,
)
from app.config import BOT_TOKEN


def setup_handlers(app: Application) -> None:
    """Register all bot handlers."""
    app.add_handler(CommandHandler("start", start))
    app.add_handler(setup_handler)
    app.add_handler(CallbackQueryHandler(access_callback, pattern=r"^(acc_|reject_)") )
    app.add_handler(CallbackQueryHandler(olt_callback_handler))
    app.add_handler(CallbackQueryHandler(mikrotik_callback_handler))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_router,
        )
    )


async def message_router(update, context):
    """Route text messages to OLT or MikroTik handler."""
    text = update.message.text

    olt_items = [
        "📡 MANAGE OLT",
        "📊 STATUS",
        "🔍 CARI",
        "📝 REGISTRASI",
        "💾 SAVE CONFIG",
        "🔄 SYNC DB",
        "⚙️ KONFIGURASI",
    ]

    mikrotik_items = [
        "🌐 MANAGE MIKROTIK",
        "📊 STATUS MT",
        "➕ TAMBAH USER",
        "🗑 HAPUS USER",
        "✏️ EDIT USER",
        "🔙 MIKROTIK MENU",
    ]

    if any(item in text for item in olt_items):
        await olt_handler(update, context)
    elif any(item in text for item in mikrotik_items):
        await mikrotik_handler(update, context)
    elif text == "🏠 MENU UTAMA":
        await show_main_menu(update, context)
    else:
        await olt_handler(update, context)
        if update.message.text == text:
            await mikrotik_handler(update, context)


async def show_main_menu(update, context):
    """Display the main menu."""
    from telegram import ReplyKeyboardMarkup

    context.user_data["step"] = None
    keyboard = ReplyKeyboardMarkup(
        [
            ["📡 MANAGE OLT", "🌐 MANAGE MIKROTIK"],
            ["⚙️ KONFIGURASI"],
            ["📊 LAPORAN"],
        ],
        resize_keyboard=True,
    )
    await update.message.reply_text("Pilih Menu", reply_markup=keyboard)


def main() -> None:
    """Run the bot."""
    app = Application.builder().token(BOT_TOKEN).build()
    setup_handlers(app)
    print("🤖 Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
