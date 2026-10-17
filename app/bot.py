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
from data.users import is_allowed
from handlers.mikrotik import (
    menu_handler as mikrotik_handler,
    callback_handler as mikrotik_callback_handler,
)
from handlers.olt import (
    menu_handler as olt_handler,
    callback_handler as olt_callback_handler,
    OLT_STEPS,
)
from app.config import BOT_TOKEN


OLT_ITEMS = {
    "📡 MANAGE OLT",
    "📊 STATUS",
    "🔍 CARI",
    "📝 REGISTRASI",
    "💾 SAVE CONFIG",
    "🔄 SYNC DB",
}

MIKROTIK_ITEMS = {
    "🌐 MANAGE MIKROTIK",
    "📊 STATUS MT",
    "➕ TAMBAH USER",
    "🗑 HAPUS USER",
    "✏️ EDIT USER",
    "🔙 MIKROTIK MENU",
}

MIKROTIK_CALLBACK_PREFIXES = ("mt_", "edit_", "set_profile_")


def setup_handlers(app: Application) -> None:
    """Register all bot handlers."""
    app.add_handler(CommandHandler("start", start))
    app.add_handler(setup_handler)
    app.add_handler(CallbackQueryHandler(access_callback, pattern=r"^(acc_|reject_)"))
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_router,
        )
    )


async def message_router(update, context):
    """Route text messages to OLT or MikroTik handler (approved users only)."""
    if not is_allowed(update.effective_user.id):
        await update.message.reply_text("⛔ Akses belum disetujui. Gunakan /start untuk meminta akses.")
        return

    text = update.message.text
    if text == "🏠 MENU UTAMA" or text in OLT_ITEMS or text in MIKROTIK_ITEMS or text.startswith("🌐 Router "):
        context.user_data["step"] = None

    if text == "🏠 MENU UTAMA":
        await show_main_menu(update, context)
    elif text in OLT_ITEMS:
        await olt_handler(update, context)
    elif text in MIKROTIK_ITEMS or text.startswith("🌐 Router "):
        await mikrotik_handler(update, context)
    elif context.user_data.get("step") in OLT_STEPS:
        await olt_handler(update, context)
    elif context.user_data.get("step"):
        await mikrotik_handler(update, context)


async def callback_router(update, context):
    """Route inline button callbacks to OLT or MikroTik handler (approved users only)."""
    query = update.callback_query
    if not is_allowed(query.from_user.id):
        await query.answer("⛔ Akses belum disetujui", show_alert=True)
        return

    if query.data.startswith(MIKROTIK_CALLBACK_PREFIXES):
        await mikrotik_callback_handler(update, context)
    else:
        await olt_callback_handler(update, context)


async def show_main_menu(update, context):
    """Display the main menu."""
    from telegram import ReplyKeyboardMarkup

    context.user_data["step"] = None
    keyboard = ReplyKeyboardMarkup(
        [
            ["📡 MANAGE OLT"],
            ["🌐 MANAGE MIKROTIK"],
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
