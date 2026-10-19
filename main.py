"""
APRS Bot - Ilmu Informatika UKDC
Universitas Katolik Darma Cendika

Bot APRS untuk perayaan-perayaan tertentu di tahun 2026.
Fitur:
  - Menerima Call Sign dari pengirim
  - Membalas dengan ucapan perayaan + gambar personalized
  - Mencatat statistik call sign pengirim
  - Mendukung command: tahutek, stats, help, report

Penggunaan:
  1. Edit config.py - sesuaikan CALLSIGN dan PASSCODE
  2. Jalankan: python main.py
  3. Kirim pesan APRS ke bot dengan perintah yang tersedia
"""

import sys

try:
    import aprslib  # type: ignore[import-not-found]
except ImportError:
    aprslib = None
    print("[BOOT] WARNING: aprslib is not installed. Install it with: pip install aprslib", file=sys.stderr)

import threading
import queue
import time
import importlib
import os

from config import CALLSIGN, PASSCODE, SERVER, PORT, MODULES_DIR
from event_manager import get_active_events, get_event_by_trigger
from statistics import log_callsign, log_event, export_full_report
from card_generator import generate_personalized_card

# ============================================================
# Global Variables
# ============================================================

# List of received message IDs to avoid duplicate ACKs
received_msgs = set()

# Dictionary to hold command functions
command_functions = {}

# APRS client (global reference)
client = None


# ============================================================
# Module Loading
# ============================================================

def load_commands():
    """
    Dynamically load command modules from the modules folder.
    Setiap modul harus memiliki fungsi handle_command(from_call=None).
    """
    global command_functions
    command_functions = {}

    if not os.path.isdir(MODULES_DIR):
        print(f"[LOAD] WARNING: Modules directory not found: {MODULES_DIR}")
        return

    # Tambahkan modules dir ke sys.path jika belum ada
    if MODULES_DIR not in sys.path:
        sys.path.insert(0, os.path.dirname(MODULES_DIR))

    for filename in os.listdir(MODULES_DIR):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            try:
                # Import module dari folder modules
                module = importlib.import_module(f"modules.{module_name}")
                if hasattr(module, "handle_command"):
                    command_functions[module_name] = module.handle_command
                    print(f"[LOAD] Loaded command: {module_name}")
                else:
                    print(f"[LOAD] WARNING: Module '{module_name}' has no 'handle_command' function")
            except Exception as e:
                print(f"[LOAD] ERROR loading '{module_name}': {e}")

    print(f"[LOAD] Total commands loaded: {len(command_functions)}")
    print(f"[LOAD] Available commands: {', '.join(command_functions.keys())}")


# ============================================================
# APRS Message Handling
# ============================================================

def send_ack(aprs_client, msgNo, to_call):
    """
    Mengirim ACK (acknowledgment) untuk pesan yang diterima.

    Args:
        aprs_client: APRS-IS client instance
        msgNo: Nomor pesan yang di-ACK
        to_call: Call sign tujuan ACK
    """
    to_call_padded = f"{to_call:<9}"
    if any(char.isalpha() for char in str(msgNo)):
        msgNo = f"{msgNo}}}"
    ack_message = f"{CALLSIGN}>APRS::{to_call_padded}:ack{msgNo}"
    try:
        print(f"[ACK] Sending: {ack_message}")
        aprs_client.sendall(ack_message)
        print(f"[ACK] Sent for message {msgNo} to {to_call}")
        log_event("ACK_SENT", to_call, f"msgNo: {msgNo}")
        time.sleep(5)
    except Exception as e:
        print(f"[ACK] Error: {e}")
        log_event("ERROR", to_call, f"ACK error: {e}")


def send_response(aprs_client, to_call, response_message):
    """
    Mengirim pesan balasan ke pengirim, dengan splitting otomatis
    agar tidak melebihi batas panjang pesan APRS.

    Args:
        aprs_client: APRS-IS client instance
        to_call: Call sign tujuan
        response_message: Pesan balasan
    """
    to_call_padded = f"{to_call:<9}"

    def split_message(message, max_length=48):
        """Split message pada spasi agar tidak terpotong di tengah kata."""
        words = message.split()
        messages = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 > max_length:
                if current:
                    messages.append(current)
                current = word
            else:
                current = f"{current} {word}".strip()
        if current:
            messages.append(current)
        return messages

    messages = split_message(response_message)

    for i, msg in enumerate(messages):
        response = f"{CALLSIGN}>APRS::{to_call_padded}:{msg}"
        try:
            print(f"[SEND] [{i+1}/{len(messages)}] {response}")
            aprs_client.sendall(response)
            print(f"[SEND] Response sent to {to_call}")
            log_event("RESPONSE_SENT", to_call, f"Part {i+1}/{len(messages)}: {msg[:30]}...")
        except Exception as e:
            print(f"[SEND] Error: {e}")
            log_event("ERROR", to_call, f"Send error: {e}")
        time.sleep(5)


