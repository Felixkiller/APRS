"""
Modul Pembuat Kartu Ucapan - APRS Bot Ilmu Informatika UKDC

Membuat gambar kartu ucapan yang dipersonalisasi dengan:
- Gambar perayaan sebagai background
- Call sign pengirim yang ditampilkan di gambar
- Watermark Ilmu Informatika UKDC
"""

import os
from datetime import datetime

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover - Pillow is optional at runtime
    Image = None
    ImageDraw = None
    ImageFont = None

from config import GENERATED_CARDS_DIR, TIMEZONE


def _get_local_time():
    """Mendapatkan waktu lokal WIB."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo(TIMEZONE))
    except ImportError:
        from datetime import timedelta, timezone
        wib = timezone(timedelta(hours=7))
        return datetime.now(wib)


def generate_personalized_card(callsign, event_config):
    """
    Membuat kartu ucapan yang dipersonalisasi dengan call sign pengirim.

    Menggunakan library Pillow (PIL) untuk menggabungkan gambar perayaan
    dengan teks call sign pengirim.

    Args:
        callsign: Call sign pengirim APRS
        event_config: Dictionary konfigurasi event dari EVENTS_2026

    Returns:
        str: Path ke file gambar yang dihasilkan, atau None jika gagal
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("[CARD] ERROR: Pillow library not installed. Run: pip install Pillow")
        return None

    event_name = event_config.get("name", "Event")
    base_image_path = event_config.get("image", "")

    if not os.path.exists(base_image_path):
        print(f"[CARD] WARNING: Base image not found: {base_image_path}")
        # Buat gambar fallback jika gambar dasar tidak ditemukan
        return _generate_fallback_card(callsign, event_config)

    try:
        # Buka gambar dasar
        img = Image.open(base_image_path).copy()
        draw = ImageDraw.Draw(img)
        width, height = img.size

        # Coba gunakan font yang tersedia
        font_large = _get_font(size=max(36, int(height * 0.05)))
        font_medium = _get_font(size=max(24, int(height * 0.035)))
        font_small = _get_font(size=max(18, int(height * 0.025)))

        # ---- Banner Call Sign di bagian bawah ----
        banner_height = int(height * 0.18)
        banner_y = height - banner_height

        # Buat semi-transparent overlay untuk banner
        overlay = Image.new("RGBA", (width, banner_height), (0, 0, 50, 200))
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        img.paste(overlay, (0, banner_y), overlay)

        draw = ImageDraw.Draw(img)

        # Teks call sign
        cs_text = f"Kepada: {callsign}"
        cs_bbox = draw.textbbox((0, 0), cs_text, font=font_large)
        cs_w = cs_bbox[2] - cs_bbox[0]
        cs_x = (width - cs_w) // 2
        cs_y = banner_y + int(banner_height * 0.15)

        # Shadow effect
        draw.text((cs_x + 2, cs_y + 2), cs_text, fill=(0, 0, 0, 200), font=font_large)
        # Teks utama
        draw.text((cs_x, cs_y), cs_text, fill=(255, 215, 0, 255), font=font_large)

        # Teks waktu
        now = _get_local_time()
        time_text = f"{now.strftime('%d %B %Y %H:%M WIB')}"
        time_bbox = draw.textbbox((0, 0), time_text, font=font_small)
        time_w = time_bbox[2] - time_bbox[0]
        time_x = (width - time_w) // 2
        time_y = cs_y + (cs_bbox[3] - cs_bbox[1]) + 10
        draw.text((time_x, time_y), time_text, fill=(200, 200, 200, 255), font=font_small)

        # Teks institusi
        inst_text = "Ilmu Informatika UKDC"
        inst_bbox = draw.textbbox((0, 0), inst_text, font=font_medium)
        inst_w = inst_bbox[2] - inst_bbox[0]
        inst_x = (width - inst_w) // 2
        inst_y = time_y + (time_bbox[3] - time_bbox[1]) + 5
        draw.text((inst_x, inst_y), inst_text, fill=(255, 255, 255, 255), font=font_medium)

        # ---- Simpan hasil ----
        safe_callsign = callsign.replace("/", "_").replace("\\", "_")
        event_key = event_config.get("command_trigger", "event")
        filename = f"{event_key}_{safe_callsign}_{now.strftime('%Y%m%d_%H%M%S')}.png"
        output_path = os.path.join(GENERATED_CARDS_DIR, filename)

        # Convert ke RGB jika perlu (untuk JPEG compatibility)
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (0, 0, 50))
            bg.paste(img, mask=img.split()[3])
            bg.save(output_path, quality=95)
        else:
            img.save(output_path, quality=95)

        print(f"[CARD] Generated: {output_path}")
        return output_path

    except Exception as e:
        print(f"[CARD] Error generating card: {e}")
        return _generate_fallback_card(callsign, event_config)


