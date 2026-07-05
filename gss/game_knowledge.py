import re
from pathlib import Path


def _norm(value: str) -> str:
    value = str(value or "").lower()
    value = value.replace("&", " and ")
    value = value.replace("+", " plus ")
    value = re.sub(r"[^a-z0-9а-яё]+", "", value)
    return value.strip()


def _words(value: str) -> set[str]:
    return {
        _norm(x)
        for x in re.split(r"[^a-zA-Z0-9а-яА-ЯёЁ]+", str(value or ""))
        if _norm(x)
    }


EXTRA_GAME_NAMES_RAW = """
RoboCop Rogue City
RoboCop Rogue City Unfinished Business
RoboCop Unfinished Business
Silent Hill 2
Silent Hill Homecoming
Silent Hill Downpour
Metal Gear Solid Delta Snake Eater
Metal Gear Solid V The Phantom Pain
Metal Gear Solid V Ground Zeroes
Metal Gear Rising Revengeance
Death Stranding
Death Stranding Director's Cut
Alan Wake
Alan Wake 2
Control
Quantum Break
Max Payne
Max Payne 2
Max Payne 3
F.E.A.R.
F.E.A.R. 2 Project Origin
F.E.A.R. 3
Trepang2
Half-Life
Half-Life 2
Half-Life Alyx
Black Mesa
Portal
Portal 2
Left 4 Dead
Left 4 Dead 2
Team Fortress 2
Counter-Strike 2
Counter-Strike Global Offensive
Dota 2
The Witcher
The Witcher 2
The Witcher 3 Wild Hunt
Cyberpunk 2077
Red Dead Redemption
Red Dead Redemption 2
Grand Theft Auto III
Grand Theft Auto Vice City
Grand Theft Auto San Andreas
Grand Theft Auto IV
Grand Theft Auto V
Bully Scholarship Edition
L.A. Noire
Max Payne
Mafia
Mafia II
Mafia III
Mafia Definitive Edition
Mafia The Old Country
Far Cry
Far Cry 2
Far Cry 3
Far Cry 4
Far Cry 5
Far Cry 6
Far Cry Primal
Crysis
Crysis Warhead
Crysis 2
Crysis 3
Crysis Remastered
Crysis 2 Remastered
Crysis 3 Remastered
Battlefield 3
Battlefield 4
Battlefield 1
Battlefield V
Battlefield 2042
Battlefield Hardline
Call of Duty
Call of Duty 2
Call of Duty 4 Modern Warfare
Call of Duty World at War
Call of Duty Modern Warfare 2
Call of Duty Black Ops
Call of Duty Modern Warfare 3
Call of Duty Black Ops II
Call of Duty Ghosts
Call of Duty Advanced Warfare
Call of Duty Black Ops III
Call of Duty Infinite Warfare
Call of Duty WWII
Call of Duty Black Ops 4
Call of Duty Modern Warfare
Call of Duty Black Ops Cold War
Call of Duty Vanguard
Call of Duty Modern Warfare II
Call of Duty Modern Warfare III
Wolfenstein The New Order
Wolfenstein The Old Blood
Wolfenstein II The New Colossus
Wolfenstein Youngblood
DOOM
DOOM Eternal
DOOM The Dark Ages
Quake
Quake II
Quake 4
RAGE
RAGE 2
Prey
Dishonored
Dishonored 2
Dishonored Death of the Outsider
Deus Ex Human Revolution
Deus Ex Mankind Divided
Thief
BioShock
BioShock 2
BioShock Infinite
System Shock
System Shock 2
Metro 2033
Metro Last Light
Metro Exodus
S.T.A.L.K.E.R. Shadow of Chernobyl
S.T.A.L.K.E.R. Clear Sky
S.T.A.L.K.E.R. Call of Pripyat
S.T.A.L.K.E.R. 2 Heart of Chornobyl
Atomic Heart
Terminator Resistance
Terminator Resistance Annihilation Line
Terminator Dark Fate Defiance
Aliens Fireteam Elite
Alien Isolation
Aliens Colonial Marines
Predator Hunting Grounds
Avatar Frontiers of Pandora
Borderlands
Borderlands 2
Borderlands 3
Borderlands The Pre-Sequel
Tiny Tina's Wonderlands
Destiny 2
Warframe
The Division
The Division 2
Ghost Recon Wildlands
Ghost Recon Breakpoint
Splinter Cell
Splinter Cell Chaos Theory
Splinter Cell Conviction
Splinter Cell Blacklist
Rainbow Six Siege
Rainbow Six Extraction
Ready or Not
SWAT 4
Insurgency Sandstorm
Squad
Hell Let Loose
Arma 3
Ground Branch
Zero Hour
Six Days in Fallujah
Escape from Tarkov
Hunt Showdown
PUBG Battlegrounds
Apex Legends
Fortnite
Overwatch
Overwatch 2
Titanfall
Titanfall 2
Mirror's Edge
Mirror's Edge Catalyst
Mass Effect
Mass Effect 2
Mass Effect 3
Mass Effect Andromeda
Mass Effect Legendary Edition
Dragon Age Origins
Dragon Age II
Dragon Age Inquisition
Dragon Age The Veilguard
Baldur's Gate
Baldur's Gate II
Baldur's Gate 3
Divinity Original Sin
Divinity Original Sin 2
Pillars of Eternity
Pillars of Eternity II Deadfire
Pathfinder Kingmaker
Pathfinder Wrath of the Righteous
Wasteland 2
Wasteland 3
Disco Elysium
Planescape Torment
Torment Tides of Numenera
Fallout
Fallout 2
Fallout 3
Fallout New Vegas
Fallout 4
Fallout 76
The Elder Scrolls III Morrowind
The Elder Scrolls IV Oblivion
The Elder Scrolls V Skyrim
Skyrim Special Edition
Skyrim Anniversary Edition
Starfield
Kingdom Come Deliverance
Kingdom Come Deliverance II
Mount and Blade Warband
Mount and Blade II Bannerlord
Gothic
Gothic II
Gothic 3
Risen
Risen 2
Risen 3
ELEX
ELEX II
Two Worlds
GreedFall
GreedFall II
Vampire The Masquerade Bloodlines
Vampire The Masquerade Bloodlines 2
The Outer Worlds
The Outer Worlds 2
Avowed
Pillars of Eternity
Hogwarts Legacy
Elden Ring
Dark Souls
Dark Souls II
Dark Souls III
Sekiro Shadows Die Twice
Armored Core VI Fires of Rubicon
Lies of P
Lords of the Fallen
Nioh
Nioh 2
Wo Long Fallen Dynasty
Code Vein
Mortal Shell
Remnant From the Ashes
Remnant II
Monster Hunter World
Monster Hunter Rise
Monster Hunter Wilds
Dragon's Dogma
Dragon's Dogma 2
Devil May Cry 4
Devil May Cry 5
Resident Evil
Resident Evil 0
Resident Evil 2
Resident Evil 3
Resident Evil 4
Resident Evil 5
Resident Evil 6
Resident Evil 7 Biohazard
Resident Evil Village
Resident Evil Revelations
Resident Evil Revelations 2
Dead Space
Dead Space 2
Dead Space 3
Dead Space Remake
The Callisto Protocol
The Evil Within
The Evil Within 2
Outlast
Outlast 2
Amnesia The Dark Descent
Amnesia Rebirth
Amnesia The Bunker
SOMA
Layers of Fear
Observer
Blair Witch
Little Nightmares
Little Nightmares II
Little Nightmares III
Alone in the Dark
Fatal Frame Maiden of Black Water
Tormented Souls
Signalis
Until Dawn
The Quarry
The Dark Pictures Anthology Man of Medan
The Dark Pictures Anthology Little Hope
The Dark Pictures Anthology House of Ashes
The Dark Pictures Anthology The Devil in Me
Detroit Become Human
Heavy Rain
Beyond Two Souls
Life is Strange
Life is Strange Before the Storm
Life is Strange 2
Life is Strange True Colors
Tell Me Why
Twin Mirror
The Walking Dead
The Wolf Among Us
Batman The Telltale Series
Tales from the Borderlands
Minecraft Story Mode
Firewatch
What Remains of Edith Finch
Gone Home
The Vanishing of Ethan Carter
Dear Esther
Everybody's Gone to the Rapture
Stray
Outer Wilds
No Man's Sky
Subnautica
Subnautica Below Zero
Raft
The Forest
Sons Of The Forest
Green Hell
Valheim
V Rising
Rust
DayZ
Project Zomboid
Don't Starve
Don't Starve Together
ARK Survival Evolved
ARK Survival Ascended
Conan Exiles
Palworld
Terraria
Starbound
Core Keeper
Minecraft
Vintage Story
RimWorld
Factorio
Satisfactory
Dyson Sphere Program
Oxygen Not Included
Frostpunk
Frostpunk 2
Cities Skylines
Cities Skylines II
SimCity
The Sims
The Sims 2
The Sims 3
The Sims 4
Planet Coaster
Planet Zoo
Jurassic World Evolution
Jurassic World Evolution 2
Two Point Hospital
Two Point Campus
Prison Architect
Workers & Resources Soviet Republic
Anno 1404
Anno 1800
Tropico 4
Tropico 5
Tropico 6
Civilization IV
Civilization V
Civilization VI
Civilization VII
Humankind
Old World
Crusader Kings II
Crusader Kings III
Europa Universalis IV
Victoria 3
Hearts of Iron IV
Stellaris
Imperator Rome
Total War Rome
Total War Medieval II
Total War Shogun 2
Total War Rome II
Total War Attila
Total War Warhammer
Total War Warhammer II
Total War Warhammer III
Total War Three Kingdoms
Total War Pharaoh
Company of Heroes
Company of Heroes 2
Company of Heroes 3
Warhammer 40000 Dawn of War
Warhammer 40000 Dawn of War II
Warhammer 40000 Dawn of War III
Warhammer 40000 Space Marine
Warhammer 40000 Space Marine 2
Warhammer 40000 Darktide
Warhammer Vermintide
Warhammer Vermintide 2
StarCraft
StarCraft II
Warcraft III
Diablo
Diablo II
Diablo III
Diablo IV
World of Warcraft
Hearthstone
Heroes of the Storm
Overwatch
Age of Empires II Definitive Edition
Age of Empires III Definitive Edition
Age of Empires IV
Age of Mythology Retold
Stronghold
Stronghold Crusader
Stronghold Warlords
Command and Conquer Remastered
Command and Conquer Red Alert
Command and Conquer Red Alert 2
Command and Conquer Red Alert 3
Command and Conquer Generals
Supreme Commander
Supreme Commander 2
Homeworld
Homeworld 2
Homeworld 3
Northgard
They Are Billions
Against the Storm
Manor Lords
Dwarf Fortress
Battle Brothers
XCOM Enemy Unknown
XCOM 2
Phoenix Point
Gears Tactics
Marvel's Midnight Suns
Into the Breach
FTL Faster Than Light
Slay the Spire
Hades
Hades II
Bastion
Transistor
Pyre
Dead Cells
Hollow Knight
Hollow Knight Silksong
Ori and the Blind Forest
Ori and the Will of the Wisps
Celeste
Cuphead
Shovel Knight
Undertale
Deltarune
Stardew Valley
Graveyard Keeper
My Time at Portia
My Time at Sandrock
Coral Island
Farming Simulator 17
Farming Simulator 19
Farming Simulator 22
Farming Simulator 25
Euro Truck Simulator 2
American Truck Simulator
SnowRunner
MudRunner
BeamNG.drive
Assetto Corsa
Assetto Corsa Competizione
Assetto Corsa EVO
Forza Horizon 4
Forza Horizon 5
Forza Motorsport
Need for Speed Underground
Need for Speed Underground 2
Need for Speed Most Wanted
Need for Speed Carbon
Need for Speed Hot Pursuit
Need for Speed Rivals
Need for Speed Heat
Need for Speed Unbound
Burnout Paradise
The Crew
The Crew 2
The Crew Motorfest
F1 2020
F1 2021
F1 22
F1 23
F1 24
DiRT Rally
DiRT Rally 2.0
DiRT 5
WRC
EA Sports WRC
Rocket League
Trackmania
TrackMania Nations Forever
Wreckfest
MX Bikes
Ride 4
Ride 5
Microsoft Flight Simulator
Microsoft Flight Simulator 2024
X-Plane 11
X-Plane 12
DCS World
Kerbal Space Program
Kerbal Space Program 2
Elite Dangerous
EVE Online
Star Citizen
X4 Foundations
Hardspace Shipbreaker
Everspace
Everspace 2
Chorus
Ace Combat 7
Project Wingman
Hi-Fi RUSH
Bayonetta
Bayonetta 2
NieR Automata
NieR Replicant
Metal Gear Rising Revengeance
Vanquish
Yakuza 0
Yakuza Kiwami
Yakuza Kiwami 2
Yakuza 3
Yakuza 4
Yakuza 5
Yakuza 6
Yakuza Like a Dragon
Like a Dragon Infinite Wealth
Like a Dragon Ishin
Judgment
Lost Judgment
Persona 3 Reload
Persona 4 Golden
Persona 5 Royal
Shin Megami Tensei V Vengeance
Final Fantasy VII Remake
Final Fantasy XV
Final Fantasy XVI
Final Fantasy XIV
Final Fantasy X X-2 HD Remaster
Final Fantasy XII The Zodiac Age
Dragon Quest XI
Octopath Traveler
Octopath Traveler II
Triangle Strategy
Chrono Trigger
Tales of Arise
Tales of Berseria
Tales of Vesperia
Scarlet Nexus
The Legend of Heroes Trails in the Sky
The Legend of Heroes Trails of Cold Steel
Ys VIII Lacrimosa of Dana
Ys IX Monstrum Nox
Ys X Nordics
Granblue Fantasy Relink
Street Fighter V
Street Fighter 6
Tekken 7
Tekken 8
Mortal Kombat 11
Mortal Kombat 1
Injustice 2
Guilty Gear Strive
Dragon Ball FighterZ
Soulcalibur VI
King of Fighters XV
MultiVersus
Brawlhalla
Lethal Company
Content Warning
Among Us
Phasmophobia
Dead by Daylight
Killing Floor
Killing Floor 2
Killing Floor 3
Payday 2
Payday 3
Left 4 Dead
Back 4 Blood
Deep Rock Galactic
Helldivers
Helldivers 2
Risk of Rain 2
Vampire Survivors
Brotato
Balatro
Cult of the Lamb
Dave the Diver
Dredge
Inscryption
Return of the Obra Dinn
Papers Please
The Case of the Golden Idol
The Talos Principle
The Talos Principle 2
The Witness
Baba Is You
Human Fall Flat
Superliminal
Viewfinder
Cocoon
Inside
Limbo
Planet of Lana
Tunic
Death's Door
Hyper Light Drifter
Katana ZERO
Hotline Miami
Hotline Miami 2
Ruiner
Shadow Warrior
Shadow Warrior 2
Shadow Warrior 3
Serious Sam
Serious Sam 4
Duke Nukem 3D
Dusk
Amid Evil
Ion Fury
Prodeus
Turbo Overkill
Ultrakill
Cultic
Selaco
Turok
Turok 2
Postal 2
Postal 4
High on Life
The Ascent
Cyber Shadow
Ghostrunner
Ghostrunner 2
A Plague Tale Innocence
A Plague Tale Requiem
Hellblade Senua's Sacrifice
Senua's Saga Hellblade II
Tomb Raider
Rise of the Tomb Raider
Shadow of the Tomb Raider
Uncharted Legacy of Thieves Collection
Marvel's Spider-Man Remastered
Marvel's Spider-Man Miles Morales
Marvel's Spider-Man 2
God of War
God of War Ragnarok
Horizon Zero Dawn
Horizon Forbidden West
Days Gone
The Last of Us Part I
Returnal
Ratchet and Clank Rift Apart
Ghost of Tsushima Director's Cut
Deathloop
Redfall
Forza Horizon
Gears 5
Gears of War Ultimate Edition
Halo The Master Chief Collection
Halo Infinite
Sea of Thieves
State of Decay
State of Decay 2
Psychonauts
Psychonauts 2
Grounded
Pentiment
Hi-Fi Rush
Ori
As Dusk Falls
Tell Me Why
Quantum Break
Ryse Son of Rome
Kena Bridge of Spirits
Immortals Fenyx Rising
Assassin's Creed
Assassin's Creed II
Assassin's Creed Brotherhood
Assassin's Creed Revelations
Assassin's Creed III
Assassin's Creed IV Black Flag
Assassin's Creed Rogue
Assassin's Creed Unity
Assassin's Creed Syndicate
Assassin's Creed Origins
Assassin's Creed Odyssey
Assassin's Creed Valhalla
Assassin's Creed Mirage
Assassin's Creed Shadows
Prince of Persia The Sands of Time
Prince of Persia The Lost Crown
Watch Dogs
Watch Dogs 2
Watch Dogs Legion
The Settlers
Might and Magic Heroes
Trials Rising
Trackmania
South Park The Stick of Truth
South Park The Fractured But Whole
Hitman
Hitman 2
Hitman 3
Hitman World of Assassination
Kane and Lynch
Just Cause
Just Cause 2
Just Cause 3
Just Cause 4
Mad Max
Sleeping Dogs
Saints Row
Saints Row 2
Saints Row The Third
Saints Row IV
Agents of Mayhem
Prototype
Prototype 2
Middle-earth Shadow of Mordor
Middle-earth Shadow of War
Batman Arkham Asylum
Batman Arkham City
Batman Arkham Origins
Batman Arkham Knight
Gotham Knights
Suicide Squad Kill the Justice League
Marvel's Avengers
Guardians of the Galaxy
LEGO Star Wars The Skywalker Saga
LEGO Batman
LEGO Batman 2
LEGO Batman 3
LEGO Marvel Super Heroes
LEGO Marvel Super Heroes 2
LEGO City Undercover
Minecraft Dungeons
Ori and the Blind Forest
Ori and the Will of the Wisps
Alice Madness Returns
American McGee's Alice
Prince of Persia
Beyond Good and Evil
Rayman Legends
Rayman Origins
Spyro Reignited Trilogy
Crash Bandicoot N Sane Trilogy
Crash Team Racing Nitro-Fueled
SpongeBob SquarePants Battle for Bikini Bottom Rehydrated
Teenage Mutant Ninja Turtles Shredder's Revenge
Cuphead
A Hat in Time
Yooka-Laylee
Psychonauts
Sonic Mania
Sonic Frontiers
Sonic Generations
Sonic Superstars
Sonic Adventure DX
Sonic Adventure 2
Mega Man 11
Mega Man X Legacy Collection
Castlevania Advance Collection
Bloodstained Ritual of the Night
Blasphemous
Blasphemous 2
Salt and Sanctuary
Salt and Sacrifice
Ender Lilies
Ender Magnolia
Noita
Spelunky
Spelunky 2
Rogue Legacy
Rogue Legacy 2
Enter the Gungeon
The Binding of Isaac Rebirth
Darkest Dungeon
Darkest Dungeon II
Loop Hero
Moonlighter
Children of Morta
Wizard of Legend
Gunfire Reborn
Roboquest
Void Bastards
System Shock
Prey
Voidtrain
Chernobylite
Miasma Chronicles
Mutant Year Zero Road to Eden
Shadowrun Returns
Shadowrun Dragonfall
Shadowrun Hong Kong
Wartales
Kenshi
Stoneshard
The Long Dark
Firewatch
Road 96
Pacific Drive
Maneater
Abzu
Journey
Flower
Solar Ash
The Pathless
Sable
Lake
Eastward
Sea of Stars
Chained Echoes
CrossCode
Moonring
Citizen Sleeper
Norco
Kentucky Route Zero
Oxenfree
Oxenfree II
Night in the Woods
Spiritfarer
Unpacking
A Short Hike
Coffee Talk
VA-11 Hall-A
Slime Rancher
Slime Rancher 2
PowerWash Simulator
House Flipper
House Flipper 2
Cooking Simulator
PC Building Simulator
PC Building Simulator 2
Car Mechanic Simulator
Thief Simulator
Gas Station Simulator
Contraband Police
Police Simulator Patrol Officers
Train Sim World
Train Sim World 2
Train Sim World 3
Train Sim World 4
Train Sim World 5
Bus Simulator
Construction Simulator
Cities in Motion
Planet Crafter
Medieval Dynasty
Sengoku Dynasty
Bellwright
Enshrouded
Nightingale
Once Human
Soulmask
Lightyear Frontier
Forever Skies
ICARUS
SCUM
The Isle
Path of Titans
HumanitZ
Abiotic Factor
7 Days to Die
Grounded
Smalland
Voidtrain
Sea of Thieves
Skull and Bones
Sid Meier's Pirates
Blackwake
Subnautica
Sunkenland
Hydroneer
Astroneer
Trailmakers
Besiege
Scrap Mechanic
Teardown
People Playground
Totally Accurate Battle Simulator
Ultimate Epic Battle Simulator
Mount and Blade II Bannerlord
Chivalry 2
Mordhau
For Honor
Kingdoms and Castles
Songs of Syx
Foundation
Banished
Timberborn
Farthest Frontier
Settlement Survival
Surviving Mars
Surviving the Aftermath
Endzone A World Apart
Ixion
Falling Frontier
Homeworld Deserts of Kharak
Dune Spice Wars
Endless Space
Endless Space 2
Endless Legend
Galactic Civilizations III
Galactic Civilizations IV
Sins of a Solar Empire
Sins of a Solar Empire II
Age of Wonders III
Age of Wonders 4
SpellForce 3
The Battle for Middle-earth
Majesty
Heroes of Might and Magic III
Heroes of Might and Magic V
Songs of Conquest
King's Bounty
King's Bounty II
Dorfromantik
Mini Metro
Mini Motorways
Opus Magnum
Infinifactory
SpaceChem
TIS-100
SHENZHEN I/O
Exapunks
BATTLETECH
MechWarrior 5 Mercenaries
MechWarrior Online
Armored Core VI
Daemon X Machina
Zone of the Enders
Earth Defense Force 4.1
Earth Defense Force 5
Earth Defense Force 6
Lost Planet
Lost Planet 2
Lost Planet 3
Earthfall
World War Z
World War Z Aftermath
Days Gone
Dying Light
Dying Light 2
Dead Island
Dead Island 2
Dead Rising
Dead Rising 2
Dead Rising 3
Dead Rising 4
State of Decay
State of Decay 2
The Walking Dead Saints and Sinners
Arizona Sunshine
Vertigo 2
Boneworks
Bonelab
Blade and Sorcery
Pavlov VR
Half-Life Alyx
Beat Saber
Superhot
Superhot VR
SUPERHOT MIND CONTROL DELETE
"""

