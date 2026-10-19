"""
Test Script - APRS Bot Ilmu Informatika UKDC

Menguji semua modul tanpa perlu koneksi APRS-IS.
Jalankan: python test_bot.py
"""

import os
import sys

# Pastikan path benar
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Test konfigurasi."""
    print("\n" + "=" * 50)
    print("TEST 1: Konfigurasi")
    print("=" * 50)
    from config import (
        CALLSIGN, SERVER, PORT, MODULES_DIR, IMAGES_DIR,
        LOGS_DIR, GENERATED_CARDS_DIR, EVENTS_2026, TIMEZONE
    )

    print(f"  Callsign       : {CALLSIGN}")
    print(f"  Server         : {SERVER}:{PORT}")
    print(f"  Modules Dir    : {MODULES_DIR} (exists: {os.path.isdir(MODULES_DIR)})")
    print(f"  Images Dir     : {IMAGES_DIR} (exists: {os.path.isdir(IMAGES_DIR)})")
    print(f"  Logs Dir       : {LOGS_DIR} (exists: {os.path.isdir(LOGS_DIR)})")
    print(f"  Cards Dir      : {GENERATED_CARDS_DIR} (exists: {os.path.isdir(GENERATED_CARDS_DIR)})")
    print(f"  Timezone       : {TIMEZONE}")
    print(f"  Events 2026    : {len(EVENTS_2026)} event(s)")

    for key, event in EVENTS_2026.items():
        print(f"    - {key}: {event['name']} ({event['date']})")
        print(f"      Trigger: {event['command_trigger']}")
        print(f"      Image: {event['image']} (exists: {os.path.exists(event['image'])})")

    print("  ✅ Config OK\n")


def test_event_manager():
    """Test event manager."""
    print("=" * 50)
    print("TEST 2: Event Manager")
    print("=" * 50)
    from event_manager import (
        get_active_events, get_event_by_trigger,
        get_all_triggers, get_event_info
    )

    triggers = get_all_triggers()
    print(f"  All triggers   : {triggers}")

    active = get_active_events()
    print(f"  Active events  : {len(active)}")
    for key, event in active:
        print(f"    - {event['name']}")

    key, event = get_event_by_trigger("tahunbaru")
    print(f"  Trigger 'tahunbaru' : {key} -> {event['name'] if event else 'NOT FOUND'}")

    info = get_event_info("tahun_baru")
    print(f"  Event info     : {info}")

    print("  ✅ Event Manager OK\n")


def test_statistics():
    """Test statistik."""
    print("=" * 50)
    print("TEST 3: Statistik")
    print("=" * 50)
    from statistics import (
        log_callsign, log_event, get_statistics_summary,
        format_stats_report, get_callsign_history, export_full_report
    )

    # Simulasi beberapa callsign
    test_calls = [
        ("YB3ABC-9", "Tahun Baru 2026", "tahunbaru"),
        ("YB7XYZ-5", "Tahun Baru 2026", "tahunbaru"),
        ("YB3ABC-9", "Tahun Baru 2026", "tahunbaru"),
        ("YC1DEF-7", "Tahun Baru 2026", "tahunbaru"),
        ("YB7XYZ-5", "Tahun Baru 2026", "stats"),
    ]

    print("  Logging test callsigns...")
    for cs, event, msg in test_calls:
        log_callsign(cs, event, msg)
        log_event("TEST", cs, f"Test message: {msg}")
        print(f"    Logged: {cs} -> {event}")

    # Ringkasan
    stats = get_statistics_summary()
    print(f"\n  Total Pesan    : {stats['total_messages']}")
    print(f"  Callsign Unik  : {stats['unique_callsigns']}")
    print(f"  Top Callsigns  : {stats['top_callsigns']}")
    print(f"  Events Count   : {stats['events_count']}")
    print(f"  All Callsigns  : {stats['callsign_list']}")

    # History
    history = get_callsign_history("YB3ABC-9")
    print(f"\n  History YB3ABC-9: {len(history)} entries")

    # Format report
    report = format_stats_report()
    print(f"\n  APRS Report:\n    {report}")

    # Export full report
    report_path = export_full_report()
    print(f"\n  Full report exported to: {report_path}")

    print("  ✅ Statistics OK\n")


def test_card_generator():
    """Test pembuat kartu ucapan."""
    print("=" * 50)
    print("TEST 4: Card Generator")
    print("=" * 50)
    from card_generator import generate_personalized_card
    from config import EVENTS_2026

    event_config = EVENTS_2026["tahun_baru"]
    test_callsign = "YB3TEST-9"

    print(f"  Generating card for: {test_callsign}")
    print(f"  Event: {event_config['name']}")
    print(f"  Base image: {event_config['image']}")

    card_path = generate_personalized_card(test_callsign, event_config)

    if card_path and os.path.exists(card_path):
        size = os.path.getsize(card_path)
        print(f"  Card generated: {card_path}")
        print(f"  File size: {size:,} bytes")
        print("  ✅ Card Generator OK\n")
    else:
        print("  ⚠️ Card generation returned None (check errors above)\n")


def test_command_modules():
    """Test command modules."""
    print("=" * 50)
    print("TEST 5: Command Modules")
    print("=" * 50)

    # Test tahunbaru
    from modules.tahunbaru import handle_command as tahunbaru_cmd
    result = tahunbaru_cmd(from_call="YB3TEST-9")
    print(f"  tahunbaru -> {result[:80]}...")

    # Test stats
    from modules.stats import handle_command as stats_cmd
    result = stats_cmd(from_call="YB3TEST-9")
    print(f"  stats     -> {result[:80]}...")

    # Test help
    from modules.help import handle_command as help_cmd
    result = help_cmd(from_call="YB3TEST-9")
    print(f"  help      -> {result[:80]}...")

    # Test report
    from modules.report import handle_command as report_cmd
    result = report_cmd(from_call="YB3TEST-9")
    print(f"  report    -> {result[:80]}...")

    print("  ✅ Command Modules OK\n")


def test_module_loading():
    """Test dynamic module loading."""
    print("=" * 50)
    print("TEST 6: Dynamic Module Loading")
    print("=" * 50)

    # Simulasi load_commands dari main.py
    import importlib
    from config import MODULES_DIR

    loaded = {}
    for filename in os.listdir(MODULES_DIR):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f"modules.{module_name}")
                if hasattr(module, "handle_command"):
                    loaded[module_name] = module.handle_command
                    print(f"    Loaded: {module_name}")
            except Exception as e:
                print(f"    ERROR: {module_name} - {e}")

    print(f"\n  Total loaded: {len(loaded)} modules")
    print(f"  Commands: {', '.join(loaded.keys())}")
    print("  ✅ Module Loading OK\n")


if __name__ == "__main__":
    print("\n" + "🎯" * 25)
    print("  APRS BOT TEST SUITE")
    print("  Ilmu Informatika UKDC")
    print("🎯" * 25)

    try:
        test_config()
        test_event_manager()
        test_statistics()
        test_card_generator()
        test_command_modules()
        test_module_loading()

        print("=" * 50)
        print("✅ SEMUA TEST BERHASIL!")
        print("=" * 50)
        print("\nBot siap dijalankan dengan: python main.py")
        print("Pastikan CALLSIGN dan PASSCODE sudah dikonfigurasi di config.py\n")

    except Exception as e:
        print(f"\n❌ TEST GAGAL: {e}")
        import traceback
        traceback.print_exc()
