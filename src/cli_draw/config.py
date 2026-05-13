import json
from pathlib import Path

DEFAULT_CONFIG = {
    "colors": [
        {"id": 0, "name": "white", "hex": "#FFFFFF"},
        {"id": 1, "name": "red", "hex": "#FF0000"},
        {"id": 2, "name": "green", "hex": "#00FF00"},
        {"id": 3, "name": "yellow", "hex": "#FFFF00"},
        {"id": 4, "name": "blue", "hex": "#0000FF"},
        {"id": 5, "name": "magenta", "hex": "#FF00FF"},
        {"id": 6, "name": "cyan", "hex": "#00FFFF"},
        {"id": 7, "name": "black", "hex": "#000000"},
    ],
    "brushes": ["#", "*", ".", " ", "o", "x", "@", "+"]
}

CONFIG_DIR = Path.home() / ".cli-draw"
CONFIG_FILE = CONFIG_DIR / "config.json"


def hex_to_ansi(hex_color: str) -> str:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"\033[38;2;{r};{g};{b}m"


def hex_to_curses_color(hex_color: str) -> int:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    if r > 127:
        r = 1
    if g > 127:
        g = 1
    if b > 127:
        b = 1
    return r * 4 + g * 2 + b


def load_config() -> dict:
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
            if "colors" not in config:
                config = DEFAULT_CONFIG.copy()
                save_config(config)
            return config
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_colors(config: dict) -> list[tuple[str, str, int]]:
    colors = []
    for c in config.get("colors", DEFAULT_CONFIG["colors"]):
        name = c.get("name", "white")
        hex_code = c.get("hex", "#FFFFFF")
        colors.append((name, hex_to_ansi(hex_code), hex_to_curses_color(hex_code)))
    return colors


def get_color_names(config: dict) -> list[str]:
    return [c.get("name", "white") for c in config.get("colors", DEFAULT_CONFIG["colors"])]


def get_brushes(config: dict) -> list[str]:
    return config.get("brushes", DEFAULT_CONFIG["brushes"])


def get_brushes(config: dict) -> list[str]:
    return config.get("brushes", DEFAULT_CONFIG.get("brushes", ["#", "*", ".", " "]))