EXTRA_COMPANY_NAMES_RAW = """
Valve
Steam
Steamworks
Electronic Arts
EA Games
EA Sports
BioWare
DICE
Criterion
Respawn
Ubisoft
Ubisoft Montreal
Ubisoft Quebec
Ubisoft Toronto
Rockstar Games
Rockstar North
Take-Two Interactive
2K
2K Games
2K Czech
Gearbox Software
Bethesda
Bethesda Softworks
Bethesda Game Studios
id Software
Arkane Studios
MachineGames
Tango Gameworks
Obsidian Entertainment
inXile Entertainment
Ninja Theory
Double Fine
Mojang
343 Industries
The Coalition
Playground Games
Turn 10 Studios
Rare
Sony Interactive Entertainment
PlayStation Studios
Naughty Dog
Santa Monica Studio
Insomniac Games
Guerrilla Games
Housemarque
Bend Studio
Sucker Punch Productions
Kojima Productions
Konami
Capcom
Square Enix
Bandai Namco
FromSoftware
SEGA
Atlus
Ryu Ga Gotoku Studio
PlatinumGames
Team Ninja
Koei Tecmo
NIS America
Falcom
CD Projekt RED
Larian Studios
Remedy Entertainment
Bloober Team
Frictional Games
Red Barrels
Supermassive Games
Quantic Dream
Dontnod Entertainment
Telltale Games
IO Interactive
Avalanche Studios
Warner Bros Games
Rocksteady Studios
Monolith Productions
NetherRealm Studios
TT Games
Crystal Dynamics
Eidos Montreal
Treyarch
Infinity Ward
Sledgehammer Games
Raven Software
Bungie
Digital Extremes
Epic Games
Riot Games
Blizzard Entertainment
Activision
Paradox Interactive
Paradox Development Studio
Creative Assembly
Relic Entertainment
Firaxis Games
Amplitude Studios
Triumph Studios
Slitherine
Wargaming
Gaijin Entertainment
Bohemia Interactive
Offworld Industries
VOID Interactive
New World Interactive
Krafton
Bluehole
Facepunch Studios
11 bit studios
Klei Entertainment
Re-Logic
ConcernedApe
Supergiant Games
Motion Twin
Team Cherry
Moon Studios
Playdead
Campo Santo
Annapurna Interactive
Devolver Digital
Raw Fury
Focus Entertainment
Saber Interactive
Asobo Studio
Giants Software
SCS Software
Reiza Studios
Kunos Simulazioni
Milestone
Codemasters
Frontier Developments
Hello Games
Unknown Worlds
Endnight Games
Iron Gate
Coffee Stain Studios
Wube Software
Ludeon Studios
Keen Software House
Zachtronics
Landfall Games
Tarsier Studios
Mundfish
GSC Game World
4A Games
Techland
The Farm 51
Teyon
Frogwares
Crytek
Croteam
Flying Wild Hog
New Blood Interactive
3D Realms
Nightdive Studios
Blackbird Interactive
Gearbox Publishing
Perfect World
Tencent
NetEase
Pearl Abyss
NCSoft
Amazon Games
Game Science
Embark Studios
Arrowhead Game Studios
Fatshark
Ghost Ship Games
Starbreeze
OVERKILL
Tripwire Interactive
10 Chambers
Behaviour Interactive
Kinetic Games
Zeekerss
"""

