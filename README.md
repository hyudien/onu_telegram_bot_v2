# ONU Telegram Bot v2

Bot untuk manajemen OLT (Optical Line Terminal) dan MikroTik infrastructure melalui Telegram.

## Fitur

### OLT Management
- 📊 Status monitoring ONU per PON
- 🔍 Pencarian pelanggan berdasarkan nama/SN/PPPoE user
- 📝 Registrasi ONU baru
- 🔄 Change package
- 🔑 Change PPPoE credentials
- 🔄 Ganti ONU
- 🗑️ Delete ONU
- 🌐 Enable remote access
- 💾 Save configuration
- 🔄 Sync database

### MikroTik Management
- 📊 Status monitoring (CPU, RAM, Users)
- ➕ Tambah user PPPoE
- 🗑️ Hapus user
- ✏️ Edit user (password, profile, comment)
- 🟢 Lihat user online
- 🔴 Lihat user offline

## Setup Cepat

### 1. Clone Repository
```bash
git clone https://github.com/hyudien/onu_telegram_bot_v2.git
cd onu_telegram_bot_v2
```

### 2. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```bash
cp .env.example .env
# Edit .env dengan text editor dan isi:
# - BOT_TOKEN: dari BotFather di Telegram
# - ADMIN_ID: User ID Anda di Telegram
```

Untuk mendapatkan BOT_TOKEN:
1. Chat @BotFather di Telegram
2. Gunakan `/newbot` untuk membuat bot baru
3. Copy token yang diberikan

Untuk mendapatkan ADMIN_ID:
1. Chat @userinfobot di Telegram
2. Bot akan menampilkan ID Anda

### 5. Run Bot
```bash
python main.py
```

## Struktur Project

```
onu_telegram_bot_v2/
├── app/
│   ├── __init__.py
│   ├── bot.py              # Entry point aplikasi
│   └── config.py           # Config & environment variables
├── handlers/
│   ├── __init__.py
│   ├── start.py            # Handler untuk /start & access control
│   ├── mikrotik.py         # Handler untuk MikroTik operations
│   └── olt.py              # Handler untuk OLT operations
├── data/
│   ├── __init__.py
│   ├── allowed_users.json  # Daftar user yang diizinkan
│   ├── customer_db.py      # Database customer
│   ├── customer_*.json     # Data customer backup
│   ├── mikrotik_routers.py # Daftar router MikroTik
│   ├── modes.py            # Mode ONU (BRIDGE, PPPOE, PPPOE+BRIDGE)
│   ├── mt_profiles.py      # Profile MikroTik
│   ├── onu_types.py        # Tipe ONU
│   ├── packages.py         # Package/Paket kecepatan
│   ├── pons.py             # Daftar PON
│   ├── users.py            # User management
│   ├── vlans.py            # VLAN configuration
│   └── vlan_profiles.py    # VLAN profiles
├── mikrotik/
│   ├── __init__.py
│   ├── actions.py          # CRUD operations
│   ├── api.py              # API wrapper
│   ├── config.py           # Config MikroTik
│   ├── koneksi.py          # Connection handler
│   ├── status.py           # Status monitoring
│   └── users.py            # User management
├── olt/
│   ├── __init__.py
│   ├── change_onu.py       # Change ONU logic
│   ├── change_package.py   # Change package logic
│   ├── change_pppoe.py     # Change PPPoE logic
│   ├── delete_onu.py       # Delete ONU logic
│   ├── find_onu_id.py      # Find free ONU ID
│   ├── get_onu_config.py   # Get ONU configuration
│   ├── get_onu_info.py     # Get ONU information
│   ├── get_status.py       # Get status monitoring
│   ├── parser.py           # Parse CLI output
│   ├── reboot_onu.py       # Reboot ONU
│   ├── register_onu.py     # Register ONU logic
│   ├── templates.py        # Templates
│   └── zte.py              # ZTE OLT specifics
├── sync_discovery.py       # Sync discovery script
├── sync_olt_db.py          # Sync OLT database
├── sync_pppoe.py           # Sync PPPoE config
├── main.py                 # Main entry point
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Konfigurasi

### Bot Access Control
Saat pertama kali user menggunakan bot:
1. User menjalankan `/start`
2. Bot mengirim request ke ADMIN_ID
3. Admin bisa approve atau reject dengan tombol
4. Hanya user yang approved bisa menggunakan bot

### Data Files
Data pelanggan disimpan di `data/customers.json`

Format:
```json
[
  {
    "name": "Pelanggan 1",
    "sn": "GPHF1234567",
    "pon": "gpon-olt_0/1_0",
    "onu_id": "1",
    "vlan": "100",
    "mode": "PPPOE",
    "package": "10M",
    "pppoe_user": "user1@isp",
    "pppoe_pass": "password123",
    "onu_type": "ALL-ONT",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

## Troubleshooting

### Bot tidak start
- Pastikan BOT_TOKEN sudah benar
- Pastikan file `.env` ada di root folder
- Check log untuk error message

### Access denied
- Pastikan ADMIN_ID sudah benar
- Pastikan user sudah di-approve oleh admin
- Check `data/allowed_users.json`

### OLT/MikroTik connection error
- Pastikan OLT/MikroTik dapat diakses dari server
- Check koneksi network
- Verify credentials di config file

## Development

### Adding New Handler
1. Buat function baru di `handlers/`
2. Import di `app/bot.py`
3. Add handler ke Application

### Adding New Data Model
1. Buat file baru di `data/`
2. Define data structure
3. Import di handler yang memerlukan

## Security Notes

⚠️ **Jangan pernah commit `.env` ke repository!**

- `.env` sudah di-list di `.gitignore`
- Gunakan `.env.example` sebagai template
- Simpan credentials dengan aman
- Jangan share BOT_TOKEN ke orang lain

## Support & Issues

Jika ada masalah atau pertanyaan, silakan buat issue di repository.

## License

MIT License - feel free to use and modify

## Changelog

### v2.0.0 (Current)
- ✨ Clean architecture dengan modular design
- 🔐 Security improvements (environment variables)
- 🧹 Remove unused code dan cleanup
- 📝 Better documentation
- 🐛 Fix bug di logic edit comment
- 🚀 Performance improvements

### v1.0.0
- Initial release
