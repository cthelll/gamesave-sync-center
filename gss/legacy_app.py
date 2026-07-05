                      
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QBrush
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QComboBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QMenu,
    QAbstractItemView,
    QDialog,
    QTabWidget,
    QFormLayout,
    QLineEdit,
    QListWidget,
    QDialogButtonBox,
    QGroupBox,
    QSizePolicy,
    QFrame,
)


APP_NAME = "Game Save Sync Center"
USER = os.environ.get("USER", "cthelll")

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "gamesave-sync-center"
DATA_DIR = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))) / "gamesave-sync-center"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
LOG_DIR = DATA_DIR / "logs"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


SAVE_EXTENSIONS = {
    ".sav", ".save", ".sav0", ".sav1", ".dat", ".bin", ".game", ".slot",
    ".json", ".xml", ".ini", ".cfg", ".player", ".checkpoint", ".sgm",
}

IGNORE_DIR_NAMES = {
    "cache", "caches", "gpucache", "shadercache", "code cache",
    "crashpad", "crashreportclient", "temp", "tmp", "logs", "log",
    "microsoft", "nvidia", "amd", "intel", "packages", "cryptneturlcache",
    "unrealengine", "epicgameslauncher", "cef", "webview2", "qtwebengine",
}

NON_GAME_FOLDERS = {
    "docker", "docker desktop", "ms-playwright-go", "playwright",
    "oem", "opencode", "pdx", "unrealengine",
    "dockerdesktop", "docker desktop installer",
    "application data", "virtualstore", "squirreltemp", "tailscale", "rustdesk",
    "telegram desktop", "toastnotificationmanagercompat", "publishers",
    "pluely", "planet9", "acer", "discord", "spotify", "mozilla", "google",
    "chromium", "steam", "valve", "ubisoft game launcher", "epicgameslauncher",
    "cef", "d3dscache", "pip", "npm-cache", "packages", "microsoft",
}

COMPANY_FOLDERS = {
    "wb games": "WB Games / publisher folder",
    "warner bros. interactive entertainment": "Warner Bros / publisher folder",
    "fromsoftware": "FromSoftware / publisher folder",
    "capcom": "Capcom / publisher folder",
    "cd projekt red": "CD Projekt RED / publisher folder",
    "bethesda softworks": "Bethesda / publisher folder",
    "bethesda": "Bethesda / publisher folder",
    "electronic arts": "Electronic Arts / publisher folder",
    "ea games": "EA Games / publisher folder",
    "ubisoft": "Ubisoft / publisher folder",
    "rockstar games": "Rockstar Games / publisher folder",
    "konami": "Konami / publisher folder",
    "sega": "SEGA / publisher folder",
    "square enix": "Square Enix / publisher folder",
    "2k games": "2K Games / publisher folder",
    "gearbox software": "Gearbox / publisher folder",
    "remedy": "Remedy / publisher folder",
    "focus entertainment": "Focus Entertainment / publisher folder",
    "devolver digital": "Devolver / publisher folder",
    "paradox interactive": "Paradox / publisher folder",
    "larian studios": "Larian Studios / publisher folder",
    "obsidian entertainment": "Obsidian / publisher folder",
    "io interactive": "IO Interactive / publisher folder",
}


def norm_name(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def profile(name: str, *aliases: str):
    return {"name": name, "aliases": [name, *aliases]}


KNOWN_PROFILES = {
    "robocop_unfinished_business": profile("RoboCop Unfinished Business", "RoboCopUnfinishedBusiness", "RoboCop Rogue City - Unfinished Business"),
    "robocop_rogue_city": profile("RoboCop Rogue City", "RoboCop", "RoboCop Rogue City"),
    "silent_hill_2": profile("Silent Hill 2", "SilentHill2", "SH2Remake"),
    "mgs_delta": profile("MGS Delta", "MGSDelta", "Metal Gear Solid Delta", "METAL GEAR SOLID DELTA"),
    "dispatch": profile("Dispatch"),
    "bloodlines_2": profile("Bloodlines 2", "Bloodlines2", "Vampire The Masquerade Bloodlines 2"),
    "megabonk": profile("Megabonk", "Ved"),
    "alice_madness_returns": profile("Alice Madness Returns"),
    "farming_simulator_2025": profile("Farming Simulator 2025", "FarmingSimulator2025"),
    "farming_simulator_22": profile("Farming Simulator 22", "FarmingSimulator2022", "FarmingSimulator22"),
    "resident_evil_7": profile("Resident Evil 7", "RESIDENT EVIL 7", "re7", "418370"),
    "resident_evil_village": profile("Resident Evil Village", "RE8", "Resident Evil 8", "Resident Evil Village"),
    "resident_evil_4": profile("Resident Evil 4 Remake", "RE4", "Resident Evil 4"),
    "resident_evil_2": profile("Resident Evil 2 Remake", "RE2", "Resident Evil 2"),
    "resident_evil_3": profile("Resident Evil 3 Remake", "RE3", "Resident Evil 3"),
    "cyberpunk_2077": profile("Cyberpunk 2077", "Cyberpunk2077"),
    "witcher_3": profile("The Witcher 3", "The Witcher 3", "Witcher 3", "TheWitcher3"),
    "elden_ring": profile("Elden Ring", "EldenRing"),
    "sekiro": profile("Sekiro", "Sekiro Shadows Die Twice"),
    "dark_souls_3": profile("Dark Souls III", "DarkSoulsIII", "Dark Souls III"),
    "armored_core_6": profile("Armored Core VI", "ArmoredCore6", "Armored Core VI Fires of Rubicon"),
    "stalker_2": profile("S.T.A.L.K.E.R. 2", "Stalker2", "STALKER2", "S.T.A.L.K.E.R. 2 Heart of Chornobyl"),
    "metro_exodus": profile("Metro Exodus", "MetroExodus"),
    "starfield": profile("Starfield"),
    "skyrim_se": profile("Skyrim Special Edition", "Skyrim Special Edition", "SkyrimSE"),
    "fallout_4": profile("Fallout 4", "Fallout4"),
    "fallout_new_vegas": profile("Fallout New Vegas", "FalloutNV", "Fallout New Vegas"),
    "doom_eternal": profile("DOOM Eternal", "DOOMEternal", "DOOM Eternal"),
    "doom_dark_ages": profile("DOOM The Dark Ages", "DOOMTheDarkAges", "DOOM The Dark Ages"),
    "doom_2016": profile("DOOM 2016", "DOOM"),
    "wolfenstein_2": profile("Wolfenstein II", "Wolfenstein II The New Colossus", "Wolfenstein2"),
    "crysis_3": profile("Crysis 3", "Crysis3"),
    "far_cry_3": profile("Far Cry 3", "FarCry3"),
    "far_cry_4": profile("Far Cry 4", "FarCry4"),
    "far_cry_5": profile("Far Cry 5", "FarCry5"),
    "far_cry_6": profile("Far Cry 6", "FarCry6"),
    "gta_v": profile("Grand Theft Auto V", "GTA V", "GTAV", "Grand Theft Auto V"),
    "rdr2": profile("Red Dead Redemption 2", "RDR2", "Red Dead Redemption 2"),
    "baldurs_gate_3": profile("Baldur's Gate 3", "Baldurs Gate 3", "Baldur's Gate 3", "Larian Studios"),
    "divinity_original_sin_2": profile("Divinity Original Sin 2", "Divinity Original Sin 2"),
    "control": profile("Control", "Remedy", "ControlRemedy"),
    "alan_wake_2": profile("Alan Wake 2", "AlanWake2"),
    "atomic_heart": profile("Atomic Heart", "AtomicHeart"),
    "trepang2": profile("Trepang2", "Trepang2"),
    "fear": profile("F.E.A.R.", "FEAR", "F.E.A.R."),
    "half_life_2": profile("Half-Life 2", "Half-Life 2", "HalfLife2"),
    "outer_worlds": profile("The Outer Worlds", "TheOuterWorlds", "The Outer Worlds"),
    "hogwarts_legacy": profile("Hogwarts Legacy", "Hogwarts Legacy", "Phoenix"),
    "indiana_jones": profile("Indiana Jones and the Great Circle", "TheGreatCircle", "Indiana Jones and the Great Circle"),
    "kingdom_come_2": profile("Kingdom Come Deliverance II", "KingdomComeDeliverance2", "Kingdom Come Deliverance II"),
    "bannerlord": profile("Mount & Blade II Bannerlord", "Mount and Blade II Bannerlord", "Bannerlord"),
    "no_mans_sky": profile("No Man's Sky", "No Mans Sky", "NoMansSky"),
    "subnautica": profile("Subnautica"),
    "terraria": profile("Terraria"),
    "stardew_valley": profile("Stardew Valley", "StardewValley"),
    "hades": profile("Hades"),
    "hades_2": profile("Hades II", "Hades II", "Hades2"),
    "hollow_knight": profile("Hollow Knight", "HollowKnight"),
    "persona_3_reload": profile("Persona 3 Reload", "P3R", "Persona3Reload"),
    "persona_5_royal": profile("Persona 5 Royal", "P5R", "Persona5Royal"),
    "nier_automata": profile("NieR Automata", "NieRAutomata", "NieR Automata"),
    "yakuza_like_dragon": profile("Like a Dragon / Yakuza", "Yakuza", "LikeADragon", "Like a Dragon"),
    "life_is_strange": profile("Life is Strange", "LifeIsStrange"),
    "tomb_raider": profile("Tomb Raider", "TombRaider"),
    "borderlands_3": profile("Borderlands 3", "Borderlands3"),
    "dragon_age_inquisition": profile("Dragon Age Inquisition", "Dragon Age Inquisition"),
    "mass_effect_le": profile("Mass Effect Legendary Edition", "Mass Effect Legendary Edition"),
    "goldberg": profile("Goldberg SteamEmu Saves", "Goldberg SteamEmu Saves"),
    "public_steam": profile("Public Steam / CODEX-RUNE-FLT", "Public Steam", "CODEX", "RUNE", "FLT", "EMPRESS Public Steam"),
}

PROFILE_ALIAS = {}
for key, p in KNOWN_PROFILES.items():
    for alias in p["aliases"]:
        PROFILE_ALIAS[norm_name(alias)] = key



SEARCH_ALIASES = {
    "винда": "windows",
    "виндовс": "windows",
    "винде": "windows",
    "винды": "windows",
    "линукс": "linux",
    "линуксе": "linux",
    "протон": "proton",
    "стим": "steam",
    "портпротон": "portproton",
    "порт": "portproton",
    "ботлс": "bottles",
    "бутылки": "bottles",
    "героик": "heroic",
    "лутрис": "lutris",

    "робокоп": "robocop",
    "мгс": "mgs",
    "метал": "mgs",
    "сайлент": "silent",
    "хилл": "hill",
    "ферма": "farming",
    "симулятор": "simulator",
    "ведьмак": "witcher",
    "киберпанк": "cyberpunk",
    "сталкер": "stalker",
    "эльден": "elden",
    "дум": "doom",
    "фаркрай": "farcry",
    "фар": "farcry",
    "гта": "gta",
    "рдр": "rdr",
    "резидент": "resident",
    "обитель": "resident",

    "новее": "newer",
    "свежее": "newer",
    "свежие": "newer",
    "последнее": "newest",
    "последние": "newest",
    "синхронизировано": "synced",
    "синк": "synced",
    "только": "only",
    "игра": "game",
    "игры": "game",
    "издатель": "publisher",
    "компания": "publisher",
    "папка": "folder",
    "неизвестное": "other",
    "мусор": "other",
}

CYR_LAT = str.maketrans({
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l",
    "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s",
    "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "c", "ч": "ch",
    "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "", "э": "e",
    "ю": "yu", "я": "ya",
})

def normalize_search_text(value: str) -> str:
    value = str(value or "").lower()
    value = value.translate(CYR_LAT)
    value = value.replace("→", " ")
    value = value.replace("_", " ")
    value = value.replace("-", " ")
    value = re.sub(r"[^a-z0-9а-яё]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value

def expand_search_query(query: str) -> list[str]:
    normalized = normalize_search_text(query)
    raw_tokens = [t for t in normalized.split() if t]

    tokens = []
    for token in raw_tokens:
        if token in SEARCH_ALIASES:
            tokens.extend(normalize_search_text(SEARCH_ALIASES[token]).split())
        else:
            tokens.append(token)

                                                                     
    joined = "".join(tokens)
    if joined and joined not in tokens:
        tokens.append(joined)

    out = []
    seen = set()
    for t in tokens:
        if len(t) <= 1:
            continue
        if t not in seen:
            seen.add(t)
            out.append(t)

    return out

def fuzzy_token_match(token: str, words: list[str], blob: str) -> bool:
    if token in blob:
        return True

    if len(token) <= 3:
        return False

    for word in words:
        if len(word) <= 2:
            continue
        if word.startswith(token) or token.startswith(word):
            return True
        if abs(len(word) - len(token)) <= 2:
            if SequenceMatcher(None, token, word).ratio() >= 0.78:
                return True

    return False

@dataclass
class FolderStats:
    files: int = 0
    size: int = 0
    latest: float = 0.0
    save_like_files: int = 0
    truncated: bool = False


@dataclass
class Candidate:
    platform: str
    launcher: str
    source: str
    path: Path
    display: str
    key: str
    stats: FolderStats
    confidence: str
    appid: str = ""


@dataclass
class GameGroup:
    key: str
    name: str
    confidence: str = "unknown"
    windows: list[Candidate] = field(default_factory=list)
    linux: list[Candidate] = field(default_factory=list)


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def safe_filename(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_.-]+", "_", s)
    return s.strip("_") or "game"


def fmt_time(ts: float) -> str:
    if not ts:
        return "-"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


def fmt_size(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    x = float(n)
    for u in units:
        if x < 1024:
            return f"{x:.1f} {u}" if u != "B" else f"{int(x)} B"
        x /= 1024
    return f"{x:.1f} PB"


def load_settings() -> dict:
    default = {
        "win_root": "/run/media/cthelll/Acer",
        "shared_root": "/run/media/cthelll/DATA/SaveSync/Universal",
        "backup_root": "/run/media/cthelll/DATA/SaveSync/_app_backups",
        "extra_linux_roots": [],
    }

    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text())
            default.update(data)
        except Exception:
            pass

    save_settings(default)
    return default


def save_settings(settings: dict):
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2, ensure_ascii=False))