SCENE_GROUPS_RAW = """
SKIDROW
RELOADED
Razor1911
Razor 1911
RUNE
CODEX
FLT
FAIRLIGHT
PLAZA
CPY
EMPRESS
TENOKE
Goldberg
Goldberg SteamEmu
ALI213
3DM
DARKSiDERS
DARKZER0
DARKZERO
HOODLUM
DODI
FitGirl
ElAmigos
GOG
GOG Games
KaOs
KaOsKrew
Xatab
Mechanics
R.G. Mechanics
RG Mechanics
R.G. Catalyst
Catalyst
SEWN
P2P
Voksi
DeltaT
Chronos
TiNYiSO
HI2U
BAT
PROPHET
POSTMORTEM
CODEX-RUNE-FLT
CODEX RUNE FLT
Public Steam
OnlineFix
Online Fix
SmartSteamEmu
CreamAPI
CreamInstaller
Nemirtingas
Mr Goldberg
Anadius
"""

EXTRA_NON_GAME_RAW = """
Docker
Docker Desktop
dockerdesktop
ms-playwright-go
playwright
ai.opencode.desktop
OpenCode
AMD
NVIDIA
Intel
Realtek
Epic Online Services
EOS
CEF
Chromium
CrashReportClient
Crash Reports
CrashDumps
Logs
Temp
Cache
Caches
ShaderCache
Shader Cache
GPUCache
D3DSCache
DXCache
GLCache
VulkanCache
UnrealEngine
Unity
UnityHub
Godot
Microsoft
Windows
Packages
Adobe
Mozilla
Google
Discord
Telegram Desktop
Spotify
OBS
obs-studio
Steam
Steamworks Shared
Proton
Proton Experimental
Proton Hotfix
Proton EasyAntiCheat Runtime
Proton BattlEye Runtime
SteamLinuxRuntime
Steam Linux Runtime
Steamworks Common Redistributables
DirectX
VC Redist
Visual C++
BattlEye
EasyAntiCheat
EAC
EOSOverlayRenderer
Oculus
OpenXR
OpenVR
Razer
Logitech
Corsair
SteelSeries
ASUS
MSI
OEM
Public Steam
CODEX-RUNE-FLT
CODEX RUNE FLT
SKIDROW
RELOADED
RUNE
CODEX
FLT
FAIRLIGHT
CPY
EMPRESS
TENOKE
PLAZA
HOODLUM
Goldberg
OnlineFix
"""


