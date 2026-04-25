"""
Logo'yu transparan arka plan + saf beyaz silüete dönüştürür.
PIPELINE: koyu pikselleri beyaza çevir > beyaz BG'yi şeffaf yap >
          bbox-crop ile boşlukları sıkıştır > minimal nefes payı ekle.
Sonuç: assets/logo-white.png  (her pikseli içerikle dolu, header'da maksimum boyut)
"""
from PIL import Image
from pathlib import Path

SRC = Path(__file__).parent / "logo (1).png"
DST = Path(__file__).parent / "logo-white.png"

BG_THRESHOLD = 200
EDGE_BOOST   = 1.4
PAD_X        = 24
PAD_Y        = 6

img = Image.open(SRC).convert("RGBA")
w, h = img.size
print(f"Source: {SRC.name}  ({w}x{h})  aspect {w/h:.3f}")

pixels = img.load()
silhouette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
out_px = silhouette.load()

white_count = 0
transparent_count = 0

for y in range(h):
    for x in range(w):
        r, g, b, _ = pixels[x, y]
        luminance = (r + g + b) / 3

        if luminance > BG_THRESHOLD:
            out_px[x, y] = (255, 255, 255, 0)
            transparent_count += 1
        else:
            opacity_ratio = 1 - (luminance / BG_THRESHOLD)
            alpha = min(255, int(255 * min(1, opacity_ratio * EDGE_BOOST)))
            out_px[x, y] = (255, 255, 255, alpha)
            white_count += 1

bbox = silhouette.getbbox()
if bbox is None:
    raise SystemExit("Logo boş çıktı, threshold'u kontrol et")

cropped = silhouette.crop(bbox)
cw, ch = cropped.size
print(f"Cropped: {cw}x{ch}  aspect {cw/ch:.3f}  (bbox: {bbox})")

new_w = cw + 2 * PAD_X
new_h = ch + 2 * PAD_Y
final = Image.new("RGBA", (new_w, new_h), (0, 0, 0, 0))
final.paste(cropped, (PAD_X, PAD_Y))

final.save(DST, "PNG", optimize=True)
print(f"Output:  {DST.name}  {new_w}x{new_h}  aspect {new_w/new_h:.3f}")
print(f"  white pixels: {white_count:,}")
print(f"  transparent:  {transparent_count:,}")
print(f"  size:         {DST.stat().st_size / 1024:.1f} KB")