def quick_stats(path: Path, max_files: int = 1500, max_seconds: float = 0.10) -> FolderStats:
    st = FolderStats()
    start = time.monotonic()

    try:
        for root, dirs, files in os.walk(path):
            dirs[:] = [
                d for d in dirs
                if d.lower() not in IGNORE_DIR_NAMES and not d.lower().endswith("cache")
            ]

            for fn in files:
                full = Path(root) / fn
                try:
                    if full.is_symlink():
                        continue
                    s = full.stat()
                except OSError:
                    continue

                st.files += 1
                st.size += s.st_size
                if s.st_mtime > st.latest:
                    st.latest = s.st_mtime
                if full.suffix.lower() in SAVE_EXTENSIONS:
                    st.save_like_files += 1

                if st.files >= max_files or (time.monotonic() - start) > max_seconds:
                    st.truncated = True
                    return st
    except OSError:
        pass

    return st


def detected_windows_roots() -> list[Path]:
    roots = []
    bases = [Path("/run/media") / USER, Path("/media") / USER, Path("/mnt")]

    for base in bases:
        if not base.exists():
            continue
        try:
            for d in base.iterdir():
                if not d.is_dir():
                    continue
                if (d / "Windows").is_dir() and (d / "Users").is_dir():
                    roots.append(d)
        except OSError:
            pass

    seen = set()
    out = []
    for r in roots:
        s = str(r)
        if s not in seen:
            seen.add(s)
            out.append(r)
    return out


def windows_users(win_root: Path) -> list[Path]:
    users_dir = win_root / "Users"
    out = []

    if not users_dir.is_dir():
        return out

    try:
        for d in users_dir.iterdir():
            if not d.is_dir():
                continue
            if d.name.lower() in {"public", "default", "default user", "all users"}:
                continue
            out.append(d)
    except OSError:
        pass

    return sorted(out, key=lambda p: p.name.lower())


def steam_compat_roots(shared_hint: str = "") -> list[Path]:
    roots = [
        Path.home() / ".local/share/Steam/steamapps/compatdata",
        Path.home() / ".steam/steam/steamapps/compatdata",
        Path.home() / ".steam/root/steamapps/compatdata",
    ]

    data_root = Path("/run/media") / USER
    if data_root.exists():
        for disk in data_root.iterdir():
            roots.append(disk / "SteamLibrary/steamapps/compatdata")
            roots.append(disk / "steamapps/compatdata")

    if shared_hint:
        p = Path(shared_hint)
        for parent in [p, *p.parents]:
            roots.append(parent / "SteamLibrary/steamapps/compatdata")
            roots.append(parent / "steamapps/compatdata")

    out = []
    seen = set()
    for r in roots:
        if r.is_dir():
            try:
                s = str(r.resolve())
            except OSError:
                s = str(r)
            if s not in seen:
                seen.add(s)
                out.append(r)
    return out


def prefix_user_dirs(prefix_root: Path, launcher: str, source: str, appid: str = "") -> list[tuple[str, str, str, Path]]:
    users = prefix_root / "drive_c/users"
    out = []

    if not users.is_dir():
        return out

    try:
        for u in users.iterdir():
            if not u.is_dir():
                continue
            if u.name.lower() in {"public", "default", "default user", "all users"}:
                continue
            out.append((launcher, source, appid, u))
    except OSError:
        pass

    return out


def find_wine_prefixes_under(base: Path, max_depth: int = 6) -> list[Path]:
    out = []
    if not base.exists():
        return out

    base_depth = len(base.parts)

    for root, dirs, _files in os.walk(base):
        p = Path(root)
        name = p.name.lower()

        if name in IGNORE_DIR_NAMES or name in {".git", "node_modules", ".venv", "venv"}:
            dirs[:] = []
            continue

        if (p / "drive_c/users").is_dir():
            out.append(p)
            dirs[:] = []
            continue

        if len(p.parts) - base_depth >= max_depth:
            dirs[:] = []

    return out


def discover_linux_user_dirs(settings: dict) -> list[tuple[str, str, str, Path]]:
    out = []

                    
    for compat_root in steam_compat_roots(settings.get("shared_root", "")):
        try:
            appids = [p for p in compat_root.iterdir() if p.is_dir()]
        except OSError:
            continue

        for app in appids:
            pfx = app / "pfx"
            if not pfx.is_dir():
                continue
            appid = app.name
            source = f"Steam Proton {appid}"
            out.extend(prefix_user_dirs(pfx, "Steam Proton", source, appid))

                
    pp_bases = [
        Path.home() / ".var/app/ru.linux_gaming.PortProton",
        Path.home() / "PortProton",
        Path.home() / ".portproton",
    ]
    for base in pp_bases:
        for pfx in find_wine_prefixes_under(base, max_depth=8):
            out.extend(prefix_user_dirs(pfx, "PortProton", "PortProton", ""))

             
    bottles_bases = [
        Path.home() / ".var/app/com.usebottles.bottles/data/bottles/bottles",
        Path.home() / ".local/share/bottles/bottles",
    ]
    for base in bottles_bases:
        if not base.exists():
            continue
        try:
            for bottle in base.iterdir():
                if bottle.is_dir():
                    out.extend(prefix_user_dirs(bottle, "Bottles", f"Bottles: {bottle.name}", ""))
        except OSError:
            pass

            
    heroic_bases = [
        Path.home() / ".config/heroic",
        Path.home() / ".var/app/com.heroicgameslauncher.hgl",
        Path.home() / "Games/Heroic",
        Path.home() / "Games/Heroic/Prefixes",
    ]
    for base in heroic_bases:
        for pfx in find_wine_prefixes_under(base, max_depth=7):
            out.extend(prefix_user_dirs(pfx, "Heroic", f"Heroic: {pfx.name}", ""))

                                            
    lutris_bases = [
        Path.home() / ".local/share/lutris",
        Path.home() / ".config/lutris",
        Path.home() / "Games",
        Path.home() / "games",
    ]
    for base in lutris_bases:
        for pfx in find_wine_prefixes_under(base, max_depth=5):
            out.extend(prefix_user_dirs(pfx, "Lutris/Other", f"Lutris/Other: {pfx.name}", ""))

                      
    for extra in settings.get("extra_linux_roots", []):
        base = Path(extra)
        if not base.exists():
            continue

        if (base / "drive_c/users").is_dir():
            out.extend(prefix_user_dirs(base, "Custom Prefix", f"Custom: {base.name}", ""))
        else:
            for pfx in find_wine_prefixes_under(base, max_depth=8):
                out.extend(prefix_user_dirs(pfx, "Custom Prefix", f"Custom: {pfx.name}", ""))

    seen = set()
    unique = []
    for launcher, source, appid, user_dir in out:
        s = str(user_dir)
        if s not in seen:
            seen.add(s)
            unique.append((launcher, source, appid, user_dir))

    return unique


def infer_folder(path: Path, folder_name: str, stats: FolderStats) -> tuple[str, str, str]:
    low = folder_name.lower()
    n = norm_name(folder_name)

    if low in NON_GAME_FOLDERS:
        return n, folder_name, "noise"

    if n in PROFILE_ALIAS:
        key = PROFILE_ALIAS[n]
        return key, KNOWN_PROFILES[key]["name"], "exact"

    if low in COMPANY_FOLDERS:
        return n, COMPANY_FOLDERS[low], "company"

    if (path / "Saved/SaveGames").is_dir() or (path / "Saved/SaveData").is_dir() or (path / "SaveGames").is_dir():
        return n, folder_name, "probable"

    if stats.save_like_files >= 2 and stats.files <= 2500:
        return n, folder_name, "probable"

    if "save" in low and stats.files > 0:
        return n, folder_name, "probable"

    return n, folder_name, "unknown"


