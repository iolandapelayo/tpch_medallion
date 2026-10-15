"""Writes three small PNG flags (England, Spain, Catalonia) without external libraries."""
import struct
import sys
import zlib
from pathlib import Path

W, H = 60, 40


def png(path, pixel):
    rows = b"".join(b"\x00" + b"".join(bytes(pixel(x, y)) for x in range(W)) for y in range(H))
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b""))


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


WHITE, RED_EN = hexrgb("#FFFFFF"), hexrgb("#CE1124")
RED_ES, YELLOW_ES = hexrgb("#AA151B"), hexrgb("#F1BF00")
RED_CA, YELLOW_CA = hexrgb("#DA121A"), hexrgb("#FCDD09")

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
# England: St George's cross
png(out / "flag_en.png", lambda x, y: RED_EN if abs(x - W / 2 + 0.5) < 4 or abs(y - H / 2 + 0.5) < 4 else WHITE)
# Spain: red / yellow (double height) / red
png(out / "flag_es.png", lambda x, y: YELLOW_ES if H / 4 <= y < 3 * H / 4 else RED_ES)
# Catalonia: nine stripes, yellow first (four red stripes)
png(out / "flag_ca.png", lambda x, y: RED_CA if int(y * 9 / H) % 2 else YELLOW_CA)
print("flags written to", out)
