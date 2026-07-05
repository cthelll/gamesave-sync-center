# Game Save Sync Center

Game Save Sync Center is a Linux desktop app for finding, comparing, backing up, and syncing game save folders between Windows and Linux gaming environments.

It is built for dual-boot users and people who run Windows games through Steam Proton, PortProton, Bottles, Heroic, Lutris, or custom Wine prefixes.

The main goal is simple:

> Show where the saves are on both systems before copying anything.

## Features

- Scans mounted Windows user folders.
- Scans Linux gaming prefixes.
- Supports Steam Proton, PortProton, Bottles, Heroic, Lutris, and custom Wine roots.
- Groups matching Windows and Linux save folders into game entries.
- Shows whether Windows or Linux has the newer save.
- Supports manual sync:
  - Windows to Linux
  - Linux to Windows
  - Sync newest side
- Creates backups before sync operations.
- Supports rollback from logs and backup folders.
- Has search, sorting, and filtering for large save libraries.
- Uses a GNOME-style dark interface.
- Can use the Ludusavi manifest as an external game title database.
- Filters common non-game folders such as Docker, Playwright, UnrealEngine, OEM, Proton runtime folders, and scene/release-group buckets.

## Why this exists

Game saves are often scattered across many different locations:

    Documents
    Saved Games
    AppData/Local
    AppData/Roaming
    Steam userdata
    Proton compatdata
    Wine prefixes
    launcher-specific folders
    publisher folders
    random per-game folders

On Linux, Windows games usually store saves inside Proton or Wine prefixes that imitate a Windows user profile. This makes manual syncing annoying and risky.

Game Save Sync Center gives you one place to inspect both sides before copying anything.

## Installation

### 1. Clone the repository

    git clone https://github.com/YOUR_USERNAME/gamesave-sync-center.git
    cd gamesave-sync-center

### 2. Create a virtual environment

    python3 -m venv .venv
    source .venv/bin/activate

### 3. Install dependencies

    pip install -r requirements.txt

### 4. Run the app

    python app.py

## Optional external game database

The app can use the Ludusavi manifest as an external game title database.

Update it with:

    python tools/update_ludusavi_manifest.py

This downloads:

    data/external/ludusavi_manifest.yaml

The manifest is ignored by git because it is generated external data.

## Basic usage

1. Mount your Windows drive in Linux.
2. Start the app.
3. Open `Sources`.
4. Choose the Windows disk.
5. Choose the Windows user.
6. Choose the Linux source, or leave it on all prefixes.
7. Press `Rescan`.
8. Search for a game.
9. Select the matching row.
10. Check the Windows and Linux paths in the details panel.
11. Use one of the sync actions:
    - `Windows → Linux`
    - `Linux → Windows`
    - `Sync Newest`

## Backups and rollback

The app creates backups before sync operations.

Backups are used for:

- undoing the last sync
- restoring from a sync log
- restoring a backup folder into a selected destination

Always check the detected paths before syncing important saves. Detection is useful, but it is still heuristic.

## Supported sources

The scanner is designed around common Windows and Linux game-save locations:

- Windows user folders
- Steam Proton prefixes
- PortProton prefixes
- Bottles prefixes
- Heroic prefixes
- Lutris prefixes
- custom Wine roots

## Safety model

Game Save Sync Center is designed to avoid blind copying.

It tries to be safe by:

- showing paths before sync
- separating Windows and Linux candidates
- creating backups before copying
- writing sync logs
- filtering known non-game folders
- filtering common release-group and runtime folders

Still, this is alpha software. Review paths before syncing.

## Project structure

    app.py
      Entry point.

    gss/legacy_app.py
      Current main application logic.

    gss/ui/gnome.py
      GNOME-style UI integration and top panel layout.

    gss/ui/gnome_hig.qss
      Application styling.

    gss/game_knowledge.py
      Game names, company names, scene/release-group names, and non-game folder filters.

    gss/external_db.py
      External database loading.

    tools/update_ludusavi_manifest.py
      Downloads the Ludusavi manifest.

## Development

Run syntax checks:

    python -m py_compile \
      app.py \
      gss/legacy_app.py \
      gss/game_knowledge.py \
      gss/external_db.py \
      gss/ui/gnome.py \
      tools/update_ludusavi_manifest.py

Run the app:

    python app.py

## Current status

This project is in alpha.

The scanner and sync logic already work, but the architecture is still being cleaned up. The next major task is splitting `gss/legacy_app.py` into smaller modules.

## Roadmap

- Split `gss/legacy_app.py` into smaller modules.
- Add profile editor UI.
- Add ignore-list editor UI.
- Add per-game custom rules.
- Add dry-run preview before batch sync.
- Add a better restore manager.
- Add screenshots.
- Add packaged launcher and desktop installer.
- Add tests for scanner and grouping logic.

## License

License is not finalized yet.
