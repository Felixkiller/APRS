"""
Modul Event Manager - APRS Bot Ilmu Informatika UKDC

Mengelola event/perayaan:
- Menentukan event mana yang sedang aktif berdasarkan tanggal
- Menyediakan informasi event
- Mencocokkan command trigger dengan event
"""

from datetime import datetime, date

from config import EVENTS_2026, TIMEZONE


def _get_local_date():
    """Mendapatkan tanggal lokal WIB."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo(TIMEZONE)).date()
    except ImportError:
        from datetime import timedelta, timezone
        wib = timezone(timedelta(hours=7))
        return datetime.now(wib).date()


def get_active_events():
    """
    Mendapatkan daftar event yang sedang aktif saat ini.

    Returns:
        list: Daftar tuple (event_key, event_config) yang aktif
    """
    today = _get_local_date()
    active = []

    for key, event in EVENTS_2026.items():
        start = date.fromisoformat(event["date_start"])
        end = date.fromisoformat(event["date_end"])
        if start <= today <= end:
            active.append((key, event))

    return active


def get_event_by_trigger(trigger):
    """
    Mendapatkan event berdasarkan command trigger.

    Args:
        trigger: Teks command trigger (case-insensitive)

    Returns:
        tuple: (event_key, event_config) atau (None, None) jika tidak ditemukan
    """
    trigger_lower = trigger.lower().strip()

    for key, event in EVENTS_2026.items():
        if event.get("command_trigger", "").lower() == trigger_lower:
            return key, event

    return None, None


def get_event_by_key(event_key):
    """
    Mendapatkan event berdasarkan key.

    Args:
        event_key: Key event di EVENTS_2026

    Returns:
        dict: Konfigurasi event atau None
    """
    return EVENTS_2026.get(event_key)


def get_all_triggers():
    """
    Mendapatkan daftar semua command triggers yang tersedia.

    Returns:
        list: Daftar string trigger commands
    """
    triggers = []
    for key, event in EVENTS_2026.items():
        trigger = event.get("command_trigger", "")
        if trigger:
            triggers.append(trigger)
    return triggers


def get_event_info(event_key):
    """
    Mendapatkan informasi ringkas tentang event.

    Args:
        event_key: Key event

    Returns:
        str: Informasi event dalam format teks
    """
    event = EVENTS_2026.get(event_key)
    if not event:
        return "Event tidak ditemukan."

    return (
        f"Event: {event['name']} | "
        f"Tanggal: {event['date']} | "
        f"Command: {event.get('command_trigger', '-')}"
    )


def is_event_active(event_key):
    """
    Cek apakah event tertentu sedang aktif.

    Args:
        event_key: Key event di EVENTS_2026

    Returns:
        bool: True jika event aktif
    """
    event = EVENTS_2026.get(event_key)
    if not event:
        return False

    today = _get_local_date()
    start = date.fromisoformat(event["date_start"])
    end = date.fromisoformat(event["date_end"])

    return start <= today <= end
