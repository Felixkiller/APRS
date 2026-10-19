"""
Modul Statistik APRS Bot - Ilmu Informatika UKDC

Mengelola pencatatan dan pelaporan statistik:
- Mencatat setiap call sign pengirim ke file CSV
- Menyediakan ringkasan statistik
- Mendukung export laporan
"""

import csv
import os
import threading
from datetime import datetime
from collections import Counter

from config import STATS_FILE, EVENT_LOG_FILE, TIMEZONE

# Lock untuk thread-safe file operations
_stats_lock = threading.Lock()


def _get_local_time():
    """Mendapatkan waktu lokal WIB."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo(TIMEZONE))
    except ImportError:
        # Fallback jika zoneinfo tidak tersedia (Python < 3.9)
        from datetime import timedelta, timezone
        wib = timezone(timedelta(hours=7))
        return datetime.now(wib)


def _init_csv(filepath, headers):
    """Inisialisasi file CSV jika belum ada."""
    if not os.path.exists(filepath):
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)


def log_callsign(callsign, event_name, message_text=""):
    """
    Mencatat call sign pengirim ke file statistik CSV.

    Args:
        callsign: Call sign pengirim APRS
        event_name: Nama event/perayaan yang aktif
        message_text: Teks pesan yang diterima
    """
    with _stats_lock:
        _init_csv(STATS_FILE, [
            "timestamp", "callsign", "event", "message"
        ])
        now = _get_local_time()
        with open(STATS_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                now.strftime("%Y-%m-%d %H:%M:%S"),
                callsign,
                event_name,
                message_text,
            ])
        print(f"[STATS] Logged: {callsign} -> {event_name}")


def log_event(event_type, callsign, details=""):
    """
    Mencatat event/aktivitas bot ke event log CSV.

    Args:
        event_type: Tipe event (RECEIVED, REPLIED, ACK, ERROR)
        callsign: Call sign terkait
        details: Detail tambahan
    """
    with _stats_lock:
        _init_csv(EVENT_LOG_FILE, [
            "timestamp", "event_type", "callsign", "details"
        ])
        now = _get_local_time()
        with open(EVENT_LOG_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                now.strftime("%Y-%m-%d %H:%M:%S"),
                event_type,
                callsign,
                details,
            ])


def get_statistics_summary():
    """
    Menghasilkan ringkasan statistik dari file CSV.

    Returns:
        dict: Ringkasan statistik berisi:
            - total_messages: Jumlah total pesan
            - unique_callsigns: Jumlah call sign unik
            - top_callsigns: 10 call sign paling aktif
            - events_count: Jumlah pesan per event
            - callsign_list: Daftar semua call sign unik
    """
    stats = {
        "total_messages": 0,
        "unique_callsigns": 0,
        "top_callsigns": [],
        "events_count": {},
        "callsign_list": [],
    }

    if not os.path.exists(STATS_FILE):
        return stats

    callsigns = []
    events = []

    with open(STATS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            callsigns.append(row.get("callsign", ""))
            events.append(row.get("event", ""))

    if not callsigns:
        return stats

    callsign_counter = Counter(callsigns)
    event_counter = Counter(events)

    stats["total_messages"] = len(callsigns)
    stats["unique_callsigns"] = len(set(callsigns))
    stats["top_callsigns"] = callsign_counter.most_common(10)
    stats["events_count"] = dict(event_counter)
    stats["callsign_list"] = sorted(set(callsigns))

    return stats


def get_callsign_history(callsign):
    """
    Mendapatkan riwayat interaksi untuk call sign tertentu.

    Args:
        callsign: Call sign yang dicari

    Returns:
        list: Daftar interaksi call sign tersebut
    """
    history = []

    if not os.path.exists(STATS_FILE):
        return history

    with open(STATS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("callsign", "").upper() == callsign.upper():
                history.append(row)

    return history


def format_stats_report():
    """
    Format laporan statistik sebagai string yang bisa dikirim via APRS.

    Returns:
        str: Laporan statistik dalam format teks
    """
    stats = get_statistics_summary()

    report_lines = [
        f"=== STATISTIK APRS BOT ===",
        f"Ilmu Informatika UKDC",
        f"Total Pesan: {stats['total_messages']}",
        f"Callsign Unik: {stats['unique_callsigns']}",
    ]

    if stats["top_callsigns"]:
        report_lines.append("--- Top Callsigns ---")
        for i, (cs, count) in enumerate(stats["top_callsigns"][:5], 1):
            report_lines.append(f"{i}. {cs}: {count}x")

    if stats["events_count"]:
        report_lines.append("--- Per Event ---")
        for event, count in stats["events_count"].items():
            report_lines.append(f"  {event}: {count}")

    return " | ".join(report_lines)


def export_full_report(output_path=None):
    """
    Export laporan statistik lengkap ke file teks.

    Args:
        output_path: Path file output (default: logs/report_YYYYMMDD.txt)

    Returns:
        str: Path file report yang dihasilkan
    """
    if output_path is None:
        now = _get_local_time()
        output_path = os.path.join(
            os.path.dirname(STATS_FILE),
            f"report_{now.strftime('%Y%m%d_%H%M%S')}.txt"
        )

    stats = get_statistics_summary()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("  LAPORAN STATISTIK APRS BOT\n")
        f.write("  Ilmu Informatika UKDC\n")
        f.write("  Universitas Katolik Darma Cendika\n")
        f.write("=" * 60 + "\n\n")

        now = _get_local_time()
        f.write(f"Tanggal Laporan : {now.strftime('%d %B %Y %H:%M:%S WIB')}\n")
        f.write(f"Total Pesan     : {stats['total_messages']}\n")
        f.write(f"Callsign Unik   : {stats['unique_callsigns']}\n\n")

        f.write("-" * 60 + "\n")
        f.write("  TOP 10 CALLSIGN PALING AKTIF\n")
        f.write("-" * 60 + "\n")
        if stats["top_callsigns"]:
            f.write(f"{'No':>4}  {'Callsign':<12}  {'Jumlah':>8}\n")
            f.write(f"{'----':>4}  {'--------':<12}  {'------':>8}\n")
            for i, (cs, count) in enumerate(stats["top_callsigns"], 1):
                f.write(f"{i:>4}  {cs:<12}  {count:>8}\n")
        else:
            f.write("  Belum ada data.\n")

        f.write("\n" + "-" * 60 + "\n")
        f.write("  STATISTIK PER EVENT\n")
        f.write("-" * 60 + "\n")
        if stats["events_count"]:
            for event, count in stats["events_count"].items():
                f.write(f"  {event:<30}  {count:>6} pesan\n")
        else:
            f.write("  Belum ada data.\n")

        f.write("\n" + "-" * 60 + "\n")
        f.write("  DAFTAR SEMUA CALLSIGN\n")
        f.write("-" * 60 + "\n")
        if stats["callsign_list"]:
            for i, cs in enumerate(stats["callsign_list"], 1):
                f.write(f"  {i:>4}. {cs}\n")
        else:
            f.write("  Belum ada data.\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write("  Akhir Laporan\n")
        f.write("=" * 60 + "\n")

    print(f"[STATS] Report exported to: {output_path}")
    return output_path
