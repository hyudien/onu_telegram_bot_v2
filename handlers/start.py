"""Start command and access control handler"""

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from data.users import load_users, add_user
from app.config import ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - Check user access and show menu"""
    
    user_id = update.effective_user.id
    fullname = update.effective_user.full_name
    
    # Check if user is allowed
    if user_id not in load_users():
        # Send access request to admin
        buttons = [
            [
                InlineKeyboardButton("✅ ACC", callback_data=f"acc_{user_id}"),
                InlineKeyboardButton("❌ TOLAK", callback_data=f"reject_{user_id}")
            ]
        ]
        
        await context.bot.send_message(
            ADMIN_ID,
            f"🔔 Permintaan akses bot\n\n"
            f"Nama : {fullname}\n"
            f"ID   : {user_id}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
        await update.message.reply_text(
            "📨 Permintaan akses telah dikirim ke admin.\n"
            "Silakan tunggu persetujuan."
        )
        return
    
    # User is allowed - show main menu
    keyboard = ReplyKeyboardMarkup(
        [
            ["📡 MANAGE OLT"],
            ["🌐 MANAGE MIKROTIK"]
        ],
        resize_keyboard=True
    )
    
    await update.message.reply_text(
        f"Selamat datang {fullname}!\n\n"
        "Bot ONU - Manajemen OLT & MikroTik",
        reply_markup=keyboard
    )

async def access_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle access request approval/rejection"""
    
    query = update.callback_query
    
    if query.from_user.id != ADMIN_ID:
        await query.answer("Hanya admin yang dapat melakukan ini", show_alert=True)
        return
    
    await query.answer()
    data = query.data
    
    if data.startswith("acc_"):
        # Approve access
        user_id = int(data.replace("acc_", ""))
        add_user(user_id)
        await query.edit_message_text(f"✅ User {user_id} disetujui")
        
        # Notify user
        try:
            await context.bot.send_message(
                user_id,
                "✅ Akses Anda telah disetujui!\n"
                "Gunakan /start untuk memulai."
            )
        except Exception as e:
            print(f"Error notifying user: {e}")
    
    elif data.startswith("reject_"):
        # Reject access
        user_id = int(data.replace("reject_", ""))
        await query.edit_message_text(f"❌ User {user_id} ditolak")
        
        # Notify user
        try:
            await context.bot.send_message(
                user_id,
                "❌ Akses Anda telah ditolak.\n"
                "Hubungi admin untuk informasi lebih lanjut."
            )
        except Exception as e:
            print(f"Error notifying user: {e}")
