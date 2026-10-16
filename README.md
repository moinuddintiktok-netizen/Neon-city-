# NEON CITY: SURVIVAL — VIP 3D EDITION

A Python/Panda3D third-person cyberpunk survival shooter with a procedural neon city, enemies, timed bosses, upgrades, collectibles, hovercars, and a Windows build workflow.

**Created by Chishti Bro Computers & Developers**  
**Founder: Moinuddin Chishti**

## Included files

- `neon_city_3d_vip.py` — complete game source
- `requirements.txt` — Python dependency
- `.github/workflows/main.yml` — GitHub Actions Windows build workflow
- `.gitignore` — ignores generated build files

## Features

- Real-time 3D scene with perspective camera, fog, and ambient/directional lighting
- Procedurally generated neon towers, lit windows, hologram panels, and central energy core
- Third-person operative, plasma fire, and particle effects
- Four enemy archetypes and timed district boss encounters
- XP, levels, weapon tiers, score, and saved high score
- Health, armor, ammo, medkits, credits, and data-crystal collectibles
- Hovercars, dash, status panel, pause/redeploy flow, and on-screen HUD
- GitHub Actions workflow that packages a Windows build as a downloadable artifact

## Controls

- `W A S D` or arrow keys — move
- Mouse — aim
- Left mouse button — fire
- `E` — enter/exit a nearby hovercar
- `F` — use a medkit
- `SPACE` — dash
- `TAB` — show/hide status panel
- `P` or `ESC` — pause/resume
- `ENTER` or `R` — start/redeploy

## Run on a computer

Install Python 3.11, then from the project directory run:

```bash
python -m pip install -r requirements.txt
python neon_city_3d_vip.py
```

A desktop environment and graphics support are required to run the game window.

## Build from GitHub mobile

1. Create or open a GitHub repository.
2. Upload `neon_city_3d_vip.py`, `requirements.txt`, `README.md`, and `.gitignore` to the repository root.
3. Create `.github/workflows/main.yml` and paste the included workflow exactly.
4. Commit the files to `main` or `master`.
5. Open the repository's **Actions** tab and wait for **Neon City VIP 3D Windows Build** to finish.
6. Open the successful run and download the artifact named `Neon-City-VIP-3D-Windows`.
7. Extract the downloaded ZIP and run `NeonCityVIP3D.exe`. Keep the extracted companion files in the same folder.

You can also start a build manually from the Actions tab using **Run workflow**.

## Build output

The workflow builds a **Windows desktop package**, not an Android APK. It uses PyInstaller one-folder mode because bundling Panda3D engine resources is generally more reliable that way. GitHub Actions is the actual Windows build environment; this project was syntax-checked in the authoring environment, but a successful Windows build and gameplay still need to be confirmed by running the workflow and testing the artifact on a Windows PC.

## Official documentation

- Panda3D manual: https://docs.panda3d.org/1.10/python/index
- PyInstaller usage: https://pyinstaller.org/en/stable/usage.html
