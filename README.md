# anattaGen Game Environment Manager

A desktop application to create isolated environments for PC games. 

## Features

*   Game indexing from user-selected directories.
*   Customizable options for each game.
*   Tabbed interface for Setup, Deployment, and Editing environments.

## Tech Stack

*   Python
*   Qt6 (for the main application)

# But, why???

## 3 Reasons:

**1.** Removing a Mickey Mouse sticker bricked the device and voided the repair warranty 

**2.** Steam has no gaemz

**3.** DRM / Malware concerns require *"unofficial patches"*

## Benfits:

**[+]** Offers a pre-configurated, self-contained portable environment for each game.

**[+]** Granular options with precise and individuated controls to customize joystick mappings, monitor layouts, audio outputs and more.

**[+]** Leverages native Windows shortcuts and languages for backwards compatibility.

**[+]** Executable identification, release/build versions, group-naemz and other extranious title abberations are intelligently handled to derive titles set by the publisher and the steam-database enables further metadata aqiuisition key to portability between computers, drives, and gaming-frontends.

## Use Case

Creates a specialized launcher and profile-folder (jacket) for each game which houses the game's shortcut/s and isolates settings such as
 keyboad-mapping and monitor layout.  Tools which automate the process of creating and loading presets for devices, games and settings at 
 a granular level are downloaded and installed from directly within the program.

Antimicro/X, JoyXoff, Joy2Key keymappers are supported.


## Installation
- This Version: **[CURV]**

- This Build: **[VERSION]**

Run the installer or extract the binary to a location of your choice, **or** download and build and run the source files and executables.
```sh
[RJ_PROJ]

			├──  bin
			│   ├──  aria2c.exe
			│   └──  7z.exe
			├──  Python
			│   ├──  ax_DeskTemplate.set
			│   ├──  ax_GameTemplate.set
			│   ├──  ax_KBM_Template.set
			│   ├──  ax_Trigger.set
			│   ├──  cmdtemplate.set
			│   ├──  config.ini
			│   ├──  config.set
			│   ├──  configparser.ConfigParser
			│   ├──  demoted.set
			│   ├──  exclude_exe.set
			│   ├──  folder_exclude.set
			│   ├──  Joystick.ico
			│   ├──  ks_Blank.set
			│   ├──  ks_DeskTemplate.set
			│   ├──  ks_GameTemplate.set
			│   ├──  ks_Trigger.set
			│   ├──  main.py
			│   ├──  main_test.py
			│   ├──  main_window_new.py
			│   ├──  release_groups.set
			│   ├──  repos.set
			│   ├──  requirements.txt
			│   ├──  steam.json
			│   |
			└──  README.md
			│   |
			│	└──  ui
			│       ├──  Install.png
			│       ├──  key.png
			│       ├──  runas.png
			│       ├──  Setup.png
			│       ├──  Tip.png
			│       └──  Update.png
			│       ├──  config_manager.py
			│       ├──  deployment_tab_ui.py
			│       ├──  editor_tab_ui.py
			│       ├──  game_indexer.py
			│       ├──  index_manager.py
			│       ├──  name_processor.py
			│       ├──  name_utils.py
			│       ├──  setup_tab_ui.py
			│       ├──  steam_cache.py
			│       ├──  steam_integration.py
			│       ├──  steam_processor.py
			│       ├──  steam_utils.py
			│       ├──  title_identifier.py
			│       └──  ui_widgets.py
			├──  bin
			│   ├──  aria2c.exe
			│   ├──  7za.exe
			│   ├──  lrDeploy.exe
			│   ├──  NewOSK.exe
			│   ├──  Setup.exe
			│   ├──  SkinHu.dll
			│   ├──  Source_Builder.exe
			│   ├──  Update.exe
			│   ├──  USkin.dll
			│   └──  [RJ_EXE].exe
			│
			├──  site
			│   ├──  AnkaCoder_b.otf
			│   ├──  index.html
			│   ├──  InterUI.html
			│   ├──  Hermit-Regular.otf
			│   ├──  key.ico
			│   ├──  ReadMe.md
			│   ├──  TruenoLt.otf
			│   ├──  version.txt
			│	└──  img
			│       ├──  Install.png
			│       ├──  key.png
			│       ├──  runas.png
			│       ├──  Setup.png
			│       ├──  Tip.png
			│       └──  Update.png
# Documentation

[Detailed Docs can be found here](https://[GIT_USER].github.io/[RJ_PROJ])

# Setup


## Launching Games
It is not necessary, but recommended to enable the RunAsAdmin option.
Ideally, [RJ_PROJ] can run entirely in userspace, however many games require administrator access where user-level hardware is unavailable or unreliable.

![AsAdmin](https://[GIT_USER].github.io/[RJ_PROJ]/img/runas.png)

During gameplay you may modify and/or create additional joystick profiles and any found within the game's jacket will be saved and reloaded for player 2/3/4, prioritizing the default profile-name eg: game-name/_#.gamecontroller.amgp, and other "player#" monikers.)

# W.I.P/To Do

Configuration, save and save-state locations are written to the Game.ini, however Cloud-Backup of Game-Saves and Game-Configuration files is a work in progress.  

I will likely end up adopting an open sourced file-sync service application. 