def make_candidate(platform: str, launcher: str, source: str, path: Path, display: str, appid: str = "") -> Candidate | None:
    if not path.is_dir():
        return None

    stats = quick_stats(path)
    key, nice_name, confidence = infer_folder(path, display, stats)

    if confidence == "noise":
        return None

    return Candidate(
        platform=platform,
        launcher=launcher,
        source=source,
        path=path,
        display=nice_name,
        key=key,
        stats=stats,
        confidence=confidence,
        appid=appid,
    )


def scan_direct_children(platform: str, launcher: str, source: str, base: Path, appid: str = "") -> list[Candidate]:
    out = []
    if not base.is_dir():
        return out

    try:
        for child in base.iterdir():
            if not child.is_dir():
                continue
            c = make_candidate(platform, launcher, source, child, child.name, appid)
            if c:
                out.append(c)
    except OSError:
        pass

    return out


def scan_windows(win_root: Path, win_user: Path) -> list[Candidate]:
    out = []

    locations = [
        win_user / "AppData/Local",
        win_user / "AppData/Roaming",
        win_user / "AppData/LocalLow",
        win_user / "Documents/My Games",
        win_user / "Saved Games",
    ]

    for loc in locations:
        out.extend(scan_direct_children("windows", "Windows", "Windows", loc))

    public_steam = win_root / "Users/Public/Documents/Steam"
    if public_steam.is_dir():
        c = make_candidate("windows", "Windows", "Windows Public Documents", public_steam, "Public Steam")
        if c:
            out.append(c)

    goldberg = win_user / "AppData/Roaming/Goldberg SteamEmu Saves"
    if goldberg.is_dir():
        c = make_candidate("windows", "Windows", "Windows Goldberg", goldberg, "Goldberg SteamEmu Saves")
        if c:
            out.append(c)

    return out


def scan_linux(settings: dict) -> list[Candidate]:
    out = []

    for launcher, source, appid, user_dir in discover_linux_user_dirs(settings):
        locations = [
            user_dir / "AppData/Local",
            user_dir / "AppData/Roaming",
            user_dir / "AppData/LocalLow",
            user_dir / "Documents/My Games",
            user_dir / "Saved Games",
        ]

        for loc in locations:
            out.extend(scan_direct_children("linux", launcher, source, loc, appid))

        public = user_dir.parent / "Public"
        public_steam = public / "Documents/Steam"
        if public_steam.is_dir():
            c = make_candidate("linux", launcher, source, public_steam, "Public Steam", appid)
            if c:
                out.append(c)

        goldberg = user_dir / "AppData/Roaming/Goldberg SteamEmu Saves"
        if goldberg.is_dir():
            c = make_candidate("linux", launcher, source, goldberg, "Goldberg SteamEmu Saves", appid)
            if c:
                out.append(c)

    return out


def confidence_rank(conf: str) -> int:
    return {
        "exact": 4,
        "probable": 3,
        "company": 2,
        "unknown": 1,
    }.get(conf, 0)


def group_candidates(candidates: list[Candidate]) -> list[GameGroup]:
    groups: dict[str, GameGroup] = {}

    for c in candidates:
        if c.key not in groups:
            groups[c.key] = GameGroup(key=c.key, name=c.display, confidence=c.confidence)

        g = groups[c.key]
        if confidence_rank(c.confidence) > confidence_rank(g.confidence):
            g.confidence = c.confidence
            g.name = c.display

        if c.platform == "windows":
            g.windows.append(c)
        else:
            g.linux.append(c)

    for g in groups.values():
        g.windows.sort(key=lambda x: (confidence_rank(x.confidence), x.stats.latest), reverse=True)
        g.linux.sort(key=lambda x: (confidence_rank(x.confidence), x.stats.latest), reverse=True)

    return sorted(groups.values(), key=lambda g: (
        -confidence_rank(g.confidence),
        not (g.windows and g.linux),
        g.name.lower()
    ))


def backup_folder(src: Path, backup_root: Path, game_name: str, label: str) -> Path | None:
    if not src.is_dir():
        return None

    dst = backup_root / now_stamp() / safe_filename(game_name) / safe_filename(label)
    dst.parent.mkdir(parents=True, exist_ok=True)

    def ignore(_dir, names):
        return [n for n in names if n.lower() in IGNORE_DIR_NAMES]

    shutil.copytree(src, dst, ignore=ignore, dirs_exist_ok=True)
    return dst


def copy_save_folder(src: Path, dst: Path, overwrite: bool = True) -> tuple[int, int]:
    copied_files = 0
    copied_bytes = 0

    for root, dirs, files in os.walk(src):
        dirs[:] = [
            d for d in dirs
            if d.lower() not in IGNORE_DIR_NAMES and not d.lower().endswith("cache")
        ]

        root_path = Path(root)
        rel = root_path.relative_to(src)
        dst_dir = dst / rel
        dst_dir.mkdir(parents=True, exist_ok=True)

        for fn in files:
            sp = root_path / fn
            dp = dst_dir / fn

            try:
                if sp.is_symlink():
                    continue

                if dp.exists() and not overwrite:
                    ss = sp.stat()
                    ds = dp.stat()
                    if int(ss.st_mtime) <= int(ds.st_mtime) and ss.st_size == ds.st_size:
                        continue

                shutil.copy2(sp, dp)
                copied_files += 1
                copied_bytes += sp.stat().st_size
            except OSError:
                continue

    return copied_files, copied_bytes


