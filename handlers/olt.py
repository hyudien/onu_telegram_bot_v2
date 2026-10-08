"""OLT management handlers - Stub for now"""

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from data.pons import PON_NAMES
from olt.get_status import get_summary, get_pon_info, get_pon_summary_live, get_pon_problem_customers_live
from data.customer_db import find_customers

def clear_step(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear current step"""
    context.user_data["step"] = None

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle OLT menu messages"""
    
    text = update.message.text
    step = context.user_data.get("step")
    
    # Main menu
    if text == "📡 MANAGE OLT":
        clear_step(context)
        keyboard = ReplyKeyboardMarkup(
            [
                ["📊 STATUS", "🔍 CARI"],
                ["📝 REGISTRASI"],
                ["💾 SAVE CONFIG"],
                ["🔄 SYNC DB"],
                ["🏠 MENU UTAMA"]
            ],
            resize_keyboard=True
        )
        await update.message.reply_text("📡 Menu OLT", reply_markup=keyboard)
        return
    
    # Status
    if text == "📊 STATUS":
        clear_step(context)
        try:
            s = get_summary()
            msg = (
                f"📊 STATUS OLT\n\n"
                f"🟢 Online     : {s['online']}\n"
                f"🔴 Offline    : {s['offline']}\n"
                f"📡 LOS        : {s['los']}\n"
                f"⚡ DyingGasp  : {s['dyinggasp']}\n\n"
                f"📊 Total ONU  : {s['total']}"
            )
            
            buttons = [[InlineKeyboardButton("📍 PER PON", callback_data="perpon")]]
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(buttons))
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        return
    
    # Search
    if text == "🔍 CARI":
        context.user_data["step"] = "search"
        await update.message.reply_text("Masukkan Nama / SN / PPPoE User")
        return
    
    if step == "search":
        customers = find_customers(text)
        clear_step(context)
        
        if not customers:
            await update.message.reply_text("Data tidak ditemukan")
            return
        
        buttons = [
            [InlineKeyboardButton(c.get("name", c["sn"]), callback_data=f"cust_{i}")]
            for i, c in enumerate(customers[:10])
        ]
        
        context.user_data["search_result"] = customers
        await update.message.reply_text("Pilih pelanggan", reply_markup=InlineKeyboardMarkup(buttons))
        return
    
    # Registration
    if text == "📝 REGISTRASI":
        await update.message.reply_text("📝 Fitur registrasi sedang dalam pengembangan")
        return
    
    # Save config
    if text == "💾 SAVE CONFIG":
        await update.message.reply_text("💾 Fitur save config sedang dalam pengembangan")
        return
    
    # Sync DB
    if text == "🔄 SYNC DB":
        await update.message.reply_text("🔄 Fitur sync sedang dalam pengembangan")
        return

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle OLT callback queries"""
    
    query = update.callback_query
    await query.answer()
    data = query.data
    
    # Per PON status
    if data == "perpon":
        buttons = []
        row = []
        
        for pon, nama in PON_NAMES.items():
            row.append(InlineKeyboardButton(nama, callback_data=f"pon_{pon}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        
        if row:
            buttons.append(row)
        
        await query.edit_message_text(
            "📍 Pilih PON",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    
    # PON status
    if data.startswith("pon_") or data.startswith("refresh_"):
        try:
            if data.startswith("refresh_"):
                pon = data.replace("refresh_", "")
            else:
                pon = data.replace("pon_", "")
            
            pon_data = get_pon_info(pon)
            summary = get_pon_summary_live(pon_data)
            problems = get_pon_problem_customers_live(pon_data, pon)
            nama_pon = PON_NAMES.get(pon, pon)
            
            msg = (
                f"📡 {nama_pon}\n"
                f"({pon})\n\n"
                f"🟢 Online : {summary['online']}\n"
                f"🔴 Offline : {summary['offline']}\n"
                f"📊 Total : {summary['total']}\n\n"
            )
            
            if problems:
                msg += "🔴 ONU BERMASALAH\n\n"
                for p in problems:
                    msg += f"{p['onu_id']} - {p['name']}\n({p['status'].upper()})\n\n"
            else:
                msg += "✅ Semua ONU Online"
            
            buttons = [
                [InlineKeyboardButton("🔄 REFRESH", callback_data=f"refresh_{pon}")],
                [InlineKeyboardButton("◀️ KEMBALI", callback_data="perpon")]
            ]
            
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(buttons))
        except Exception as e:
            await query.answer(f"Error: {str(e)}", show_alert=True)
        return
    
    # Customer detail (if search result exists)
    if data.startswith("cust_"):
        try:
            idx = int(data.replace("cust_", ""))
            cust = context.user_data["search_result"][idx]
            context.user_data["selected_customer"] = cust
            
            msg = (
                f"NAMA  : {cust.get('name', '-')}\n"
                f"USER  : {cust.get('pppoe_user', '-')}\n"
                f"SN    : {cust.get('sn', '-')}\n"
                f"PON   : {cust.get('pon', '-')}\n"
                f"ONU   : {cust.get('onu_id', '-')}\n"
                f"MODE  : {cust.get('mode', '-')}\n"
                f"VLAN  : {cust.get('vlan', '-')}\n"
                f"PAKET : {cust.get('package', '-')}"
            )
            
            buttons = [
                [InlineKeyboardButton("📡 INFO", callback_data="cust_info")],
                [InlineKeyboardButton("⬆️ UBAH PAKET", callback_data="cust_change_pkg")]
            ]
            
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(buttons))
        except (IndexError, KeyError) as e:
            await query.answer(f"Error: {str(e)}", show_alert=True)
        return
