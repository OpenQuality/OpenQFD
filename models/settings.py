"""App-level settings (last-opened project, etc.), persisted next to license.json."""
import json
import os
from pathlib import Path


def _settings_dir():
    if os.name == 'nt':
        base = Path(os.environ.get('APPDATA', Path.home()))
    else:
        base = Path.home() / '.config'
    d = base / 'OpenQFD'
    d.mkdir(parents=True, exist_ok=True)
    return d


def _settings_path():
    return _settings_dir() / "settings.json"


def load_settings():
    p = _settings_path()
    if p.exists():
        try:
            with open(p, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_settings(**kwargs):
    data = load_settings()
    data.update(kwargs)
    try:
        with open(_settings_path(), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