def open_folder(path: Path):
    if not path.is_dir():
        return
    subprocess.Popen(["xdg-open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.all_candidates: list[Candidate] = []
        self.groups: list[GameGroup] = []
        self.updating_source_combo = False

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1180, 720)
        screen = QApplication.primaryScreen()
        if screen:
            area = screen.availableGeometry()
            width = min(1680, max(1280, int(area.width() * 0.92)))
            height = min(980, max(760, int(area.height() * 0.88)))
            self.resize(width, height)
            self.move(
                area.x() + (area.width() - width) // 2,
                area.y() + (area.height() - height) // 2
            )
        else:
            self.resize(1440, 860)
        self.resize(1320, 780)


        self.win_root_combo = QComboBox()
        self.win_root_combo.setMinimumWidth(210)

        self.win_user_combo = QComboBox()
        self.win_user_combo.setMinimumWidth(190)

        self.linux_source_combo = QComboBox()
        self.linux_source_combo.setMinimumWidth(230)
        self.linux_source_combo.addItem("All prefixes")

        self.view_combo = QComboBox()
        self.view_combo.addItems(["Recommended", "Games only", "All folders"])
        self.view_combo.setMinimumWidth(150)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Recommended",
            "Name",
            "Type",
            "Status",
            "Newest save",
            "Windows latest",
            "Linux latest",
            "Launcher",
            "Both folders",
        ])
        self.sort_combo.setMinimumWidth(160)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search games, prefixes, appids, paths…")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumWidth(520)
        self.search_input.setMaximumWidth(760)
        self.search_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels([
            "Game",
            "Type",
            "Status",
            "Windows latest",
            "Linux latest",
            "Windows path",
            "Linux path",
            "Linux source",
            "Launcher",
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.update_details)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_game_context_menu)
        self.table.cellDoubleClicked.connect(lambda _row, _col: self.show_selected_details_popup())
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)

        self.details = QTextEdit()
        self.details.setReadOnly(True)

        self.btn_rescan = QPushButton("Rescan")
        self.btn_rescan.setObjectName("secondaryAction")
        self.btn_rescan.clicked.connect(self.rescan)

        self.btn_choose_disk = QPushButton("Change…")
        self.btn_choose_disk.setObjectName("secondaryAction")
        self.btn_choose_disk.clicked.connect(self.choose_windows_disk)

        self.btn_add_prefix = QPushButton("Add Source…")
        self.btn_add_prefix.setObjectName("secondaryAction")
        self.btn_add_prefix.clicked.connect(self.add_linux_root)

        self.btn_win_to_lin = QPushButton("Windows → Linux")
        self.btn_win_to_lin.setObjectName("primaryAction")
        self.btn_win_to_lin.clicked.connect(lambda: self.sync_selected("windows_to_linux"))

        self.btn_lin_to_win = QPushButton("Linux → Windows")
        self.btn_lin_to_win.setObjectName("primaryAction")
        self.btn_lin_to_win.clicked.connect(lambda: self.sync_selected("linux_to_windows"))

        self.btn_newest_both = QPushButton("Sync Newest")
        self.btn_newest_both.setObjectName("primaryAction")
        self.btn_newest_both.setToolTip("Copy the newest save to the older side for the selected games.")
        self.btn_newest_both.clicked.connect(self.sync_newest_selected)

        self.btn_backup = QPushButton("Backup")
        self.btn_backup.setObjectName("secondaryAction")
        self.btn_backup.clicked.connect(self.backup_selected)

        self.btn_open_win = QPushButton("Open Windows")
        self.btn_open_win.setObjectName("secondaryAction")
        self.btn_open_win.clicked.connect(lambda: self.open_selected("windows"))

        self.btn_open_lin = QPushButton("Open Linux")
        self.btn_open_lin.setObjectName("secondaryAction")
        self.btn_open_lin.clicked.connect(lambda: self.open_selected("linux"))

        self.btn_settings = QPushButton("Settings…")
        self.btn_settings.setObjectName("secondaryAction")
        self.btn_settings.clicked.connect(self.show_settings)

        top = QToolBar()
        top.setMovable(False)
        top.addWidget(QLabel("Windows: "))
        top.addWidget(self.win_root_combo)
        top.addWidget(self.btn_choose_disk)
        top.addSeparator()
        top.addWidget(QLabel("User: "))
        top.addWidget(self.win_user_combo)
        top.addSeparator()
        top.addWidget(QLabel("Linux: "))
        top.addWidget(self.linux_source_combo)
        top.addWidget(self.btn_add_prefix)
        top.addSeparator()
        filters = QToolBar("Filters")
        filters.setMovable(False)
        filters.setFloatable(False)
        self.addToolBarBreak(Qt.TopToolBarArea)
        self.addToolBar(filters)

        filters.addWidget(QLabel("Search: "))
        filters.addWidget(self.search_input)

        filter_spacer = QWidget()
        filter_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        filters.addWidget(filter_spacer)

        filters.addWidget(QLabel("View: "))
        filters.addWidget(self.view_combo)
        filters.addWidget(QLabel("Sort: "))
        filters.addWidget(self.sort_combo)
        filters.addSeparator()
        filters.addWidget(self.btn_rescan)
        self.addToolBar(top)

        filters = QToolBar("Filters")
        filters.setMovable(False)
        filters.setFloatable(False)
        self.addToolBarBreak(Qt.TopToolBarArea)
        self.addToolBar(filters)

        action_bar = QHBoxLayout()
        action_bar.setContentsMargins(8, 6, 8, 6)
        action_bar.setSpacing(8)
        sync_label = QLabel("Sync")
        sync_label.setStyleSheet("font-weight: 700; color: #cfc7b7; padding-right: 2px;")
        action_bar.addWidget(sync_label)
        action_bar.addWidget(self.btn_win_to_lin)
        action_bar.addWidget(self.btn_lin_to_win)
        action_bar.addWidget(self.btn_newest_both)
        action_bar.addSpacing(12)

        tools_label = QLabel("Tools")
        tools_label.setStyleSheet("font-weight: 700; color: #cfc7b7; padding-left: 4px; padding-right: 2px;")
        action_bar.addWidget(tools_label)
        action_bar.addWidget(self.btn_backup)
        action_bar.addWidget(self.btn_open_win)
        action_bar.addWidget(self.btn_open_lin)
        action_bar.addStretch()
        action_bar.addWidget(self.btn_settings)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.table)
        splitter.addWidget(self.details)
        splitter.setSizes([540, 240])

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.addLayout(action_bar)
        layout.addWidget(splitter)
        self.setCentralWidget(root)

        self.populate_windows_roots()

        self.win_root_combo.currentTextChanged.connect(self.on_win_root_changed)
        self.win_user_combo.currentTextChanged.connect(lambda _x: self.save_current_settings())
        self.linux_source_combo.currentTextChanged.connect(lambda _x: self.apply_filters())
        self.view_combo.currentTextChanged.connect(lambda _x: self.apply_filters())
        self.sort_combo.currentTextChanged.connect(lambda _x: self.apply_filters())
        self.search_input.textChanged.connect(lambda _x: self.apply_filters())

        self.rescan()

    def populate_windows_roots(self):
        self.win_root_combo.blockSignals(True)
        self.win_root_combo.clear()

        roots = detected_windows_roots()
        saved = Path(self.settings.get("win_root", ""))

        if saved and str(saved) not in [str(r) for r in roots]:
            roots.insert(0, saved)

        for r in roots:
            self.win_root_combo.addItem(str(r))

        idx = self.win_root_combo.findText(str(saved))
        if idx >= 0:
            self.win_root_combo.setCurrentIndex(idx)

        self.win_root_combo.blockSignals(False)
        self.populate_windows_users()

    def populate_windows_users(self):
        self.win_user_combo.blockSignals(True)
        self.win_user_combo.clear()

        root = Path(self.win_root_combo.currentText())
        users = windows_users(root)

        for u in users:
            self.win_user_combo.addItem(str(u))

        self.win_user_combo.blockSignals(False)

    def on_win_root_changed(self):
        self.populate_windows_users()
        self.save_current_settings()

    def save_current_settings(self):
        if self.win_root_combo.currentText():
            self.settings["win_root"] = self.win_root_combo.currentText()
        save_settings(self.settings)

    def choose_windows_disk(self):
        d = QFileDialog.getExistingDirectory(self, "Choose Windows disk", "/run/media")
        if not d:
            return

        if self.win_root_combo.findText(d) < 0:
            self.win_root_combo.addItem(d)
        self.win_root_combo.setCurrentText(d)
        self.save_current_settings()
        self.populate_windows_users()

    def add_linux_root(self):
        d = QFileDialog.getExistingDirectory(
            self,
            "Choose Linux prefix or root containing Wine/Proton prefixes",
            str(Path.home())
        )
        if not d:
            return

        roots = self.settings.setdefault("extra_linux_roots", [])
        if d not in roots:
            roots.append(d)
            save_settings(self.settings)

        QMessageBox.information(
            self,
            APP_NAME,
            f"Added Linux root/prefix:\n\n{d}\n\nNow rescanning."
        )
        self.rescan()

    def rescan(self):
        self.save_current_settings()

        win_root = Path(self.win_root_combo.currentText())
        win_user = Path(self.win_user_combo.currentText())

        candidates: list[Candidate] = []

        if win_root.is_dir() and win_user.is_dir():
            candidates.extend(scan_windows(win_root, win_user))

        candidates.extend(scan_linux(self.settings))

        self.all_candidates = candidates
        self.update_linux_source_combo()
        self.apply_filters()

    def update_linux_source_combo(self):
        current = self.linux_source_combo.currentText() or "All prefixes"
        sources = sorted({c.source for c in self.all_candidates if c.platform == "linux"})
        launchers = sorted({c.launcher for c in self.all_candidates if c.platform == "linux"})

        items = ["All prefixes"]
        items.extend([f"Launcher: {l}" for l in launchers])
        items.extend([f"Prefix: {s}" for s in sources])

        self.updating_source_combo = True
        self.linux_source_combo.blockSignals(True)
        self.linux_source_combo.clear()
        self.linux_source_combo.addItems(items)

        idx = self.linux_source_combo.findText(current)
        if idx >= 0:
            self.linux_source_combo.setCurrentIndex(idx)

        self.linux_source_combo.blockSignals(False)
        self.updating_source_combo = False

    def filtered_candidates(self) -> list[Candidate]:
        src_filter = self.linux_source_combo.currentText()
        view = self.view_combo.currentText()

        out = []

        for c in self.all_candidates:
            if c.platform == "linux":
                if src_filter.startswith("Launcher: "):
                    launcher = src_filter.replace("Launcher: ", "", 1)
                    if c.launcher != launcher:
                        continue
                elif src_filter.startswith("Prefix: "):
                    source = src_filter.replace("Prefix: ", "", 1)
                    if c.source != source:
                        continue

            if view == "Games only" and c.confidence not in {"exact", "probable"}:
                continue

            if view == "Recommended" and c.confidence not in {"exact", "probable", "company"}:
                continue

            out.append(c)

        return out

    def search_blob_for_group(self, g: GameGroup) -> str:
        parts = [
            g.name,
            g.key,
            g.confidence,
            self.match_label(g.confidence),
            self.status_for(g),
        ]

        for c in g.windows + g.linux:
            parts.extend([
                c.display,
                c.key,
                c.confidence,
                c.launcher,
                c.source,
                c.appid,
                str(c.path),
                c.path.name,
                " ".join(c.path.parts[-8:]),
            ])

        return normalize_search_text(" ".join(str(x) for x in parts if x))

    def search_score_for_group(self, g: GameGroup, query: str) -> int:
        tokens = expand_search_query(query)
        if not tokens:
            return 0

        blob = self.search_blob_for_group(g)
        words = blob.split()

        score = 0
        for token in tokens:
            if token in blob:
                score += 20
                if normalize_search_text(g.name).startswith(token):
                    score += 20
                continue

            if fuzzy_token_match(token, words, blob):
                score += 8
                continue

            return -1

        if g.confidence == "exact":
            score += 12
        elif g.confidence == "probable":
            score += 7
        elif g.confidence == "company":
            score += 3

        if g.windows and g.linux:
            score += 6

        return score

    def sort_groups(self, groups: list[GameGroup], scores: dict[str, int]) -> list[GameGroup]:
        mode = self.sort_combo.currentText() if hasattr(self, "sort_combo") else "Recommended"

        def win_latest(g):
            return g.windows[0].stats.latest if g.windows else 0

        def lin_latest(g):
            return g.linux[0].stats.latest if g.linux else 0

        def newest(g):
            return max(win_latest(g), lin_latest(g))

        def launcher(g):
            return g.linux[0].launcher if g.linux else ""

        if mode == "Recommended":
            return sorted(
                groups,
                key=lambda g: (
                    -scores.get(g.key, 0),
                    -confidence_rank(g.confidence),
                    not (g.windows and g.linux),
                    -newest(g),
                    g.name.lower(),
                )
            )

        if mode == "Name":
            return sorted(groups, key=lambda g: g.name.lower())

        if mode == "Type":
            return sorted(groups, key=lambda g: (-confidence_rank(g.confidence), g.name.lower()))

        if mode == "Status":
            return sorted(groups, key=lambda g: (self.status_for(g), g.name.lower()))

        if mode == "Newest save":
            return sorted(groups, key=lambda g: (-newest(g), g.name.lower()))

        if mode == "Windows latest":
            return sorted(groups, key=lambda g: (-win_latest(g), g.name.lower()))

        if mode == "Linux latest":
            return sorted(groups, key=lambda g: (-lin_latest(g), g.name.lower()))

        if mode == "Launcher":
            return sorted(groups, key=lambda g: (launcher(g).lower(), g.name.lower()))

        if mode == "Both folders":
            return sorted(groups, key=lambda g: (not (g.windows and g.linux), g.name.lower()))

        return groups

    def apply_filters(self):
        groups = group_candidates(self.filtered_candidates())

        query = self.search_input.text() if hasattr(self, "search_input") else ""
        scores = {}

        if query.strip():
            filtered = []
            for g in groups:
                score = self.search_score_for_group(g, query)
                if score >= 0:
                    scores[g.key] = score
                    filtered.append(g)
            groups = filtered
        else:
            scores = {g.key: 0 for g in groups}

        self.groups = self.sort_groups(groups, scores)
        self.populate_table()

    def populate_table(self):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        for g in self.groups:
            row = self.table.rowCount()
            self.table.insertRow(row)

            win = g.windows[0] if g.windows else None
            lin = g.linux[0] if g.linux else None
            status = self.status_for(g)

            values = [
                g.name,
                self.match_label(g.confidence),
                status,
                fmt_time(win.stats.latest) if win else "-",
                fmt_time(lin.stats.latest) if lin else "-",
                str(win.path) if win else "-",
                str(lin.path) if lin else "-",
                lin.source if lin else "-",
                lin.launcher if lin else "-",
            ]

            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                if col == 0:
                    item.setData(Qt.UserRole, g.key)

                self.decorate_item(item, g, col)
                self.table.setItem(row, col, item)

        self.table.setSortingEnabled(True)
        self.update_details()

    def decorate_item(self, item: QTableWidgetItem, g: GameGroup, col: int):
        if g.confidence == "exact":
            if col in {0, 1}:
                f = QFont()
                f.setBold(True)
                item.setFont(f)
            item.setForeground(QBrush(QColor("#ece8df")))
        elif g.confidence == "probable":
            item.setForeground(QBrush(QColor("#d7d3ca")))
        elif g.confidence == "company":
            item.setForeground(QBrush(QColor("#d4bf8a")))
        else:
            item.setForeground(QBrush(QColor("#9d9a93")))

        if col == 1:
            if g.confidence == "exact":
                item.setBackground(QBrush(QColor("#313631")))
            elif g.confidence == "probable":
                item.setBackground(QBrush(QColor("#303236")))
            elif g.confidence == "company":
                item.setBackground(QBrush(QColor("#3a3327")))

    def match_label(self, conf: str) -> str:
        return {
            "exact": "Game",
            "probable": "Detected",
            "company": "Publisher",
            "unknown": "Other",
        }.get(conf, conf)

    def status_for(self, g: GameGroup) -> str:
        if g.windows and g.linux:
            wt = g.windows[0].stats.latest
            lt = g.linux[0].stats.latest

            if not wt or not lt:
                return "Both found"

            if abs(wt - lt) <= 2:
                return "Looks synced"
            if wt > lt:
                return "Windows newer"
            return "Linux newer"

        if g.windows:
            return "Only Windows"
        if g.linux:
            return "Only Linux"
        return "Empty"

    def selected_group(self) -> GameGroup | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if not item:
            return None
        key = item.data(Qt.UserRole)

        for g in self.groups:
            if g.key == key:
                return g
        return None

    def choose_candidate(self, candidates: list[Candidate], title: str) -> Candidate | None:
        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0]

        items = []
        mapping = {}

        for c in candidates:
            label = f"{self.match_label(c.confidence)} | {c.source} | {fmt_time(c.stats.latest)} | {c.path}"
            items.append(label)
            mapping[label] = c

        selected, ok = QInputDialog.getItem(self, title, "Choose folder:", items, 0, False)
        if not ok or not selected:
            return None

        return mapping[selected]

    def selected_groups(self) -> list[GameGroup]:
        rows = sorted({idx.row() for idx in self.table.selectionModel().selectedRows()})
        if not rows and self.table.currentRow() >= 0:
            rows = [self.table.currentRow()]

        out = []
        seen = set()

        for row in rows:
            item = self.table.item(row, 0)
            if not item:
                continue

            key = item.data(Qt.UserRole)
            if key in seen:
                continue

            for g in self.groups:
                if g.key == key:
                    out.append(g)
                    seen.add(key)
                    break

        return out

    def main_candidate(self, candidates: list[Candidate]) -> Candidate | None:
        if not candidates:
            return None
        return candidates[0]

    def build_direct_pairs(self, groups: list[GameGroup], mode: str):
        pairs = []
        skipped = []

        for g in groups:
            win = self.main_candidate(g.windows)
            lin = self.main_candidate(g.linux)

            if mode == "windows_to_linux":
                if not win or not lin:
                    skipped.append((g.name, "missing Windows or Linux folder"))
                    continue
                pairs.append((g, win, lin, "Windows → Linux", "linux-before-sync"))

            elif mode == "linux_to_windows":
                if not win or not lin:
                    skipped.append((g.name, "missing Windows or Linux folder"))
                    continue
                pairs.append((g, lin, win, "Linux → Windows", "windows-before-sync"))

        return pairs, skipped

    def build_newest_pairs(self, groups: list[GameGroup]):
        pairs = []
        skipped = []

        for g in groups:
            win = self.main_candidate(g.windows)
            lin = self.main_candidate(g.linux)

            if g.confidence not in {"exact", "probable"}:
                skipped.append((g.name, f"not a game-level entry: {self.match_label(g.confidence)}"))
                continue

            if not win or not lin:
                skipped.append((g.name, "missing Windows or Linux folder"))
                continue

            wt = win.stats.latest
            lt = lin.stats.latest

            if not wt and not lt:
                skipped.append((g.name, "no modified files found"))
                continue

            if abs(wt - lt) <= 2:
                skipped.append((g.name, "already looks synced"))
                continue

            if wt > lt:
                pairs.append((g, win, lin, "Newest: Windows → Linux", "linux-before-newest-sync"))
            else:
                pairs.append((g, lin, win, "Newest: Linux → Windows", "windows-before-newest-sync"))

        return pairs, skipped

    def run_sync_pairs(self, pairs, skipped, title: str):
        if not pairs:
            msg = "Nothing to sync."
            if skipped:
                msg += "\n\nSkipped:\n" + "\n".join([f"- {name}: {reason}" for name, reason in skipped[:20]])
            QMessageBox.information(self, APP_NAME, msg)
            return

        preview = []
        for g, src, dst, human, _backup_label in pairs[:14]:
            preview.append(
                f"- {g.name}\n"
                f"  {human}\n"
                f"  FROM: {src.path}\n"
                f"  TO:   {dst.path}"
            )

        if len(pairs) > 14:
            preview.append(f"... and {len(pairs) - 14} more")

        if skipped:
            preview.append("")
            preview.append("Skipped:")
            for name, reason in skipped[:10]:
                preview.append(f"- {name}: {reason}")
            if len(skipped) > 10:
                preview.append(f"... and {len(skipped) - 10} more skipped")

        msg = (
            f"{title}\n\n"
            f"Ready: {len(pairs)}\n"
            f"Skipped: {len(skipped)}\n\n"
            + "\n".join(preview)
            + "\n\nDestination folders will be backed up before copying. Existing matching files will be overwritten from the chosen source. Extra files are not deleted.\n\nContinue?"
        )

        if QMessageBox.question(self, APP_NAME, msg) != QMessageBox.Yes:
            return

        backup_root = Path(self.settings.get("backup_root", str(DATA_DIR / "backups")))
        backup_root.mkdir(parents=True, exist_ok=True)

        results = []
        total_files = 0
        total_bytes = 0

        for g, src, dst, human, backup_label in pairs:
            try:
                backup_path = backup_folder(dst.path, backup_root, g.name, backup_label)
                copied_files, copied_bytes = copy_save_folder(src.path, dst.path, overwrite=True)
                total_files += copied_files
                total_bytes += copied_bytes
                results.append(f"OK | {g.name} | {human} | files={copied_files} | backup={backup_path}")
            except Exception as e:
                results.append(f"ERROR | {g.name} | {human} | {e}")

        log_file = LOG_DIR / f"batch_sync_{now_stamp()}.log"
        log_file.write_text(
            f"{APP_NAME}\n"
            f"time: {datetime.now().isoformat()}\n"
            f"operation: {title}\n"
            f"pairs: {len(pairs)}\n"
            f"skipped: {len(skipped)}\n"
            f"copied_files: {total_files}\n"
            f"copied_bytes: {total_bytes}\n\n"
            + "\n".join(results)
            + "\n\nSkipped:\n"
            + "\n".join([f"{name}: {reason}" for name, reason in skipped])
        )

        QMessageBox.information(
            self,
            APP_NAME,
            f"Done.\n\n"
            f"Synced games: {len(pairs)}\n"
            f"Skipped: {len(skipped)}\n"
            f"Copied files: {total_files}\n"
            f"Copied size: {fmt_size(total_bytes)}\n\n"
            f"Log:\n{log_file}"
        )

        self.rescan()

    def update_details(self):
        groups = self.selected_groups()

        if len(groups) > 1:
            lines = [f"{len(groups)} games selected", "=" * 22, ""]
            ready_both = sum(1 for g in groups if g.windows and g.linux)
            lines.append(f"Ready for Windows/Linux sync: {ready_both}")
            lines.append("")
            for g in groups[:40]:
                lines.append(f"- {g.name}: {self.status_for(g)}")
            if len(groups) > 40:
                lines.append(f"... and {len(groups) - 40} more")
            self.details.setPlainText("\n".join(lines))
            return

        g = self.selected_group()

        if not g:
            self.details.setPlainText("No game selected.")
            return

        lines = []
        lines.append(g.name)
        lines.append("=" * len(g.name))
        lines.append("")
        lines.append(f"Type:   {self.match_label(g.confidence)}")
        lines.append(f"Status: {self.status_for(g)}")
        lines.append("")

        lines.append("Windows candidates:")
        if g.windows:
            for c in g.windows:
                lines.append(f"- {self.match_label(c.confidence)} | {c.source}")
                lines.append(f"  path:   {c.path}")
                lines.append(f"  latest: {fmt_time(c.stats.latest)}")
                lines.append(f"  files:  {c.stats.files}{'+' if c.stats.truncated else ''}")
                lines.append(f"  saves:  {c.stats.save_like_files}{'+' if c.stats.truncated else ''}")
                lines.append(f"  size:   {fmt_size(c.stats.size)}{'+' if c.stats.truncated else ''}")
        else:
            lines.append("- not found")

        lines.append("")
        lines.append("Linux candidates:")
        if g.linux:
            for c in g.linux:
                lines.append(f"- {self.match_label(c.confidence)} | {c.source}")
                lines.append(f"  launcher: {c.launcher}")
                lines.append(f"  appid:    {c.appid or '-'}")
                lines.append(f"  path:     {c.path}")
                lines.append(f"  latest:   {fmt_time(c.stats.latest)}")
                lines.append(f"  files:    {c.stats.files}{'+' if c.stats.truncated else ''}")
                lines.append(f"  saves:    {c.stats.save_like_files}{'+' if c.stats.truncated else ''}")
                lines.append(f"  size:     {fmt_size(c.stats.size)}{'+' if c.stats.truncated else ''}")
        else:
            lines.append("- not found")

        self.details.setPlainText("\n".join(lines))

    def show_game_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if item is None:
            return

        if not self.table.item(item.row(), 0).isSelected():
            self.table.selectRow(item.row())
        g = self.selected_group()
        if not g:
            return

        menu = QMenu(self)

        selected_count = len(self.selected_groups())
        suffix = f" ({selected_count} selected)" if selected_count > 1 else ""

        act_win_to_lin = menu.addAction("Windows → Linux" + suffix)
        act_lin_to_win = menu.addAction("Linux → Windows" + suffix)
        act_newest = menu.addAction("Newest → Both" + suffix)
        menu.addSeparator()
        act_backup = menu.addAction("Backup" + suffix)
        menu.addSeparator()
        act_open_win = menu.addAction("Open Windows folder")
        act_open_lin = menu.addAction("Open Linux folder")
        menu.addSeparator()
        act_details = menu.addAction("Details")

        if not g.windows:
            act_win_to_lin.setEnabled(False)
            act_open_win.setEnabled(False)

        if not g.linux:
            act_lin_to_win.setEnabled(False)
            act_open_lin.setEnabled(False)

        chosen = menu.exec(self.table.viewport().mapToGlobal(pos))

        if chosen == act_win_to_lin:
            self.sync_selected("windows_to_linux")
        elif chosen == act_lin_to_win:
            self.sync_selected("linux_to_windows")
        elif chosen == act_newest:
            self.sync_newest_selected()
        elif chosen == act_backup:
            self.backup_selected()
        elif chosen == act_open_win:
            self.open_selected("windows")
        elif chosen == act_open_lin:
            self.open_selected("linux")
        elif chosen == act_details:
            self.show_selected_details_popup()

    def show_selected_details_popup(self):
        g = self.selected_group()
        if not g:
            return

        QMessageBox.information(
            self,
            APP_NAME,
            self.details.toPlainText()
        )

    def sync_selected(self, mode: str):
        groups = self.selected_groups()

        if len(groups) > 1:
            pairs, skipped = self.build_direct_pairs(groups, mode)
            title = "Windows → Linux" if mode == "windows_to_linux" else "Linux → Windows"
            self.run_sync_pairs(pairs, skipped, title)
            return

        g = self.selected_group()
        if not g:
            return

        if mode == "windows_to_linux":
            src = self.choose_candidate(g.windows, "Choose Windows source")
            dst = self.choose_candidate(g.linux, "Choose Linux destination")
            human = "Windows → Linux"
            backup_label = "linux-before-sync"
        else:
            src = self.choose_candidate(g.linux, "Choose Linux source")
            dst = self.choose_candidate(g.windows, "Choose Windows destination")
            human = "Linux → Windows"
            backup_label = "windows-before-sync"

        if not src or not dst:
            QMessageBox.warning(self, APP_NAME, "Source or destination not found.")
            return

        msg = (
            f"{human}\n\n"
            f"Game:\n{g.name}\n\n"
            f"FROM:\n{src.path}\n\n"
            f"TO:\n{dst.path}\n\n"
            f"Destination будет сохранён в backup перед копированием.\n\n"
            f"Продолжить?"
        )

        if QMessageBox.question(self, APP_NAME, msg) != QMessageBox.Yes:
            return

        backup_root = Path(self.settings.get("backup_root", str(DATA_DIR / "backups")))
        backup_root.mkdir(parents=True, exist_ok=True)

        try:
            backup_path = backup_folder(dst.path, backup_root, g.name, backup_label)
            copied_files, copied_bytes = copy_save_folder(src.path, dst.path, overwrite=True)
        except Exception as e:
            QMessageBox.critical(self, APP_NAME, f"Sync failed:\n\n{e}")
            return

        log_file = LOG_DIR / f"sync_{safe_filename(g.name)}_{now_stamp()}.log"
        log_file.write_text(
            f"{APP_NAME}\n"
            f"time: {datetime.now().isoformat()}\n"
            f"operation: {human}\n"
            f"game: {g.name}\n"
            f"source: {src.path}\n"
            f"destination: {dst.path}\n"
            f"backup: {backup_path}\n"
            f"copied_files: {copied_files}\n"
            f"copied_bytes: {copied_bytes}\n"
        )

        QMessageBox.information(
            self,
            APP_NAME,
            f"Готово.\n\n"
            f"Copied files: {copied_files}\n"
            f"Copied size: {fmt_size(copied_bytes)}\n\n"
            f"Backup:\n{backup_path}\n\n"
            f"Log:\n{log_file}"
        )

        self.rescan()

    def sync_newest_selected(self):
        groups = self.selected_groups()
        if not groups:
            return

        pairs, skipped = self.build_newest_pairs(groups)
        self.run_sync_pairs(pairs, skipped, "Newest → Both")

    def backup_selected(self):
        groups = self.selected_groups()
        if not groups:
            return

        backup_root = Path(self.settings.get("backup_root", str(DATA_DIR / "backups")))
        backup_root.mkdir(parents=True, exist_ok=True)

        made = []

        for g in groups:
            for c in g.windows:
                p = backup_folder(c.path, backup_root, g.name, "windows-manual-backup")
                if p:
                    made.append(str(p))

            for c in g.linux:
                p = backup_folder(c.path, backup_root, g.name, "linux-manual-backup")
                if p:
                    made.append(str(p))

        QMessageBox.information(self, APP_NAME, "Backups created:\n\n" + "\n".join(made[:60]))

    def open_selected(self, side: str):
        g = self.selected_group()
        if not g:
            return

        if side == "windows":
            c = self.choose_candidate(g.windows, "Choose Windows folder")
        else:
            c = self.choose_candidate(g.linux, "Choose Linux folder")

        if not c:
            QMessageBox.warning(self, APP_NAME, "Folder not found.")
            return

        open_folder(c.path)

    def restore_from_log_dialog(self):
        log_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose sync log",
            str(LOG_DIR),
            "Log files (*.log);;All files (*)"
        )

        if not log_path:
            return

        self.undo_from_log(Path(log_path))

    def restore_backup_to_folder_dialog(self):
        backup_root = Path(self.settings.get("backup_root", str(DATA_DIR / "backups")))

        backup = QFileDialog.getExistingDirectory(
            self,
            "Choose backup folder to restore FROM",
            str(backup_root)
        )
        if not backup:
            return

        destination = QFileDialog.getExistingDirectory(
            self,
            "Choose destination folder to restore INTO",
            str(Path.home())
        )
        if not destination:
            return

        backup_p = Path(backup)
        destination_p = Path(destination)

        msg = (
            f"Restore backup with delete-extra mode?\n\n"
            f"FROM backup:\n{backup_p}\n\n"
            f"TO destination:\n{destination_p}\n\n"
            f"The current destination contents will be saved first, then destination will be replaced by backup.\n\n"
            f"Continue?"
        )

        if QMessageBox.question(self, APP_NAME, msg) != QMessageBox.Yes:
            return

        try:
            emergency = self.mirror_restore_folder(backup_p, destination_p)
        except Exception as e:
            QMessageBox.critical(self, APP_NAME, f"Restore failed:\n\n{e}")
            return

        QMessageBox.information(
            self,
            APP_NAME,
            f"Restore complete.\n\nCurrent destination was saved to:\n{emergency}"
        )

        self.rescan()

    def delete_backup_dialog(self):
        backup_root = Path(self.settings.get("backup_root", str(DATA_DIR / "backups")))

        target = QFileDialog.getExistingDirectory(
            self,
            "Choose backup folder to DELETE",
            str(backup_root)
        )
        if not target:
            return

        target_p = Path(target)

        if backup_root not in target_p.parents and target_p != backup_root:
            QMessageBox.warning(
                self,
                APP_NAME,
                f"Refusing to delete folder outside backup root:\n\n{target_p}"
            )
            return

        msg = (
            f"Delete backup folder?\n\n"
            f"{target_p}\n\n"
            f"This cannot be undone."
        )

        if QMessageBox.question(self, APP_NAME, msg) != QMessageBox.Yes:
            return

        try:
            shutil.rmtree(target_p)
        except Exception as e:
            QMessageBox.critical(self, APP_NAME, f"Delete failed:\n\n{e}")
            return

        QMessageBox.information(self, APP_NAME, "Backup folder deleted.")

    def show_paths_info(self):
        extra = "\n".join(self.settings.get("extra_linux_roots", [])) or "-"

        QMessageBox.information(
            self,
            APP_NAME,
            f"Settings file:\n{SETTINGS_FILE}\n\n"
            f"Data dir:\n{DATA_DIR}\n\n"
            f"Logs:\n{LOG_DIR}\n\n"
            f"Backup root:\n{self.settings.get('backup_root')}\n\n"
            f"Extra Linux roots:\n{extra}"
        )

    def choose_dir_into_line(self, line_edit: QLineEdit, title: str):
        start = line_edit.text().strip() or str(Path.home())
        d = QFileDialog.getExistingDirectory(self, title, start)
        if d:
            line_edit.setText(d)

    def open_settings_file(self):
        subprocess.Popen(["xdg-open", str(SETTINGS_FILE)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def mirror_restore_folder(self, backup: Path, destination: Path):
        """
        Restore backup into destination in mirror mode:
        destination contents are removed, then backup contents are copied in.
        This intentionally does NOT backup the current garbage first, because that can be huge.
        """
        backup = Path(backup)
        destination = Path(destination)

        if not backup.is_dir():
            raise RuntimeError(f"Backup folder does not exist:\n{backup}")

        destination.mkdir(parents=True, exist_ok=True)

        for child in destination.iterdir():
            if child.is_symlink() or child.is_file():
                child.unlink()
            elif child.is_dir():
                shutil.rmtree(child)

        for item in backup.iterdir():
            target = destination / item.name
            if item.is_symlink():
                continue
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            else:
                shutil.copy2(item, target)

    def parse_restore_entries_from_log(self, log_file: Path):
        entries = []

        log_file = Path(log_file)
        if not log_file.is_file():
            return entries

        for line in log_file.read_text(errors="replace").splitlines():
            if not line.startswith("OK | "):
                continue

            dest_match = re.search(r" \| destination=(.*?) \| backup=", line)
            backup_match = re.search(r" \| backup=(.*)$", line)

            if not dest_match or not backup_match:
                continue

            destination = Path(dest_match.group(1).strip())
            backup = Path(backup_match.group(1).strip())

            if backup.is_dir():
                entries.append((backup, destination))

        return entries

    def latest_sync_log(self):
        candidates = []
        if LOG_DIR.is_dir():
            candidates = sorted(
                LOG_DIR.glob("*.log"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
        return candidates[0] if candidates else None

    def undo_last_sync(self):
        log_path = self.settings.get("last_sync_log") or ""
        log_file = Path(log_path) if log_path else None

        if not log_file or not log_file.is_file():
            log_file = self.latest_sync_log()

        if not log_file:
            QMessageBox.warning(self, APP_NAME, "No sync log found.")
            return

        self.undo_from_log(log_file)

    def undo_from_log(self, log_file: Path):
        log_file = Path(log_file)
        entries = self.parse_restore_entries_from_log(log_file)

        if not entries:
            QMessageBox.warning(
                self,
                APP_NAME,
                "This log cannot be restored automatically.\n\n"
                "It probably was created by an older app version and does not contain destination paths.\n\n"
                f"Log:\n{log_file}"
            )
            return

        preview = []
        for backup, destination in entries[:10]:
            preview.append(
                f"FROM backup:\n{backup}\n\n"
                f"TO destination:\n{destination}"
            )

        if len(entries) > 10:
            preview.append(f"... and {len(entries) - 10} more")

        msg = (
            f"Undo sync from log:\n{log_file}\n\n"
            f"Restore entries: {len(entries)}\n\n"
            "This will DELETE current destination contents and restore them from backup.\n"
            "Extra files created by the bad sync will be removed.\n\n"
            + "\n\n---\n\n".join(preview)
            + "\n\nContinue?"
        )

        if QMessageBox.question(self, APP_NAME, msg) != QMessageBox.Yes:
            return

        restored = []
        errors = []

        for backup, destination in entries:
            try:
                self.mirror_restore_folder(backup, destination)
                restored.append(str(destination))
            except Exception as e:
                errors.append(f"{destination}: {e}")

        text = f"Undo complete.\n\nRestored: {len(restored)}"
        if errors:
            text += "\n\nErrors:\n" + "\n".join(errors[:12])

        QMessageBox.information(self, APP_NAME, text)
        self.rescan()

    def restore_from_log_dialog(self):
        log_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose sync log",
            str(LOG_DIR),
            "Log files (*.log);;All files (*)"
        )

        if not log_path:
            return

        self.undo_from_log(Path(log_path))

    def restore_backup_to_folder_dialog(self):
        backup_root = Path(self.settings.get("backup_root", str(DATA_DIR / "backups")))

        backup = QFileDialog.getExistingDirectory(
            self,
            "Choose backup folder to restore FROM",
            str(backup_root)
        )
        if not backup:
            return

        destination = QFileDialog.getExistingDirectory(
            self,
            "Choose destination folder to restore INTO",
            str(Path.home())
        )
        if not destination:
            return

        backup_p = Path(backup)
        destination_p = Path(destination)

        msg = (
            "Restore backup?\n\n"
            f"FROM backup:\n{backup_p}\n\n"
            f"TO destination:\n{destination_p}\n\n"
            "Destination contents will be deleted and replaced by backup contents.\n\n"
            "Continue?"
        )

        if QMessageBox.question(self, APP_NAME, msg) != QMessageBox.Yes:
            return

        try:
            self.mirror_restore_folder(backup_p, destination_p)
        except Exception as e:
            QMessageBox.critical(self, APP_NAME, f"Restore failed:\n\n{e}")
            return

        QMessageBox.information(self, APP_NAME, "Restore complete.")
        self.rescan()

    def delete_backup_dialog(self):
        backup_root = Path(self.settings.get("backup_root", str(DATA_DIR / "backups")))

        target = QFileDialog.getExistingDirectory(
            self,
            "Choose backup folder to DELETE",
            str(backup_root)
        )
        if not target:
            return

        target_p = Path(target)

        try:
            target_p.relative_to(backup_root)
        except ValueError:
            QMessageBox.warning(
                self,
                APP_NAME,
                f"Refusing to delete folder outside backup root:\n\n{target_p}"
            )
            return

        msg = (
            "Delete backup folder?\n\n"
            f"{target_p}\n\n"
            "This cannot be undone."
        )

        if QMessageBox.question(self, APP_NAME, msg) != QMessageBox.Yes:
            return

        try:
            shutil.rmtree(target_p)
        except Exception as e:
            QMessageBox.critical(self, APP_NAME, f"Delete failed:\n\n{e}")
            return

        QMessageBox.information(self, APP_NAME, "Backup folder deleted.")

    def show_paths_info(self):
        extra = "\n".join(self.settings.get("extra_linux_roots", [])) or "-"

        QMessageBox.information(
            self,
            APP_NAME,
            f"Settings file:\n{SETTINGS_FILE}\n\n"
            f"Data dir:\n{DATA_DIR}\n\n"
            f"Logs:\n{LOG_DIR}\n\n"
            f"Backup root:\n{self.settings.get('backup_root')}\n\n"
            f"Extra Linux roots:\n{extra}"
        )

    def show_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(APP_NAME + " Settings")
        dialog.resize(820, 560)

        tabs = QTabWidget(dialog)

                                 
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)

        paths_group = QGroupBox("Paths")
        paths_form = QFormLayout(paths_group)

        win_root_edit = QLineEdit(self.settings.get("win_root", ""))
        shared_root_edit = QLineEdit(self.settings.get("shared_root", ""))
        backup_root_edit = QLineEdit(self.settings.get("backup_root", ""))

        def path_row(line_edit, title):
            row = QWidget()
            row_l = QHBoxLayout(row)
            row_l.setContentsMargins(0, 0, 0, 0)
            btn = QPushButton("Browse")
            btn.setObjectName("secondaryAction")
            btn.clicked.connect(lambda: self.choose_dir_into_line(line_edit, title))
            row_l.addWidget(line_edit)
            row_l.addWidget(btn)
            return row

        paths_form.addRow("Windows disk:", path_row(win_root_edit, "Choose Windows disk"))
        paths_form.addRow("Shared storage:", path_row(shared_root_edit, "Choose shared save storage"))
        paths_form.addRow("Backup root:", path_row(backup_root_edit, "Choose backup root"))

        general_layout.addWidget(paths_group)

        save_general_btn = QPushButton("Save settings and rescan")
        save_general_btn.setObjectName("primaryAction")

        def save_general():
            self.settings["win_root"] = win_root_edit.text().strip()
            self.settings["shared_root"] = shared_root_edit.text().strip()
            self.settings["backup_root"] = backup_root_edit.text().strip()
            save_settings(self.settings)
            self.populate_windows_roots()
            self.rescan()
            QMessageBox.information(self, APP_NAME, "Settings saved.")

        save_general_btn.clicked.connect(save_general)
        general_layout.addWidget(save_general_btn)
        general_layout.addStretch()

                                  
        prefixes_tab = QWidget()
        prefixes_layout = QVBoxLayout(prefixes_tab)

        prefixes_group = QGroupBox("Extra Linux prefix roots")
        prefixes_group_layout = QVBoxLayout(prefixes_group)

        extra_list = QListWidget()
        for root in self.settings.get("extra_linux_roots", []):
            extra_list.addItem(root)

        prefix_buttons = QHBoxLayout()

        add_prefix_btn = QPushButton("Add root")
        add_prefix_btn.setObjectName("secondaryAction")
        remove_prefix_btn = QPushButton("Remove selected")
        remove_prefix_btn.setObjectName("secondaryAction")
        open_prefix_btn = QPushButton("Open selected")
        open_prefix_btn.setObjectName("secondaryAction")
        save_prefix_btn = QPushButton("Save prefixes and rescan")
        save_prefix_btn.setObjectName("primaryAction")

        def add_prefix():
            d = QFileDialog.getExistingDirectory(
                dialog,
                "Choose Linux prefix or folder containing prefixes",
                str(Path.home())
            )
            if not d:
                return
            existing = [extra_list.item(i).text() for i in range(extra_list.count())]
            if d not in existing:
                extra_list.addItem(d)

        def remove_prefix():
            for item in extra_list.selectedItems():
                extra_list.takeItem(extra_list.row(item))

        def open_prefix():
            items = extra_list.selectedItems()
            if items:
                open_folder(Path(items[0].text()))

        def save_prefixes():
            self.settings["extra_linux_roots"] = [
                extra_list.item(i).text() for i in range(extra_list.count())
            ]
            save_settings(self.settings)
            self.rescan()
            QMessageBox.information(self, APP_NAME, "Prefixes saved.")

        add_prefix_btn.clicked.connect(add_prefix)
        remove_prefix_btn.clicked.connect(remove_prefix)
        open_prefix_btn.clicked.connect(open_prefix)
        save_prefix_btn.clicked.connect(save_prefixes)

        prefix_buttons.addWidget(add_prefix_btn)
        prefix_buttons.addWidget(remove_prefix_btn)
        prefix_buttons.addWidget(open_prefix_btn)
        prefix_buttons.addStretch()
        prefix_buttons.addWidget(save_prefix_btn)

        prefixes_group_layout.addWidget(QLabel("Add Steam/Proton/Wine prefix roots here when auto-detect does not find them."))
        prefixes_group_layout.addWidget(extra_list)
        prefixes_group_layout.addLayout(prefix_buttons)

        prefixes_layout.addWidget(prefixes_group)

        detected_group = QGroupBox("Detected sources")
        detected_layout = QVBoxLayout(detected_group)
        detected_text = QTextEdit()
        detected_text.setReadOnly(True)

        sources = sorted({c.source for c in self.all_candidates if c.platform == "linux"})
        launchers = sorted({c.launcher for c in self.all_candidates if c.platform == "linux"})
        detected_text.setPlainText(
            "Launchers:\n"
            + ("\n".join(f"- {x}" for x in launchers) if launchers else "- none")
            + "\n\nPrefixes:\n"
            + ("\n".join(f"- {x}" for x in sources) if sources else "- none")
        )
        detected_layout.addWidget(detected_text)
        prefixes_layout.addWidget(detected_group)

                                 
        backups_tab = QWidget()
        backups_layout = QVBoxLayout(backups_tab)

        backup_info = QLabel(
            "Backup and rollback actions are kept here. Restore actions use delete-extra mode, "
            "so destination is returned to backup state."
        )
        backup_info.setWordWrap(True)
        backups_layout.addWidget(backup_info)

        backup_actions = QGroupBox("Backup actions")
        backup_actions_layout = QVBoxLayout(backup_actions)

        def settings_button(text, callback, primary=False, destructive=False):
            b = QPushButton(text)
            b.setObjectName("primaryAction" if primary else "secondaryAction")
            if destructive:
                b.setStyleSheet("border-color: #7b4e45; background-color: #3a2926; color: #f0ddd7;")
            b.clicked.connect(callback)
            return b

        backup_actions_layout.addWidget(settings_button("Open Backups", lambda: (Path(self.settings.get("backup_root", str(DATA_DIR / "backups"))).mkdir(parents=True, exist_ok=True), open_folder(Path(self.settings.get("backup_root", str(DATA_DIR / "backups")))))))
        backup_actions_layout.addWidget(settings_button("Undo Last Sync", self.undo_last_sync, primary=True))
        backup_actions_layout.addWidget(settings_button("Restore from Log…", self.restore_from_log_dialog))
        backup_actions_layout.addWidget(settings_button("Restore Backup to Folder…", self.restore_backup_to_folder_dialog))
        backup_actions_layout.addWidget(settings_button("Delete Backup…", self.delete_backup_dialog, destructive=True))

        backups_layout.addWidget(backup_actions)
        backups_layout.addStretch()

                                            
        maintenance_tab = QWidget()
        maintenance_layout = QVBoxLayout(maintenance_tab)

        logs_group = QGroupBox("Logs and configuration")
        logs_layout = QVBoxLayout(logs_group)

        logs_layout.addWidget(settings_button("Open Logs", lambda: (LOG_DIR.mkdir(parents=True, exist_ok=True), open_folder(LOG_DIR))))
        logs_layout.addWidget(settings_button("Open App Data", lambda: open_folder(DATA_DIR)))
        logs_layout.addWidget(settings_button("Open Config", lambda: open_folder(CONFIG_DIR)))
        logs_layout.addWidget(settings_button("Open Settings File", self.open_settings_file))
        logs_layout.addWidget(settings_button("Show Paths", self.show_paths_info))

        maintenance_layout.addWidget(logs_group)
        maintenance_layout.addStretch()

        tabs.addTab(general_tab, "General")
        tabs.addTab(prefixes_tab, "Sources")
        tabs.addTab(backups_tab, "Backups")
        tabs.addTab(maintenance_tab, "Advanced")

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)

        layout = QVBoxLayout(dialog)
        layout.addWidget(tabs)
        layout.addWidget(buttons)

        dialog.exec()



def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    w = MainWindow()
    w.show()

    sys.exit(app.exec())



                                                                 

from difflib import SequenceMatcher as _GSS_SequenceMatcher

_GSS_SEARCH_ALIASES = {
    "винда": "windows", "виндовс": "windows", "винды": "windows", "винде": "windows",
    "линукс": "linux", "линуксе": "linux",
    "стим": "steam", "steam": "steam",
    "протон": "proton", "proton": "proton",
    "портпротон": "portproton", "portproton": "portproton",
    "бутылки": "bottles", "ботлс": "bottles", "bottles": "bottles",
    "героик": "heroic", "heroic": "heroic",
    "лутрис": "lutris", "lutris": "lutris",

    "робокоп": "robocop",
    "мгс": "mgs",
    "метал": "mgs",
    "сайлент": "silent hill",
    "хилл": "hill",
    "сталкер": "stalker",
    "ведьмак": "witcher",
    "киберпанк": "cyberpunk",
    "резидент": "resident evil",
    "обитель": "resident evil",
    "дум": "doom",
    "фаркрай": "farcry",
    "гта": "gta",
    "рдр": "rdr",
    "элден": "elden",
    "эльден": "elden",

    "новее": "newer",
    "свежее": "newer",
    "свежий": "newer",
    "последний": "newest",
    "последнее": "newest",
    "синк": "synced",
    "синхронизировано": "synced",
    "только": "only",
    "игра": "game",
    "игры": "game",
    "издатель": "publisher",
    "компания": "publisher",
    "папка": "folder",
    "другое": "other",
    "мусор": "other",
}

_GSS_CYR = str.maketrans({
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
})

def _gss_norm(value):
    value = str(value or "").lower().translate(_GSS_CYR)
    value = value.replace("→", " ")
    value = re.sub(r"[^a-z0-9а-яё]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value

def _gss_tokens(query):
    raw = _gss_norm(query).split()
    out = []
    for token in raw:
        if token in _GSS_SEARCH_ALIASES:
            out.extend(_gss_norm(_GSS_SEARCH_ALIASES[token]).split())
        else:
            out.append(token)

    joined = "".join(out)
    if len(joined) > 2:
        out.append(joined)

    result = []
    seen = set()
    for token in out:
        if len(token) < 2:
            continue
        if token not in seen:
            seen.add(token)
            result.append(token)
    return result

def _gss_fuzzy_match(token, words, compact_blob):
    if token in compact_blob:
        return True

    if len(token) <= 3:
        return False

    for word in words:
        if len(word) < 3:
            continue

        if word.startswith(token) or token.startswith(word):
            return True

        if abs(len(word) - len(token)) <= 2:
            if _GSS_SequenceMatcher(None, token, word).ratio() >= 0.78:
                return True

    return False

def _gss_candidate_latest(c):
    return c.stats.latest if c else 0

def _gss_win(g):
    return g.windows[0] if g.windows else None

def _gss_lin(g):
    return g.linux[0] if g.linux else None

def _gss_win_latest(g):
    c = _gss_win(g)
    return _gss_candidate_latest(c)

def _gss_lin_latest(g):
    c = _gss_lin(g)
    return _gss_candidate_latest(c)

def _gss_newest(g):
    return max(_gss_win_latest(g), _gss_lin_latest(g))

def _gss_status_rank(status):
    order = {
        "Windows newer": 0,
        "Linux newer": 1,
        "Only Windows": 2,
        "Only Linux": 3,
        "Both found": 4,
        "Looks synced": 5,
        "Empty": 6,
    }
    return order.get(status, 99)

def _gss_search_blob_for_group(self, g):
    parts = [
        g.name,
        g.key,
        g.confidence,
        self.match_label(g.confidence),
        self.status_for(g),
    ]

    for c in g.windows + g.linux:
        parts.extend([
            c.platform,
            c.launcher,
            c.source,
            c.appid,
            c.display,
            c.key,
            c.confidence,
            str(c.path),
            c.path.name,
            " ".join(c.path.parts[-10:]),
        ])

    blob = _gss_norm(" ".join(str(x) for x in parts if x))
    compact = blob.replace(" ", "")
    return blob, compact, blob.split()

def _gss_search_score_for_group(self, g, query):
    tokens = _gss_tokens(query)
    if not tokens:
        return 0

    blob, compact, words = _gss_search_blob_for_group(self, g)

    score = 0
    name_norm = _gss_norm(g.name)
    name_compact = name_norm.replace(" ", "")

    for token in tokens:
        matched = False

        if token in blob or token in compact:
            matched = True
            score += 30

            if name_norm.startswith(token) or token in name_compact:
                score += 25

        elif _gss_fuzzy_match(token, words, compact):
            matched = True
            score += 12

        if not matched:
            return -1

    if g.confidence == "exact":
        score += 20
    elif g.confidence == "probable":
        score += 12
    elif g.confidence == "company":
        score += 5

    if g.windows and g.linux:
        score += 10

    score += min(int(_gss_newest(g) // 100000000), 20)
    return score

def _gss_sort_groups(self, groups, scores):
    mode = self.sort_combo.currentText() if hasattr(self, "sort_combo") else "Recommended"
    reverse_toggle = bool(getattr(self, "_gss_reverse_sort", False))

    def conf(g):
        return confidence_rank(g.confidence)

    def launcher(g):
        lin = _gss_lin(g)
        return lin.launcher if lin else ""

    def source(g):
        lin = _gss_lin(g)
        return lin.source if lin else ""

    if mode == "Recommended":
        result = sorted(
            groups,
            key=lambda g: (
                -scores.get(g.key, 0),
                -conf(g),
                not (g.windows and g.linux),
                -_gss_newest(g),
                g.name.lower(),
            )
        )
    elif mode == "Name":
        result = sorted(groups, key=lambda g: g.name.lower())
    elif mode == "Type":
        result = sorted(groups, key=lambda g: (-conf(g), g.name.lower()))
    elif mode == "Status":
        result = sorted(groups, key=lambda g: (_gss_status_rank(self.status_for(g)), g.name.lower()))
    elif mode == "Newest save":
        result = sorted(groups, key=lambda g: (-_gss_newest(g), g.name.lower()))
    elif mode == "Windows latest":
        result = sorted(groups, key=lambda g: (-_gss_win_latest(g), g.name.lower()))
    elif mode == "Linux latest":
        result = sorted(groups, key=lambda g: (-_gss_lin_latest(g), g.name.lower()))
    elif mode == "Launcher":
        result = sorted(groups, key=lambda g: (launcher(g).lower(), source(g).lower(), g.name.lower()))
    elif mode == "Both folders":
        result = sorted(groups, key=lambda g: (not (g.windows and g.linux), -conf(g), g.name.lower()))
    else:
        result = sorted(groups, key=lambda g: g.name.lower())

    if reverse_toggle:
        result = list(reversed(result))

    return result

def _gss_apply_filters(self):
    candidates = self.filtered_candidates()
    groups = group_candidates(candidates)

    query = self.search_input.text() if hasattr(self, "search_input") else ""
    scores = {}

    if query.strip():
        filtered = []
        for g in groups:
            score = _gss_search_score_for_group(self, g, query)
            if score >= 0:
                scores[g.key] = score
                filtered.append(g)
        groups = filtered
    else:
        scores = {g.key: 0 for g in groups}

    self.groups = _gss_sort_groups(self, groups, scores)
    self.populate_table()

def _gss_populate_table(self):
    self.table.setSortingEnabled(False)
    self.table.setUpdatesEnabled(False)
    self.table.setRowCount(0)

    for g in self.groups:
        row = self.table.rowCount()
        self.table.insertRow(row)

        win = g.windows[0] if g.windows else None
        lin = g.linux[0] if g.linux else None

        values = [
            g.name,
            self.match_label(g.confidence),
            self.status_for(g),
            fmt_time(win.stats.latest) if win else "-",
            fmt_time(lin.stats.latest) if lin else "-",
            str(win.path) if win else "-",
            str(lin.path) if lin else "-",
            lin.source if lin else "-",
            lin.launcher if lin else "-",
        ]

        for col, val in enumerate(values):
            item = QTableWidgetItem(val)
            if col == 0:
                item.setData(Qt.UserRole, g.key)
            self.decorate_item(item, g, col)
            self.table.setItem(row, col, item)

    self.table.setUpdatesEnabled(True)
    self.table.resizeColumnsToContents()
    self.update_details()

def _gss_header_clicked(self, section):
    column_to_mode = {
        0: "Name",
        1: "Type",
        2: "Status",
        3: "Windows latest",
        4: "Linux latest",
        7: "Launcher",
        8: "Launcher",
    }

    mode = column_to_mode.get(section)
    if not mode:
        return

    current = self.sort_combo.currentText() if hasattr(self, "sort_combo") else ""

    if current == mode:
        self._gss_reverse_sort = not bool(getattr(self, "_gss_reverse_sort", False))
        self.apply_filters()
    else:
        self._gss_reverse_sort = False
        self.sort_combo.setCurrentText(mode)
        self.apply_filters()

def _gss_sort_combo_changed(self, _text):
    self._gss_reverse_sort = False
    self.apply_filters()

def _gss_install_search_sort(self):
    self._gss_reverse_sort = False

    if hasattr(self, "sort_combo"):
        self.sort_combo.blockSignals(True)
        self.sort_combo.clear()
        self.sort_combo.addItems([
            "Recommended",
            "Name",
            "Type",
            "Status",
            "Newest save",
            "Windows latest",
            "Linux latest",
            "Launcher",
            "Both folders",
        ])
        self.sort_combo.setMinimumWidth(160)
        self.sort_combo.setCurrentText("Recommended")
        self.sort_combo.blockSignals(False)
        self.sort_combo.currentTextChanged.connect(lambda text: _gss_sort_combo_changed(self, text))

    if hasattr(self, "search_input"):
        self.search_input.setPlaceholderText("Search games, launchers, prefixes, appids, paths…")
        self.search_input.textChanged.connect(lambda _text: self.apply_filters())

    self.table.setSortingEnabled(False)
    self.table.setShowGrid(False)
    self.table.verticalHeader().setVisible(False)

    header = self.table.horizontalHeader()
    header.setSectionsClickable(True)
    header.sectionClicked.connect(lambda section: _gss_header_clicked(self, section))

    self.apply_filters()

                                                                        
_GSS_OLD_INIT = MainWindow.__init__

def _gss_new_init(self, *args, **kwargs):
    _GSS_OLD_INIT(self, *args, **kwargs)
    _gss_install_search_sort(self)

MainWindow.__init__ = _gss_new_init
MainWindow.apply_filters = _gss_apply_filters
MainWindow.populate_table = _gss_populate_table
MainWindow.search_blob_for_group = _gss_search_blob_for_group
MainWindow.search_score_for_group = _gss_search_score_for_group
MainWindow.sort_groups = _gss_sort_groups

                                                               








                                                         

from gss.ui.gnome import install_gnome_ui as _gss_install_gnome_ui

_GSS_OLD_GNOME_UI_INIT = MainWindow.__init__

def _gss_gnome_ui_init(self, *args, **kwargs):
    _GSS_OLD_GNOME_UI_INIT(self, *args, **kwargs)
    _gss_install_gnome_ui(self)

MainWindow.__init__ = _gss_gnome_ui_init

                                                       


                                                               

from gss.game_knowledge import (
    install_game_knowledge as _gss_install_game_knowledge,
    install_group_filter as _gss_install_group_filter,
)

_GSS_GAME_KNOWLEDGE_STATS = _gss_install_game_knowledge(globals())
_gss_install_group_filter(globals())

                                                             

if __name__ == "__main__":
    main()
