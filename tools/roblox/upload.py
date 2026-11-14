"""Upload the showcase models to Roblox as Model assets via Open Cloud, recording IDs in game/asset_ids.json.

    export ROBLOX_API_KEY=...            # Open Cloud key with Assets: Read + Write
    export ROBLOX_USER_ID=12345          # or ROBLOX_GROUP_ID=67890 (use the owner of the place)
    python3 tools/roblox/upload.py --only Goldfish Anglerfish TreasureChest   # test batch
    python3 tools/roblox/upload.py                                             # everything else

Flags:
  --only NAME ...   upload just these names (from game/manifest.json)
  --dry-run         print what would be uploaded, touch nothing
  --format fbx|glb  source file (default fbx; the texture is embedded in both)
  --glb-fallback    if an FBX upload fails, retry that model with its .glb
  --force           re-upload names that already have an ID
  --delay SECONDS   pause between uploads (default 2; 429s back off on top of this)
  --inspect NAME .. download already-uploaded assets and list what Roblox built
                    (MeshParts, Bones, textures). Needs the key to also have
                    Legacy Assets: Manage (asset delivery) and network access to the CDN.

The ROBLOX_* variables can also live in a git-ignored .env file at the repo root.

Resumable: names already in asset_ids.json are skipped, and the file is rewritten after every
success, so an interrupted run loses nothing. Failures are logged to game/upload_failures.json
and the batch carries on. Standard library only.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "game" / "manifest.json"
IDS = ROOT / "game" / "asset_ids.json"
FAILS = ROOT / "game" / "upload_failures.json"
API = "https://apis.roblox.com/assets/v1"
DELIVERY = "https://apis.roblox.com/asset-delivery-api/v1/assetId/"
CTYPE = {"fbx": "model/fbx", "glb": "model/gltf-binary"}
POLL_EVERY, POLL_TIMEOUT = 2.0, 600


class ApiError(Exception):
    def __init__(self, status, body):
        super().__init__(f"HTTP {status}: {body[:500]}")
        self.status, self.body = status, body


def request(method, url, key, body=None, headers=None, retries=5):
    """JSON request with backoff on 429/5xx. Returns the parsed body."""
    hdrs = {"x-api-key": key, **(headers or {})}
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=body, method=method, headers=hdrs)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8", "replace")
            if (e.code == 429 or e.code >= 500) and attempt < retries:
                wait = float(e.headers.get("Retry-After") or 0) or min(60, 2 ** (attempt + 2))
                print(f"    HTTP {e.code}, retrying in {wait:.0f}s")
                time.sleep(wait)
                continue
            raise ApiError(e.code, text) from None
        except urllib.error.URLError as e:
            if attempt < retries:
                time.sleep(min(60, 2 ** (attempt + 2)))
                continue
            raise ApiError(0, str(e.reason)) from None


def multipart(fields, file_field, filename, content, ctype):
    boundary = uuid.uuid4().hex
    out = b""
    for k, v in fields.items():
        out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n"
                f"Content-Type: application/json\r\n\r\n{v}\r\n").encode()
    out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{file_field}\"; "
            f"filename=\"{filename}\"\r\nContent-Type: {ctype}\r\n\r\n").encode()
    out += content + f"\r\n--{boundary}--\r\n".encode()
    return out, f"multipart/form-data; boundary={boundary}"


def load_dotenv():
    """Fill missing ROBLOX_* vars from a git-ignored .env at the repo root (KEY=value lines)."""
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            k, sep, v = line.strip().partition("=")
            if sep and k.startswith("ROBLOX_") and not os.environ.get(k):
                os.environ[k] = v.strip().strip('"').strip("'")


def creator():
    uid, gid = os.environ.get("ROBLOX_USER_ID"), os.environ.get("ROBLOX_GROUP_ID")
    if bool(uid) == bool(gid):
        sys.exit("Set exactly one of ROBLOX_USER_ID or ROBLOX_GROUP_ID (the owner of your place).")
    return {"groupId": gid} if gid else {"userId": uid}


def upload_one(m, fmt, key, who):
    path = ROOT / m[fmt]
    meta = {
        "assetType": "Model",
        "displayName": m["name"][:50],
        "description": f"Throw Magnet for Fish showcase: {m['category']} / {m['group']}",
        "creationContext": {"creator": who},
    }
    body, ctype = multipart({"request": json.dumps(meta)}, "fileContent", path.name,
                            path.read_bytes(), CTYPE[fmt])
    op = request("POST", f"{API}/assets", key, body, {"Content-Type": ctype})
    op_id = op.get("operationId") or op.get("path", "").split("/")[-1]
    t0 = time.time()
    while not op.get("done"):
        if time.time() - t0 > POLL_TIMEOUT:
            raise ApiError(0, f"operation {op_id} still running after {POLL_TIMEOUT}s")
        time.sleep(POLL_EVERY)
        op = request("GET", f"{API}/operations/{op_id}", key)
    if "error" in op:
        raise ApiError(0, json.dumps(op["error"]))
    resp = op.get("response", {})
    asset_id = resp.get("assetId") or resp.get("path", "").split("/")[-1]
    if not str(asset_id).isdigit():
        raise ApiError(0, f"no assetId in {json.dumps(op)[:300]}")
    return int(asset_id)


def load_json(p, default):
    return json.loads(p.read_text()) if p.exists() else default


def save_json(p, data):
    p.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")


def run_upload(args, models):
    ids = load_json(IDS, {})
    todo = [m for m in models if args.force or m["name"] not in ids]
    print(f"{len(models)} selected, {len(models) - len(todo)} already uploaded, {len(todo)} to go"
          f" ({args.format}{' + glb fallback' if args.glb_fallback else ''})")
    if args.dry_run:
        for m in todo:
            print(f"  would upload {m['name']:22s} {m[args.format]}")
        return
    key = os.environ.get("ROBLOX_API_KEY") or sys.exit("ROBLOX_API_KEY is not set.")
    who = creator()
    fails = load_json(FAILS, {})
    for i, m in enumerate(todo):
        if i:
            time.sleep(args.delay)
        fmts = [args.format] + (["glb"] if args.glb_fallback and args.format == "fbx" else [])
        for fmt in fmts:
            print(f"[{i + 1}/{len(todo)}] {m['name']} ({fmt}) ...", flush=True)
            try:
                aid = upload_one(m, fmt, key, who)
            except ApiError as e:
                print(f"    FAILED: {e}")
                fails[m["name"]] = {"format": fmt, "error": str(e), "time": time.strftime("%F %T")}
                save_json(FAILS, fails)
                if e.status in (401, 403):
                    sys.exit("Authentication/permission error: check the key's Assets Read+Write "
                             "permission, its IP allowlist, and that the creator ID matches the key owner.")
                continue
            ids[m["name"]] = aid
            fails.pop(m["name"], None)
            save_json(IDS, ids)
            save_json(FAILS, fails)
            print(f"    asset {aid}")
            break
    print(f"done: {len(ids)} IDs in {IDS.relative_to(ROOT)}, {len(fails)} failures"
          f"{' (see ' + str(FAILS.relative_to(ROOT)) + ')' if fails else ''}")


# --- --inspect: read the class tree out of a downloaded binary .rbxm -------------------------

def lz4_block(src, size):
    out, i = bytearray(), 0
    while i < len(src):
        tok = src[i]; i += 1
        n = tok >> 4
        if n == 15:
            while True:
                b = src[i]; i += 1; n += b
                if b != 255:
                    break
        out += src[i:i + n]; i += n
        if i >= len(src):
            break
        off = src[i] | src[i + 1] << 8; i += 2
        n = tok & 15
        if n == 15:
            while True:
                b = src[i]; i += 1; n += b
                if b != 255:
                    break
        n += 4
        for _ in range(n):
            out.append(out[-off])
    return bytes(out[:size])


def rbxm_summary(data):
    """{className: count}, plus per-class Name/TextureID/MeshId string props (best effort)."""
    import struct
    if not data.startswith(b"<roblox!"):
        return {"error": "not a binary rbxm (XML or other)", "head": data[:80].decode("latin1")}
    pos, classes, counts, props = 32, {}, {}, {}
    while pos < len(data):
        name = data[pos:pos + 4]; clen, ulen = struct.unpack("<II", data[pos + 4:pos + 12]); pos += 16
        raw = data[pos:pos + (clen or ulen)]; pos += clen or ulen
        if clen:
            if raw[:4] == b"\x28\xb5\x2f\xfd":
                try:
                    import zstandard
                    raw = zstandard.ZstdDecompressor().decompress(raw, max_output_size=ulen)
                except ImportError:
                    return {"error": "zstd-compressed rbxm; pip install zstandard to inspect"}
            else:
                raw = lz4_block(raw, ulen)
        if name == b"INST":
            cid, = struct.unpack("<I", raw[:4]); n, = struct.unpack("<I", raw[4:8])
            cname = raw[8:8 + n].decode(); cnt, = struct.unpack("<I", raw[9 + n:13 + n])
            classes[cid] = (cname, cnt); counts[cname] = counts.get(cname, 0) + cnt
        elif name == b"PROP":
            cid, = struct.unpack("<I", raw[:4]); n, = struct.unpack("<I", raw[4:8])
            pname = raw[8:8 + n].decode(); typ = raw[8 + n]
            if typ == 1 and pname in ("Name", "TextureID", "MeshId", "ColorMap") and cid in classes:
                cname, cnt = classes[cid]; j, vals = 9 + n, []
                for _ in range(cnt):
                    ln, = struct.unpack("<I", raw[j:j + 4]); vals.append(raw[j + 4:j + 4 + ln].decode("utf-8", "replace")); j += 4 + ln
                props.setdefault(cname, {})[pname] = vals
        elif name == b"END\x00":
            break
    return {"classes": counts, "props": props}


def run_inspect(names):
    key = os.environ.get("ROBLOX_API_KEY") or sys.exit("ROBLOX_API_KEY is not set.")
    ids = load_json(IDS, {})
    for n in names:
        if n not in ids:
            print(f"{n}: no asset ID yet"); continue
        try:
            loc = request("GET", f"{DELIVERY}{ids[n]}", key)["location"]
            with urllib.request.urlopen(loc, timeout=120) as r:
                data = r.read()
        except (ApiError, urllib.error.URLError, KeyError) as e:
            print(f"{n} ({ids[n]}): could not download: {e}"); continue
        s = rbxm_summary(data)
        print(f"\n{n} ({ids[n]}):")
        if "error" in s:
            print("  ", s); continue
        print("  classes:", ", ".join(f"{k} x{v}" for k, v in sorted(s["classes"].items())))
        for cname, pr in s["props"].items():
            if cname in ("MeshPart", "SurfaceAppearance", "Model"):
                for p, v in pr.items():
                    print(f"  {cname}.{p}: {v}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="+", metavar="NAME")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--format", choices=["fbx", "glb"], default="fbx")
    ap.add_argument("--glb-fallback", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--delay", type=float, default=2.0)
    ap.add_argument("--inspect", nargs="+", metavar="NAME")
    args = ap.parse_args()
    load_dotenv()
    if args.inspect:
        return run_inspect(args.inspect)
    models = json.loads(MANIFEST.read_text())["models"]
    if args.only:
        known = {m["name"] for m in models}
        bad = [n for n in args.only if n not in known]
        if bad:
            sys.exit(f"not in manifest: {bad}")
        models = [m for m in models if m["name"] in args.only]
    run_upload(args, models)


if __name__ == "__main__":
    main()