def _generate_fallback_card(callsign, event_config):
    """
    Membuat kartu ucapan sederhana jika gambar dasar tidak tersedia.

    Args:
        callsign: Call sign pengirim
        event_config: Konfigurasi event

    Returns:
        str: Path ke file gambar fallback
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("[CARD] ERROR: Pillow not available for fallback card")
        return None

    try:
        width, height = 800, 600
        img = Image.new("RGB", (width, height), (10, 10, 60))
        draw = ImageDraw.Draw(img)

        font_large = _get_font(size=40)
        font_medium = _get_font(size=28)
        font_small = _get_font(size=20)

        event_name = event_config.get("name", "Perayaan 2026")

        # Judul event
        title_bbox = draw.textbbox((0, 0), event_name, font=font_large)
        title_w = title_bbox[2] - title_bbox[0]
        draw.text(
            ((width - title_w) // 2, 80),
            event_name,
            fill=(255, 215, 0),
            font=font_large,
        )

        # Nama institusi
        inst = "Ilmu Informatika UKDC"
        inst_bbox = draw.textbbox((0, 0), inst, font=font_medium)
        inst_w = inst_bbox[2] - inst_bbox[0]
        draw.text(
            ((width - inst_w) // 2, 150),
            inst,
            fill=(255, 255, 255),
            font=font_medium,
        )

        # Call sign
        cs_text = f"Kepada: {callsign}"
        cs_bbox = draw.textbbox((0, 0), cs_text, font=font_large)
        cs_w = cs_bbox[2] - cs_bbox[0]
        draw.text(
            ((width - cs_w) // 2, 300),
            cs_text,
            fill=(255, 215, 0),
            font=font_large,
        )

        # Greeting
        greeting = event_config.get("greeting", "Selamat merayakan!")
        # Wrap greeting text
        words = greeting.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font_small)
            if bbox[2] - bbox[0] > width - 80:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)

        y_offset = 400
        for line in lines:
            line_bbox = draw.textbbox((0, 0), line, font=font_small)
            line_w = line_bbox[2] - line_bbox[0]
            draw.text(
                ((width - line_w) // 2, y_offset),
                line,
                fill=(200, 200, 200),
                font=font_small,
            )
            y_offset += 30

        # Simpan
        safe_callsign = callsign.replace("/", "_").replace("\\", "_")
        event_key = event_config.get("command_trigger", "event")
        now = _get_local_time()
        filename = f"{event_key}_{safe_callsign}_{now.strftime('')}.png"
        output_path = os.path.join(GENERATED_CARDS_DIR, filename)
        img.save(output_path, quality=95)

        print(f"[CARD] Fallback generated: {output_path}")
        return output_path

    except Exception as e:
        print(f"[CARD] Error generating fallback card: {e}")
        return None


def _get_font(size=24):
    """
    Mendapatkan font yang tersedia di sistem.

    Args:
        size: Ukuran font

    Returns:
        ImageFont: Font object
    """
    from PIL import ImageFont

    # Daftar font yang umum tersedia
    font_paths = [
        # Windows fonts
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
        # Linux fonts
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        # macOS fonts
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue

    # Fallback ke default font
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()