def handle_packet(packet):
    """
    Callback function untuk memproses paket APRS yang masuk.

    Alur:
    1. Filter pesan yang ditujukan ke bot
    2. Kirim ACK
    3. Cocokkan dengan command yang tersedia
    4. Kirim balasan yang sesuai
    """
    print(f"[RECV] Packet: {packet}")

    # Hanya proses pesan yang ditujukan ke bot ini
    if "message_text" not in packet:
        return
    if packet.get("addresse", "").strip() != CALLSIGN:
        return

    from_call = packet.get("from", "UNKNOWN")
    msgNo = packet.get("msgNo", "")
    message_text = packet.get("message_text", "").strip()

    print(f"\n{'='*50}")
    print(f"[MSG] From: {from_call}")
    print(f"[MSG] Text: {message_text}")
    print(f"[MSG] MsgNo: {msgNo}")
    print(f"{'='*50}\n")

    # Log penerimaan pesan
    log_event("RECEIVED", from_call, f"Message: {message_text}")

    # Kirim ACK jika belum pernah
    if msgNo and msgNo not in received_msgs:
        received_msgs.add(msgNo)
        print(f"[ACK] Starting ACK thread for msgNo: {msgNo} from: {from_call}")
        threading.Thread(
            target=send_ack,
            args=(client, msgNo, from_call),
            daemon=True,
        ).start()

    # Cari dan eksekusi command yang sesuai
    message_lower = message_text.lower().strip()
    command_function = command_functions.get(message_lower)

    if command_function:
        try:
            # Panggil command handler dengan from_call
            import inspect
            sig = inspect.signature(command_function)
            if "from_call" in sig.parameters:
                response_message = command_function(from_call=from_call)
            else:
                response_message = command_function()

            if response_message:
                time.sleep(5)
                print(f"[CMD] Executing '{message_text}' from {from_call}")
                threading.Thread(
                    target=send_response,
                    args=(client, from_call, response_message),
                    daemon=True,
                ).start()
        except Exception as e:
            print(f"[CMD] Error executing command '{message_text}': {e}")
            log_event("ERROR", from_call, f"Command error: {e}")
    else:
        # Command tidak dikenali - kirim bantuan
        print(f"[CMD] Unknown command: '{message_text}' from {from_call}")
        log_event("UNKNOWN_CMD", from_call, f"Unknown: {message_text}")

        help_msg = (
            f"Hai {from_call}! Command tidak dikenali. "
            f"Ketik 'help' untuk daftar perintah. "
            f"APRS Bot Informatika UKDC."
        )
        time.sleep(5)
        threading.Thread(
            target=send_response,
            args=(client, from_call, help_msg),
            daemon=True,
        ).start()


# ============================================================
# Connection & Main
# ============================================================

def connect_to_aprs():
    """Menghubungkan ke jaringan APRS-IS."""
    global client
    if aprslib is None:
        raise SystemExit(
            "[BOOT] aprslib tidak tersedia. Jalankan "
            r".\.venv\Scripts\python.exe -m pip install -r requirements.txt "
            "lalu mulai bot dengan .\\.venv\\Scripts\\python.exe main.py"
        )

    client = aprslib.IS(CALLSIGN, PASSCODE, port=PORT)

    print(f"\n{'='*60}")
    print(f"  APRS Bot - Ilmu Informatika UKDC")
    print(f"  Universitas Katolik Darma Cendika")
    print(f"{'='*60}")
    print(f"  Callsign : {CALLSIGN}")
    print(f"  Server   : {SERVER}:{PORT}")
    print(f"  Commands : {', '.join(command_functions.keys())}")
    print(f"{'='*60}\n")

    # Filter pesan yang ditujukan ke bot (g/ = group message filter)
    client.set_filter(f"g/{CALLSIGN}")
    print(f"[CONN] Filter set: g/{CALLSIGN}")

    # Cek event yang sedang aktif
    active_events = get_active_events()
    if active_events:
        print(f"[EVENT] Active events:")
        for key, event in active_events:
            print(f"  - {event['name']} ({event['date']})")
    else:
        print(f"[EVENT] No active events at this time.")

    try:
        client.connect(SERVER, PORT)
        print(f"[CONN] Connected to APRS-IS server successfully!")
        print(f"[CONN] Listening for incoming messages...\n")
        client.consumer(handle_packet, raw=False)
    except aprslib.ConnectionDrop:
        print(f"[CONN] Connection dropped. Reconnecting in 30s...")
        time.sleep(30)
        connect_to_aprs()
    except aprslib.LoginError as e:
        print(f"[CONN] Login failed: {e}")
        print(f"[CONN] Please check CALLSIGN and PASSCODE in config.py")
    except Exception as e:
        print(f"[CONN] Error: {e}")
        print(f"[CONN] Reconnecting in 30s...")
        time.sleep(30)
        connect_to_aprs()


def print_banner():
    """Menampilkan banner startup."""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     █████╗ ██████╗ ██████╗ ███████╗    ██████╗  ██████╗ ║
║    ██╔══██╗██╔══██╗██╔══██╗██╔════╝    ██╔══██╗██╔═══██╗║
║    ███████║██████╔╝██████╔╝███████╗    ██████╔╝██║   ██║║
║    ██╔══██║██╔═══╝ ██╔══██╗╚════██║    ██╔══██╗██║   ██║║
║    ██║  ██║██║     ██║  ██║███████║    ██████╔╝╚██████╔╝║
║    ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚══════╝    ╚═════╝  ╚═════╝║
║                                                          ║
║           Ilmu Informatika UKDC - Tahun 2026             ║
║         Universitas Katolik Darma Cendika                ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


if __name__ == "__main__":
    print_banner()
    load_commands()
    connect_to_aprs()
