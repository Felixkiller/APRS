# APRS Bot - Ilmu Informatika UKDC 🎓

Bot APRS (Automatic Packet Reporting System) untuk perayaan-perayaan tertentu di tahun 2026,
khusus untuk **Ilmu Informatika UKDC** - Universitas Katolik Darma Cendika.

## ✨ Fitur

- 📡 **Koneksi APRS-IS** - Terhubung ke jaringan APRS-IS untuk menerima dan mengirim pesan
- 📨 **Penerimaan Call Sign** - Menerima pesan dari pengirim beserta call sign-nya
- 🎴 **Kartu Ucapan Personalized** - Membuat gambar ucapan perayaan dengan call sign pengirim
- 📊 **Statistik Call Sign** - Mencatat dan melaporkan statistik interaksi pengirim
- 🎉 **Event-Based** - Mendukung perayaan yang bisa dikonfigurasi per tanggal

## 🎊 Perayaan Tahun 2026

| No | Perayaan | Tanggal | Command |
|----|----------|---------|---------|
| 1 | Tahun Baru 2026 | 1 Januari 2026 | `tahunbaru` |

> **Catatan:** Perayaan bisa ditambahkan melalui file `config.py`

## 📋 Prasyarat

- Python 3.9+ (untuk `zoneinfo`) atau Python 3.7+ (dengan fallback)
- Library yang diperlukan:
  - `aprslib` - Koneksi APRS-IS
  - `Pillow` - Pembuatan gambar kartu ucapan

## ⚙️ Instalasi

1. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd APRSBot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Konfigurasi:**
   Edit file `config.py` dan sesuaikan:
   ```python
   CALLSIGN = "YOURCALL"    # Call sign APRS Anda
   PASSCODE = "12345"       # Passcode APRS-IS Anda
   ```

## 🚀 Menjalankan Bot

```bash
python main.py
```

Bot akan:
1. Terhubung ke server APRS-IS
2. Mendengarkan pesan yang ditujukan ke call sign bot
3. Memproses perintah yang masuk
4. Mengirim balasan dan menghasilkan kartu ucapan

## 📡 Perintah yang Tersedia

| Perintah | Deskripsi |
|----------|-----------|
| `tahunbaru` | Ucapan Tahun Baru 2026 + kartu ucapan personalized |
| `stats` | Tampilkan ringkasan statistik call sign |
| `help` | Daftar perintah yang tersedia |
| `report` | Generate laporan statistik lengkap (file .txt) |

## 📁 Struktur Proyek

```
APRSBot/
├── main.py                 # Program utama bot
├── config.py               # Konfigurasi (callsign, events, paths)
├── event_manager.py        # Manajemen event/perayaan
├── card_generator.py       # Pembuat kartu ucapan personalized
├── statistics.py           # Pencatatan & pelaporan statistik
├── requirements.txt        # Dependencies
├── modules/                # Command modules
│   ├── __init__.py
│   ├── tahunbaru.py        # Command: Tahun Baru
│   ├── stats.py            # Command: Statistik
│   ├── help.py             # Command: Bantuan
│   ├── report.py           # Command: Laporan
│   └── images/             # Gambar perayaan
│       └── new_year_2026.jpg
├── generated_cards/        # Output kartu ucapan personalized
├── logs/                   # File log & statistik
│   ├── statistics.csv      # Log call sign pengirim
│   └── event_log.csv       # Log aktivitas bot
└── commands/               # (Legacy) command modules lama
```

## 📊 Statistik & Laporan

### File CSV Otomatis
Bot secara otomatis mencatat ke:
- `logs/statistics.csv` - Setiap interaksi call sign
- `logs/event_log.csv` - Setiap aktivitas bot

### Format CSV Statistik
```csv
timestamp,callsign,event,message
2026-01-01 00:05:23,YB3ABC,Tahun Baru 2026,tahunbaru
2026-01-01 00:12:45,YB7XYZ,Tahun Baru 2026,tahunbaru
```

### Laporan Teks
Kirim perintah `report` ke bot untuk menghasilkan laporan lengkap di folder `logs/`.

## 🎴 Kartu Ucapan

Setiap kali pengirim mengirimkan perintah perayaan, bot akan:
1. Membuat gambar kartu ucapan dengan call sign pengirim
2. Menyimpan kartu di folder `generated_cards/`
3. Membalas dengan pesan ucapan via APRS

## 🔧 Menambahkan Perayaan Baru

Edit `config.py` dan tambahkan entry baru di `EVENTS_2026`:

```python
EVENTS_2026 = {
    "event_baru": {
        "name": "Nama Perayaan",
        "date": "2026-MM-DD",
        "date_start": "2026-MM-DD",
        "date_end": "2026-MM-DD",
        "greeting": "Pesan ucapan...",
        "image": os.path.join(IMAGES_DIR, "nama_gambar.jpg"),
        "command_trigger": "commandname",
    },
}
```

Kemudian buat file command module di `modules/commandname.py`.

## 📝 Lisensi

Open source untuk keperluan edukasi Ilmu Informatika UKDC.

## 🏫 Informasi

**Ilmu Informatika UKDC**
Universitas Katolik Darma Cendika
Surabaya, Indonesia
