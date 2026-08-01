"""
OpenQFD License - Cloud verification, one-key-one-machine.
Client only checks basic format, all validation done server-side.
"""
import hashlib, os, json, time, uuid, urllib.request, urllib.error
from pathlib import Path

EDITION_FREE = "free"
EDITION_LICENSED = "licensed"      # free key via WeChat — personal/noncommercial use
EDITION_COMMERCIAL = "commercial"  # paid key — commercial use
PURCHASE_CONTACT = "021-58108606"
LICENSE_SERVER_URL = "https://env-00jy62fw2s8u.dev-hz.cloudbasefunction.cn/openqfd-license"
OFFLINE_GRACE_DAYS = 30
_SALT = "OpenQuality2026QFD"
LICENSE_PREFIX = "OQFD"
APP_VERSION = "2026.08.01"  # date-based versioning: YYYY.MM.DD

FREE_MODULES = {"project", "voc", "ctq", "hoq", "competition", "export_basic"}
COMMERCIAL_MODULES = FREE_MODULES | {
    "competition", "kano", "ahp", "pareto", "phase",
    "export_full", "version", "triz", "fmea", "doe", "dsm",
}

def get_machine_id():
    try: return str(uuid.getnode())
    except: return "unknown"

def _license_dir():
    if os.name == 'nt':
        base = Path(os.environ.get('APPDATA', Path.home()))
    else:
        base = Path.home() / '.config'
    d = base / 'OpenQFD'; d.mkdir(parents=True, exist_ok=True); return d

def _license_path():
    return _license_dir() / "license.json"

def validate_license_format(key):
    """Basic format check only. Full validation done by cloud."""
    key = key.strip().upper()
    p = key.split("-")
    if len(p) != 5:
        return False
    if p[0] != LICENSE_PREFIX:
        return False
    for x in p[1:]:
        if len(x) != 4:
            return False
    return True  # Don't check checksum - let cloud handle it

def _cloud(action, data=None, timeout=10):
    url = f"{LICENSE_SERVER_URL}?action={action}"
    if data:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'),
            headers={"Content-Type": "application/json"}, method="POST")
    else:
        req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read().decode('utf-8', errors='replace'))
        except: return {"ok": False, "error": f"HTTP {e.code}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def check_server_status():
    try: return _cloud("status").get("status") == "running"
    except: return False

def _parse_version(v):
    parts = []
    for p in str(v).strip().split("."):
        try: parts.append(int(p))
        except ValueError: parts.append(0)
    return tuple(parts)

def check_for_update():
    """Check the license server for a newer app version.

    Returns None if the check failed or no update info is configured.
    Otherwise {'available': bool, 'version': str, 'download_url': str, 'notes': str}.
    """
    try:
        r = _cloud("check_update", timeout=6)
    except Exception:
        return None
    if not r or not r.get("ok") or not r.get("version"):
        return None
    return {
        "available": _parse_version(r["version"]) > _parse_version(APP_VERSION),
        "version": r["version"],
        "download_url": r.get("download_url", ""),
        "notes": r.get("notes", ""),
    }

def activate_license(key):
    key = key.strip().upper()
    if not validate_license_format(key):
        return {"ok": False, "error": "invalid_format",
                "message": "Format: OQFD-XXXX-XXXX-XXXX-XXXX"}
    mid = get_machine_id()
    result = _cloud("activate", {"key": key, "machine_id": mid})
    if result.get("ok"):
        edition = result.get("license_type", EDITION_LICENSED)
        local = {
            "key": result["key"], "edition": edition,
            "token": result["token"], "machine_id": mid,
            "activated_at": result["activated_at"],
            "last_verified": int(time.time()),
        }
        try:
            with open(_license_path(), 'w', encoding='utf-8') as f:
                json.dump(local, f, indent=2)
        except: pass
        return {"ok": True, "edition": edition, "key": result["key"]}
    return {"ok": False, "error": result.get("error", "unknown"),
            "message": result.get("message", result.get("error", "Activation failed"))}

def deactivate_license():
    try:
        p = _license_path()
        if not p.exists(): return {"ok": True}
        with open(p, 'r', encoding='utf-8') as f:
            local = json.load(f)
        mid = get_machine_id()
        _cloud("deactivate", {"key": local.get("key",""), "machine_id": mid})
        p.unlink()
        return {"ok": True}
    except:
        try: _license_path().unlink()
        except: pass
        return {"ok": True}

def load_license():
    try:
        p = _license_path()
        if not p.exists():
            return {"edition": EDITION_FREE, "key": None}
        with open(p, 'r', encoding='utf-8') as f:
            local = json.load(f)
        if not local.get("key") or not local.get("token"):
            return {"edition": EDITION_FREE, "key": None}
        mid = get_machine_id()
        r = _cloud("verify", {
            "key": local["key"], "token": local["token"],
            "machine_id": mid
        }, timeout=5)
        if r.get("ok") and r.get("valid"):
            edition = r.get("license_type", local.get("edition", EDITION_LICENSED))
            local["edition"] = edition
            local["last_verified"] = int(time.time())
            try:
                with open(p, 'w', encoding='utf-8') as f:
                    json.dump(local, f, indent=2)
            except: pass
            return {"edition": edition, "key": local["key"], "online": True}
        if r.get("error") == "machine mismatch":
            try: p.unlink()
            except: pass
            return {"edition": EDITION_FREE, "key": None}
        last = local.get("last_verified", 0)
        days = (time.time() - last) / 86400
        if last > 0 and days < OFFLINE_GRACE_DAYS:
            edition = local.get("edition", EDITION_LICENSED)
            return {"edition": edition, "key": local["key"], "online": False,
                    "grace_days_remaining": int(OFFLINE_GRACE_DAYS - days)}
        return {"edition": EDITION_FREE, "key": None}
    except:
        return {"edition": EDITION_FREE, "key": None}

def remove_license():
    try:
        p = _license_path()
        if p.exists(): p.unlink()
    except: pass

def is_module_allowed(module, edition):
    if edition in (EDITION_LICENSED, EDITION_COMMERCIAL): return module in COMMERCIAL_MODULES
    return module in FREE_MODULES