EXTRA_GAMES = {_norm(x): x.strip() for x in EXTRA_GAME_NAMES_RAW.splitlines() if x.strip()}

try:
    from gss.external_db import load_ludusavi_titles as _load_ludusavi_titles
    for _title in _load_ludusavi_titles():
        EXTRA_GAMES.setdefault(_norm(_title), _title)
except Exception:
    pass
EXTRA_COMPANIES = {_norm(x): x.strip() for x in EXTRA_COMPANY_NAMES_RAW.splitlines() if x.strip()}
SCENE_GROUPS = {_norm(x): x.strip() for x in SCENE_GROUPS_RAW.splitlines() if x.strip()}
EXTRA_NON_GAME = {_norm(x) for x in EXTRA_NON_GAME_RAW.splitlines() if x.strip()}

SCENE_WORDS = set(SCENE_GROUPS)
NON_GAME_WORDS = set(EXTRA_NON_GAME) | SCENE_WORDS


def _extend_obj(obj, values: dict[str, str], kind: str):
    if obj is None:
        return

    if isinstance(obj, dict):
        sample = None
        try:
            sample = next(iter(obj.values()))
        except StopIteration:
            pass

        for key, display in values.items():
            if key in obj:
                continue

            if isinstance(sample, dict):
                entry = dict(sample)
                for k in ("name", "display", "title", "label"):
                    if k in entry:
                        entry[k] = display
                for k in ("type", "kind", "category"):
                    if k in entry:
                        entry[k] = kind
                obj[key] = entry
            else:
                obj[key] = display

    elif isinstance(obj, set):
        obj.update(values.keys())
        obj.update(values.values())

    elif isinstance(obj, list):
        existing = {_norm(x) for x in obj}
        for display in values.values():
            if _norm(display) not in existing:
                obj.append(display)


