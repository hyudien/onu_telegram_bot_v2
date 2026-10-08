"""Main bot application"""

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from handlers.start import start, access_callback
from handlers.mikrotik import (
    menu_handler as mikrotik_handler,
    callback_handler as mikrotik_callback_handler
)
from handlers.olt import (
    menu_handler as olt_handler,
    callback_handler as olt_callback_handler
)
from app.config import BOT_TOKEN

def setup_handlers(app: Application) -> None:
    """Setup all bot handlers"""
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    
    # Access control callback
    app.add_handler(CallbackQueryHandler(access_callback, pattern=r"^(acc_|reject_)"))
    
    # OLT callback handlers
    app.add_handler(CallbackQueryHandler(olt_callback_handler))
    
    # MikroTik callback handlers
    app.add_handler(CallbackQueryHandler(mikrotik_callback_handler))
    
    # Text message handlers
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_router
        )
    )

async def message_router(update, context):
    """Route message to appropriate handler"""
    text = update.message.text
    
    # OLT menu items
    olt_items = ["📡 MANAGE OLT", "📊 STATUS", "🔍 CARI", "📝 REGISTRASI", "💾 SAVE CONFIG", "🔄 SYNC DB"]
    
    # MikroTik menu items
    mikrotik_items = ["🌐 MANAGE MIKROTIK", "📊 STATUS MT", "➕ TAMBAH USER", "🗑 HAPUS USER", "✏️ EDIT USER", "🔙 MIKROTIK MENU"]
    
    if any(item in text for item in olt_items):
        await olt_handler(update, context)
    elif any(item in text for item in mikrotik_items):
        await mikrotik_handler(update, context)
    elif text == "🏠 MENU UTAMA":
        await show_main_menu(update, context)
    else:
        # Try both handlers
        await olt_handler(update, context)
        if update.message.text == text:  # Message not handled
            await mikrotik_handler(update, context)

async def show_main_menu(update, context):
    """Show main menu"""
    from telegram import ReplyKeyboardMarkup
    
    context.user_data["step"] = None
    keyboard = ReplyKeyboardMarkup(
        [
            ["📡 MANAGE OLT"],
            ["🌐 MANAGE MIKROTIK"]
        ],
        resize_keyboard=True
    )
    await update.message.reply_text("Pilih Menu", reply_markup=keyboard)

def main() -> None:
    """Start the bot"""
    
    # Create the Application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Setup handlers
    setup_handlers(app)
    
    # Run the bot
    print("🤖 Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
