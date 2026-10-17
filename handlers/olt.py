"""OLT management handlers"""

import asyncio

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from data.pons import PON_NAMES
from olt.get_status import get_summary, get_pon_info, get_pon_summary_live, get_pon_problem_customers_live
from data.customer_db import find_customers
from data.modes import MODES
from data.packages import PACKAGES
from data.vlans import VLANS
from olt.change_onu import change_onu
from olt.change_package import change_package
from olt.change_pppoe import change_pppoe
from olt.delete_onu import delete_onu
from olt.enable_remote import enable_remote
from olt.get_onu_info import get_onu_info
from olt.reboot_onu import reboot_onu
from olt.register_onu import get_unconfigured_onu, register_onu
from olt.save_config import save_config
from sync_olt_db import sync_olt_db

OLT_STEPS = {
    "search", "reg_name", "reg_pppoe_user", "reg_pppoe_pass",
    "chg_pppoe_user", "chg_pppoe_pass", "chg_onu_sn",
}


async def run_blocking(func, *args):
    """Run blocking OLT (telnet) calls without blocking the event loop."""
    return await asyncio.to_thread(func, *args)


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
            s = await run_blocking(get_summary)
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
        clear_step(context)
        try:
            onus = await run_blocking(get_unconfigured_onu)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
            return
        if not onus:
            await update.message.reply_text("Tidak ada ONU baru terdeteksi")
            return
        context.user_data["reg_list"] = onus
        buttons = [
            [InlineKeyboardButton(f"{o['sn']} ({PON_NAMES.get(o['pon'], o['pon'])})", callback_data=f"reg_{i}")]
            for i, o in enumerate(onus[:20])
        ]
        await update.message.reply_text("Pilih ONU", reply_markup=InlineKeyboardMarkup(buttons))
        return

    if step == "reg_name":
        context.user_data["reg"]["name"] = text.strip()
        context.user_data["step"] = None
        buttons = [[InlineKeyboardButton(m, callback_data=f"reg_mode_{m}")] for m in MODES]
        await update.message.reply_text("Pilih Mode", reply_markup=InlineKeyboardMarkup(buttons))
        return

    if step == "reg_pppoe_user":
        context.user_data["reg"]["pppoe_user"] = text.strip()
        context.user_data["step"] = "reg_pppoe_pass"
        await update.message.reply_text("Masukkan PPPoE Password")
        return

    if step == "reg_pppoe_pass":
        context.user_data["reg"]["pppoe_pass"] = text.strip()
        clear_step(context)
        await ask_package(update.message, "reg_pkg_")
        return

    # Change PPPoE / replace ONU
    cust = context.user_data.get("selected_customer")
    if step == "chg_pppoe_user":
        context.user_data["new_pppoe_user"] = text.strip()
        context.user_data["step"] = "chg_pppoe_pass"
        await update.message.reply_text("Masukkan PPPoE Password Baru")
        return

    if step == "chg_pppoe_pass" and cust:
        clear_step(context)
        try:
            await run_blocking(
                change_pppoe, cust["pon"], cust["onu_id"], cust.get("vlan", ""),
                context.user_data.pop("new_pppoe_user"), text.strip(),
            )
            await update.message.reply_text("✅ PPPoE berhasil diubah")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        return

    if step == "chg_onu_sn" and cust:
        clear_step(context)
        try:
            await run_blocking(change_onu, cust, text.strip().upper())
            await update.message.reply_text("✅ ONU berhasil diganti")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        return

    # Save config
    if text == "💾 SAVE CONFIG":
        clear_step(context)
        try:
            await run_blocking(save_config)
            await update.message.reply_text("✅ Konfigurasi OLT berhasil disimpan")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        return

    # Sync DB
    if text == "🔄 SYNC DB":
        clear_step(context)
        try:
            r = await run_blocking(sync_olt_db)
            await update.message.reply_text(
                f"✅ Sync selesai\n\nDitambah : {r['added']}\nDiperbarui : {r['updated']}\nTotal : {r['total']}"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        return


async def ask_package(message, prefix: str) -> None:
    buttons = [[InlineKeyboardButton(p, callback_data=f"{prefix}{p}")] for p in PACKAGES]
    await message.reply_text("Pilih Paket", reply_markup=InlineKeyboardMarkup(buttons))

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
            
            pon_data = await run_blocking(get_pon_info, pon)
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
    if data.startswith("cust_") and data[5:].isdigit():
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
                [InlineKeyboardButton("⬆️ UBAH PAKET", callback_data="cust_change_pkg")],
                [InlineKeyboardButton("🔑 UBAH PPPOE", callback_data="cust_pppoe")],
                [InlineKeyboardButton("🔄 GANTI ONU", callback_data="cust_change_onu")],
                [InlineKeyboardButton("🌐 REMOTE", callback_data="cust_remote"),
                 InlineKeyboardButton("🔁 REBOOT", callback_data="cust_reboot")],
                [InlineKeyboardButton("🗑 HAPUS ONU", callback_data="cust_delete")]
            ]
            
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(buttons))
        except (IndexError, KeyError) as e:
            await query.answer(f"Error: {str(e)}", show_alert=True)
        return

    # Customer actions (selected customer required)
    cust = context.user_data.get("selected_customer")
    if data.startswith(("cust_", "pkg_", "del_")) and not cust:
        await query.answer("Pilih pelanggan terlebih dahulu", show_alert=True)
        return

    if data == "cust_info":
        try:
            info = await run_blocking(get_onu_info, cust["pon"], cust["onu_id"])
            await query.message.reply_text(info[:4000] or "Tidak ada data")
        except Exception as e:
            await query.answer(f"Error: {str(e)}", show_alert=True)
        return

    if data == "cust_change_pkg":
        await ask_package(query.message, "pkg_")
        return

    if data.startswith("pkg_"):
        package = data.replace("pkg_", "")
        try:
            await run_blocking(change_package, cust["pon"], cust["onu_id"], package)
            cust["package"] = package
            await query.edit_message_text(f"✅ Paket diubah ke {package}")
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}")
        return

    if data == "cust_pppoe":
        context.user_data["step"] = "chg_pppoe_user"
        await query.message.reply_text("Masukkan PPPoE Username Baru")
        return

    if data == "cust_change_onu":
        context.user_data["step"] = "chg_onu_sn"
        await query.message.reply_text("Masukkan SN ONU Baru")
        return

    if data == "cust_remote":
        try:
            await run_blocking(enable_remote, cust["pon"], cust["onu_id"])
            await query.answer("Remote access aktif", show_alert=True)
        except Exception as e:
            await query.answer(f"Error: {str(e)}", show_alert=True)
        return

    if data == "cust_reboot":
        try:
            await run_blocking(reboot_onu, cust["pon"], cust["onu_id"])
            await query.answer("ONU di-reboot", show_alert=True)
        except Exception as e:
            await query.answer(f"Error: {str(e)}", show_alert=True)
        return

    if data == "cust_delete":
        buttons = [[
            InlineKeyboardButton("✅ HAPUS", callback_data="del_yes"),
            InlineKeyboardButton("❌ BATAL", callback_data="del_no"),
        ]]
        await query.message.reply_text(
            f"🗑 Hapus ONU {cust.get('name', cust['sn'])} ({cust['pon']}:{cust['onu_id']})?",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return

    if data == "del_yes":
        try:
            await run_blocking(delete_onu, cust["pon"], cust["onu_id"])
            context.user_data.pop("selected_customer", None)
            await query.edit_message_text("✅ ONU berhasil dihapus")
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}")
        return

    if data == "del_no":
        await query.edit_message_text("❌ Dibatalkan")
        return

    # Registration flow
    reg = context.user_data.get("reg")

    if data.startswith("reg_mode_") and reg:
        reg["mode"] = data.replace("reg_mode_", "")
        await query.edit_message_text(f"Mode : {reg['mode']}")
        if "PPPOE" in reg["mode"]:
            context.user_data["step"] = "reg_pppoe_user"
            await query.message.reply_text("Masukkan PPPoE Username")
        else:
            await ask_package(query.message, "reg_pkg_")
        return

    if data.startswith("reg_pkg_") and reg:
        reg["package"] = data.replace("reg_pkg_", "")
        buttons = [[InlineKeyboardButton(v, callback_data=f"reg_vlan_{v}")] for v in VLANS]
        await query.edit_message_text("Pilih VLAN", reply_markup=InlineKeyboardMarkup(buttons))
        return

    if data.startswith("reg_vlan_") and reg:
        reg["vlan"] = data.replace("reg_vlan_", "")
        context.user_data.pop("reg", None)
        await query.edit_message_text("⏳ Registrasi ONU...")
        try:
            onu_id = await run_blocking(
                register_onu, reg["pon"], reg["sn"], reg["name"], reg["package"],
                reg["vlan"], reg["mode"], reg.get("pppoe_user", ""), reg.get("pppoe_pass", ""),
            )
            await query.edit_message_text(
                f"✅ REGISTRASI BERHASIL\n\nNAMA : {reg['name']}\nSN : {reg['sn']}\n"
                f"PON : {reg['pon']}\nONU : {onu_id}\nMODE : {reg['mode']}\n"
                f"VLAN : {reg['vlan']}\nPAKET : {reg['package']}"
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}")
        return

    if data.startswith("reg_") and not data.startswith(("reg_mode_", "reg_pkg_", "reg_vlan_")):
        try:
            onu = context.user_data["reg_list"][int(data.replace("reg_", ""))]
        except (KeyError, IndexError, ValueError):
            await query.answer("Data kedaluwarsa, ulangi registrasi", show_alert=True)
            return
        context.user_data["reg"] = dict(onu)
        context.user_data["step"] = "reg_name"
        await query.edit_message_text(f"SN : {onu['sn']}")
        await query.message.reply_text("Masukkan Nama Pelanggan")
        return
