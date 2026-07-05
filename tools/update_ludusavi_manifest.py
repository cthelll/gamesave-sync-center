from pathlib import Path
from urllib.request import Request, urlopen
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from gss.external_db import MANIFEST_FILE, MANIFEST_URL


def main():
    request = Request(MANIFEST_URL, headers={"User-Agent": "gamesave-sync-center"})

    with urlopen(request, timeout=60) as response:
        data = response.read()

    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_FILE.write_bytes(data)

    print(f"saved: {MANIFEST_FILE}")
    print(f"size: {len(data) / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
