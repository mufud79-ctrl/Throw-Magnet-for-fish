#!/bin/sh
# Pull real gameplay frames for VFX reference from YouTube search results (no playback, no CAPTCHA bypass):
# for each query, take the top N video ids and download YouTube's published auto-frames (hq1/hq2/hq3 at 25/50/75%),
# then tile them into one contact sheet per query (rows = videos, cols = the 3 frames).
# usage: ref_frames.sh OUT_DIR N "query one" "query two" ...
# needs: curl, python3 with Pillow (/tmp/bpyenv/bin/python works)
OUT=$1; N=$2; shift 2
mkdir -p "$OUT"
PY=${PY:-/tmp/bpyenv/bin/python}
[ -x "$PY" ] || PY=python3
qi=0
for Q in "$@"; do
  qs=$(printf '%s' "$Q" | sed 's/ /+/g')
  ids=$(curl -s -A "Mozilla/5.0" "https://www.youtube.com/results?search_query=$qs" | grep -o '"videoId":"[A-Za-z0-9_-]\{11\}"' | sed 's/.*:"\(.*\)"/\1/' | awk '!s[$0]++' | head -n "$N")
  : > "$OUT/q$qi.ids"
  for id in $ids; do
    echo "$id" >> "$OUT/q$qi.ids"
    for k in 1 2 3; do curl -s -o "$OUT/${id}_$k.jpg" "https://i.ytimg.com/vi/$id/hq$k.jpg"; done
  done
  "$PY" -I - "$OUT" "$qi" "$Q" <<'PYEOF'
import sys, os
from PIL import Image, ImageDraw
out, qi, q = sys.argv[1], sys.argv[2], sys.argv[3]
ids = [l.strip() for l in open(os.path.join(out, f"q{qi}.ids")) if l.strip()]
if ids:
    W, H = 480, 270
    sheet = Image.new("RGB", (3 * W, len(ids) * H + 36), (16, 16, 20))
    d = ImageDraw.Draw(sheet); d.text((8, 10), q, fill=(255, 255, 255))
    for r, i in enumerate(ids):
        for k in range(3):
            p = os.path.join(out, f"{i}_{k+1}.jpg")
            try:
                im = Image.open(p).convert("RGB").crop((0, 45, 480, 315))
                sheet.paste(im, (k * W, 36 + r * H))
            except Exception:
                pass
    dst = os.path.join(out, f"sheet_{qi}.jpg"); sheet.save(dst, quality=85); print(dst)
PYEOF
  qi=$((qi + 1))
done
