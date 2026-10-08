"""MikroTik management handlers"""

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from datetime import datetime

from data.mikrotik_routers import ROUTERS
from data.mt_profiles import MT_PROFILES
from mikrotik.status import get_status
from mikrotik.users import get_online_users, get_offline_users, get_user
from mikrotik.actions import add_user, delete_user, set_password, enable_user, disable_user, set_profile, set_comment, find_users

def get_router(context: ContextTypes.DEFAULT_TYPE) -> str:
    """Get selected router from context"""
    return context.user_data.get("router", "KWL")

def clear_step(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear current step"""
    context.user_data["step"] = None

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle MikroTik menu messages"""
    
    text = update.message.text
    step = context.user_data.get("step")
    
    # Main menu navigation
    if text == "🏠 MENU UTAMA":
        clear_step(context)
        keyboard = ReplyKeyboardMarkup(
            [["📡 MANAGE OLT"], ["🌐 MANAGE MIKROTIK"]],
            resize_keyboard=True
        )
        await update.message.reply_text("Pilih Menu", reply_markup=keyboard)
        return
    
    if text == "🌐 MANAGE MIKROTIK":
        clear_step(context)
        buttons = [[f"🌐 Router {router}"] for router in ROUTERS]
        buttons.append(["🏠 MENU UTAMA"])
        await update.message.reply_text(
            "🌐 Pilih Router MikroTik",
            reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        )
        return
    
    # Router selection
    if text.startswith("🌐 Router "):
        router = text.replace("🌐 Router ", "")
        context.user_data["router"] = router
        clear_step(context)
        
        keyboard = ReplyKeyboardMarkup(
            [
                ["📊 STATUS MT"],
                ["➕ TAMBAH USER"],
                ["🗑 HAPUS USER"],
                ["✏️ EDIT USER"],
                ["🔙 MIKROTIK MENU"]
            ],
            resize_keyboard=True
        )
        await update.message.reply_text(f"🌐 Router {router}", reply_markup=keyboard)
        return
    
    if text == "🔙 MIKROTIK MENU":
        clear_step(context)
        buttons = [[f"🌐 Router {router}"] for router in ROUTERS]
        buttons.append(["🏠 MENU UTAMA"])
        await update.message.reply_text(
            "🌐 Pilih Router MikroTik",
            reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        )
        return
    
    # Status
    if text == "📊 STATUS MT":
        clear_step(context)
        router = get_router(context)
        
        try:
            data = get_status(router)
            msg = (
                f"🌐 Router {router.upper()}\n\n"
                f"👥 Total User : {data['total']}\n"
                f"🟢 Online : {data['online']}\n"
                f"🔴 Offline : {data['offline']}\n\n"
                f"CPU : {data['cpu']}%\n"
                f"RAM : {data['memory']} MB\n"
                f"Uptime : {data['uptime']}"
            )
            
            buttons = [
                [
                    InlineKeyboardButton("🟢 USER ONLINE", callback_data="mt_online"),
                    InlineKeyboardButton("🔴 USER OFFLINE", callback_data="mt_offline")
                ]
            ]
            
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(buttons))
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        return
    
    # Add user
    if text == "➕ TAMBAH USER":
        context.user_data["step"] = "mt_add_user"
        await update.message.reply_text("Masukkan Username PPPoE")
        return
    
    if step == "mt_add_user":
        context.user_data["mt_user"] = text
        context.user_data["step"] = "mt_add_pass"
        await update.message.reply_text("Masukkan Password PPPoE")
        return
    
    if step == "mt_add_pass":
        context.user_data["mt_pass"] = text
        buttons = [
            [InlineKeyboardButton(p, callback_data=f"mt_profile_{p}")] for p in MT_PROFILES
        ]
        await update.message.reply_text(
            "📦 Pilih Profile",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    
    # Delete user
    if text == "🗑 HAPUS USER":
        context.user_data["step"] = "mt_delete_user"
        await update.message.reply_text("Masukkan Username PPPoE")
        return
    
    if step == "mt_delete_user":
        router = get_router(context)
        hasil = find_users(router, text)
        
        if not hasil:
            await update.message.reply_text("❌ User tidak ditemukan")
            return
        
        if len(hasil) > 1:
            context.user_data["delete_candidates"] = hasil
            context.user_data["step"] = "mt_delete_select"
            
            msg = "🔍 Ditemukan beberapa user\n\n"
            for i, name in enumerate(hasil, start=1):
                msg += f"{i}. {name}\n"
            msg += "\nBalas nomor user"
            
            await update.message.reply_text(msg)
            return
        
        await show_delete_confirmation(update, context, hasil[0])
        return
    
    if step == "mt_delete_select":
        try:
            nomor = int(text)
            hasil = context.user_data["delete_candidates"]
            username = hasil[nomor - 1]
        except (ValueError, IndexError):
            await update.message.reply_text("❌ Masukkan nomor yang benar")
            return
        
        await show_delete_confirmation(update, context, username)
        return
    
    # Edit user
    if text == "✏️ EDIT USER":
        context.user_data["step"] = "mt_edit_user"
        await update.message.reply_text("Masukkan Username PPPoE")
        return
    
    if step == "mt_edit_user":
        router = get_router(context)
        user = get_user(router, text)
        
        if not user:
            await update.message.reply_text("❌ User tidak ditemukan")
            return
        
        context.user_data["edit_user"] = text
        clear_step(context)
        
        disabled = user.get("disabled", False)
        status = "YES" if disabled else "NO"
        
        buttons = [
            [InlineKeyboardButton("🔑 Password", callback_data="edit_pass")],
            [InlineKeyboardButton("📦 Profile", callback_data="edit_profile")],
            [InlineKeyboardButton("📝 Comment", callback_data="edit_comment")],
            [
                InlineKeyboardButton("🚫 Disable", callback_data="edit_disable"),
                InlineKeyboardButton("✅ Enable", callback_data="edit_enable")
            ]
        ]
        
        msg = (
            f"👤 User : {user['name']}\n"
            f"📦 Profile : {user.get('profile', '-')}\n"
            f"📝 Comment : {user.get('comment', '-')}\n"
            f"🚫 Disabled : {status}"
        )
        
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(buttons))
        return
    
    if step == "edit_pass_input":
        username = context.user_data["edit_user"]
        router = get_router(context)
        
        try:
            set_password(router, username, text)
            await update.message.reply_text("✅ Password berhasil diubah")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        finally:
            clear_step(context)
        return
    
    if step == "edit_comment_input":
        username = context.user_data["edit_user"]
        router = get_router(context)
        
        try:
            set_comment(router, username, text)
            await update.message.reply_text(f"✅ Comment berhasil diubah untuk {username}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        finally:
            clear_step(context)
        return

async def show_delete_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, username: str) -> None:
    """Show delete confirmation dialog"""
    
    router = get_router(context)
    user = get_user(router, username)
    
    context.user_data["delete_user"] = username
    clear_step(context)
    
    buttons = [
        [
            InlineKeyboardButton("✅ HAPUS", callback_data="mt_delete_yes"),
            InlineKeyboardButton("❌ BATAL", callback_data="mt_delete_no")
        ]
    ]
    
    msg = (
        f"🗑 KONFIRMASI HAPUS\n\n"
        f"👤 User : {username}\n"
        f"📦 Profile : {user.get('profile', '-')}\n"
        f"📝 Comment : {user.get('comment', '-')}"
    )
    
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(buttons))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle MikroTik callback queries"""
    
    query = update.callback_query
    await query.answer()
    data = query.data
    
    router = get_router(context)
    
    # Profile selection during add user
    if data.startswith("mt_profile_"):
        profile = data.replace("mt_profile_", "")
        context.user_data["mt_profile"] = profile
        context.user_data["step"] = "mt_add_comment"
        
        await query.edit_message_text(f"📦 Profile : {profile}")
        await query.message.reply_text("Masukkan Comment")
        return
    
    if data == "mt_add_comment":
        username = context.user_data["mt_user"]
        password = context.user_data["mt_pass"]
        profile = context.user_data["mt_profile"]
        comment = ""
        
        try:
            add_user(router, username, password, profile, comment)
            msg = (
                f"✅ PPPoE BERHASIL DIBUAT\n\n"
                f"👤 User : {username}\n"
                f"🔑 Pass : {password}\n"
                f"📦 Profile : {profile}\n"
                f"📝 Comment : {comment}"
            )
            await query.message.reply_text(msg)
        except Exception as e:
            await query.message.reply_text(f"❌ Error: {str(e)}")
        finally:
            clear_step(context)
        return
    
    # Delete confirmation
    if data == "mt_delete_yes":
        username = context.user_data.get("delete_user")
        
        try:
            delete_user(router, username)
            await query.edit_message_text(f"✅ User {username} berhasil dihapus")
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}")
        return
    
    if data == "mt_delete_no":
        await query.edit_message_text("❌ Dibatalkan")
        return
    
    # Edit password
    if data == "edit_pass":
        context.user_data["step"] = "edit_pass_input"
        await query.message.reply_text("Masukkan Password Baru")
        return
    
    # Edit profile
    if data == "edit_profile":
        buttons = [
            [InlineKeyboardButton(p, callback_data=f"set_profile_{p}")] for p in MT_PROFILES
        ]
        await query.message.reply_text(
            "📦 Pilih Profile Baru",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    
    if data.startswith("set_profile_"):
        profile = data.replace("set_profile_", "")
        username = context.user_data["edit_user"]
        
        try:
            set_profile(router, username, profile)
            msg = (
                f"✅ PROFILE BERHASIL DIUBAH\n\n"
                f"👤 User : {username}\n"
                f"📦 Profile : {profile}"
            )
            await query.edit_message_text(msg)
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}")
        return
    
    # Edit comment
    if data == "edit_comment":
        context.user_data["step"] = "edit_comment_input"
        await query.message.reply_text("Masukkan Comment Baru")
        return
    
    # Disable user
    if data == "edit_disable":
        username = context.user_data["edit_user"]
        
        try:
            disable_user(router, username)
            await query.answer("User Disabled")
            await query.edit_message_text(f"🚫 {username} berhasil di-disable")
        except Exception as e:
            await query.answer(f"Error: {str(e)}")
        return
    
    # Enable user
    if data == "edit_enable":
        username = context.user_data["edit_user"]
        
        try:
            enable_user(router, username)
            await query.answer("User Enabled")
            await query.edit_message_text(f"✅ {username} berhasil di-enable")
        except Exception as e:
            await query.answer(f"Error: {str(e)}")
        return
    
    # User status
    if data == "mt_online":
        try:
            users = get_online_users(router)
            msg = "🟢 USER ONLINE\n\n"
            for i, user in enumerate(users[:50], start=1):
                msg += f"{i}. {user}\n"
            msg += f"\nTotal : {len(users)}"
            await query.message.reply_text(msg)
        except Exception as e:
            await query.answer(f"Error: {str(e)}", show_alert=True)
        return
    
    if data == "mt_offline":
        try:
            users = get_offline_users(router)
            msg = f"🔴 USER OFFLINE\n\nTotal : {len(users)}\n\n"
            for i, user in enumerate(users[:100], start=1):
                msg += f"{i}. {user}\n"
            msg += f"\n🕒 Refresh : {datetime.now().strftime('%H:%M:%S')}"
            
            buttons = [
                [
                    InlineKeyboardButton("🔄 REFRESH", callback_data="mt_offline_refresh"),
                    InlineKeyboardButton("🔙 KEMBALI", callback_data="mt_back")
                ]
            ]
            
            await query.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(buttons))
        except Exception as e:
            await query.answer(f"Error: {str(e)}", show_alert=True)
        return
    
    if data == "mt_offline_refresh":
        try:
            users = get_offline_users(router)
            msg = f"🔴 USER OFFLINE\n\nTotal : {len(users)}\n\n"
            for i, user in enumerate(users[:100], start=1):
                msg += f"{i}. {user}\n"
            msg += f"\n🕒 Refresh : {datetime.now().strftime('%H:%M:%S')}"
            
            buttons = [
                [
                    InlineKeyboardButton("🔄 REFRESH", callback_data="mt_offline_refresh"),
                    InlineKeyboardButton("🔙 KEMBALI", callback_data="mt_back")
                ]
            ]
            
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(buttons))
        except Exception as e:
            await query.answer(f"Error: {str(e)}", show_alert=True)
        return
    
    if data == "mt_back":
        keyboard = ReplyKeyboardMarkup(
            [
                ["📊 STATUS MT"],
                ["➕ TAMBAH USER"],
                ["🗑 HAPUS USER"],
                ["✏️ EDIT USER"],
                ["🔙 MIKROTIK MENU"]
            ],
            resize_keyboard=True
        )
        await query.message.reply_text("🌐 Router Menu", reply_markup=keyboard)
        return
