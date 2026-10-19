"""
Konfigurasi APRS Bot - Ilmu Informatika UKDC
Universitas Katolik Darma Cendika

Konfigurasi utama untuk APRS Bot perayaan tahun 2026.
"""

import os

# ============================================================
# APRS Login Details
# ============================================================
CALLSIGN = "YD3ADB-10"       # Call sign bot (SSID -10)
PASSCODE = "23973"            # Passcode APRS-IS untuk YD3ADB

# ============================================================
# APRS Server Settings
# ============================================================
SERVER = "rotate.aprs2.net"
PORT = 14580

# ============================================================
# Direktori
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(BASE_DIR, "modules")
IMAGES_DIR = os.path.join(MODULES_DIR, "images")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
GENERATED_CARDS_DIR = os.path.join(BASE_DIR, "generated_cards")
STATS_FILE = os.path.join(LOGS_DIR, "statistics.csv")
EVENT_LOG_FILE = os.path.join(LOGS_DIR, "event_log.csv")

# Pastikan semua direktori tersedia
for d in [MODULES_DIR, IMAGES_DIR, LOGS_DIR, GENERATED_CARDS_DIR]:
    os.makedirs(d, exist_ok=True)

# ============================================================
# Daftar Perayaan (Event) Tahun 2026
# Ilmu Informatika UKDC
# ============================================================
EVENTS_2026 = {
    "tahu_tek": {
        "name": "Tahu_Tek",
        "date": "2026-10-12",
        "date_start": "2026-10-12",  # Mulai aktif H-1
        "date_end": "2026-10-12",    # Berakhir H+1
        "greeting": "Salam Tahu Tek dari Ilmu Informatika UKDC! ",
        "image": os.path.join(IMAGES_DIR, "tahu_tek.jpg"),
        "command_trigger": "tahutek",
    },
}


# ============================================================
# Timezone
# ============================================================
TIMEZONE = "Asia/Jakarta"  # WIB (UTC+7)