def _extend_setlike(obj, values: set[str]):
    if obj is None:
        return

    if isinstance(obj, set):
        obj.update(values)
    elif isinstance(obj, list):
        existing = {_norm(x) for x in obj}
        for value in values:
            if value not in existing:
                obj.append(value)
    elif isinstance(obj, dict):
        for value in values:
            obj.setdefault(value, value)


def is_scene_or_noise_name(name: str) -> bool:
    n = _norm(name)
    if not n:
        return True

    if n in NON_GAME_WORDS:
        return True

                                                                     
    if "publicsteam" in n and any(x in n for x in SCENE_WORDS):
        return True

    if any(x in n for x in ("codexruneflt", "codexrune", "runeflt")):
        return True

    tokens = _words(name)
    if tokens and tokens.issubset(NON_GAME_WORDS):
        return True

    return False


def canonical_game_name(name: str) -> str | None:
    n = _norm(name)
    if n in EXTRA_GAMES:
        return EXTRA_GAMES[n]

                                                                           
    for key, display in EXTRA_GAMES.items():
        if len(key) >= 6 and (key in n or n in key):
            return display

    return None


def install_game_knowledge(ns: dict):
                   
    for var in (
        "KNOWN_PROFILES",
        "KNOWN_GAMES",
        "GAME_PROFILES",
        "KNOWN_GAME_NAMES",
    ):
        _extend_obj(ns.get(var), EXTRA_GAMES, "game")

                                                
    company_values = dict(EXTRA_COMPANIES)
    company_values.update(SCENE_GROUPS)

    for var in (
        "COMPANY_FOLDERS",
        "KNOWN_COMPANIES",
        "PUBLISHER_FOLDERS",
        "PUBLISHER_NAMES",
        "KNOWN_PUBLISHERS",
    ):
        _extend_obj(ns.get(var), company_values, "company")

                            
    for var in (
        "NON_GAME_FOLDERS",
        "IGNORE_FOLDERS",
        "NOISE_FOLDERS",
        "SYSTEM_FOLDERS",
    ):
        _extend_setlike(ns.get(var), NON_GAME_WORDS)

    return {
        "games": len(EXTRA_GAMES),
        "companies": len(EXTRA_COMPANIES),
        "scene_groups": len(SCENE_GROUPS),
        "non_game": len(NON_GAME_WORDS),
    }


def install_group_filter(ns: dict):
    old = ns.get("group_candidates")
    if old is None or getattr(old, "_game_knowledge_wrapped", False):
        return

    def wrapped_group_candidates(candidates):
        groups = old(candidates)

        cleaned = []
        for g in groups:
            name = getattr(g, "name", "")

            if is_scene_or_noise_name(name):
                continue

            canonical = canonical_game_name(name)
            if canonical:
                try:
                    g.name = canonical
                except Exception:
                    pass
                try:
                    g.confidence = "exact"
                except Exception:
                    pass

            cleaned.append(g)

        return cleaned

    wrapped_group_candidates._game_knowledge_wrapped = True
    ns["group_candidates"] = wrapped_group_candidates
