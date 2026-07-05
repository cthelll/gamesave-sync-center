from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_URL = "https://raw.githubusercontent.com/mtkennerly/ludusavi-manifest/master/data/manifest.yaml"
MANIFEST_FILE = ROOT / "data" / "external" / "ludusavi_manifest.yaml"

def load_ludusavi_titles(path=MANIFEST_FILE):
    path = Path(path)
    if not path.is_file():
        return []

    titles = []
    skip = {
        "aliases",
        "redirects",
        "metadata",
        "manifest",
        "registry",
        "files",
        "steam",
        "gog",
        "epic",
        "installDir",
    }

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line:
            continue

        if line.startswith((" ", "\t", "-")):
            continue

        match = re.match(r'^["\']?(.+?)["\']?:\s*$', line)
        if not match:
            continue

        title = match.group(1).strip()
        if not title:
            continue

        if title in skip:
            continue

        if title.startswith(("<", "$", "%")):
            continue

        if len(title) > 160:
            continue

        titles.append(title)

    seen = set()
    out = []

    for title in titles:
        key = re.sub(r"[^a-z0-9]+", "", title.lower())
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(title)

    return out
