# Little Boar — Forest Run

A native offline desktop runner built with Python and pygame-ce. No browser or server is used. The original supplied PNG atlases are bundled unchanged. The renderer selects sprite regions and scales proportionally, using the supplied day/night variants and boar poses.

## Windows

Install Python 3.12 or newer, then double-click `build-windows.bat`. The resulting `dist/LittleBoar/LittleBoar.exe` runs without Python or internet. Windows executables must be built on Windows. Alternatively, push this repository to GitHub and download `LittleBoar-Windows` from the Build Windows game workflow's artifacts.

## Run from source

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python game.py
```

Tap Space, Up or W for a short jump; hold for a longer jump. Down or S slides. P or Escape pauses; Enter activates menu buttons. Losing window focus pauses the game.

Jump over rocks and pits; slide beneath birds and branches. Almonds spawn with 80% probability and award 1 point, walnuts 17% / 5 points, acorns 3% / 10 points. Score counts collected nuts only. Day and night alternate every 45 seconds of active play. Speed increases by 18 pixels/second every minute, from 330 up to 510. Best score persists in `%LOCALAPPDATA%/LittleBoar/score.json` on Windows, or `~/.local/share/LittleBoar/score.json` elsewhere.

## Validation

`python -m unittest discover -s tests`

The tests exercise jump duration, nut values, obstacle collisions, sliding, cycle/speed boundaries and menu rendering. Windows packaging is configured in `.github/workflows/windows.yml`; Linux validation does not establish a tested Windows binary.

Updated sprites use the supplied individual cutouts. White cutout backgrounds become transparent at load time; source PNGs remain unchanged. Rocks and birds have a 50% left/right mirror chance; background trees also vary orientation. Birds appear at four heights. Locally synthesized collection oinks distinguish acorns. Audio is optional when no sound device is available. The sleeping boar appears inside the game-over overlay only.


## Windows download safety

Extract the entire downloaded ZIP and keep `_internal` next to `LittleBoar.exe`. The build now produces a regular application folder, without executable packing or runtime self-extraction. GitHub publishes the artifact only after a Windows Defender signature update and scan succeed. The download includes the scan status and SHA-256 checksums. A checksum identifies a file; it is not proof of safety.

The executable is currently unsigned. Chrome or Windows may still block an unfamiliar application, even after a clean scan. Do not disable browser or antivirus protections. Persistent false positives require vendor review and/or legitimate publisher code signing; packaging changes cannot guarantee warning removal.

Tree obstacles replace floating branches; individual trees are no longer background decorations. Slide beneath their branches. Ground tiles are clipped out of pit spans and share the same terrain scale. Night rendering darkens object sprites and adds stars, while retaining the supplied night boar/forest variants. Game over plays one descending sad oink.

Terrain now scrolls as persistent, contiguous ground and pit tiles without clipping the background. Rocks have two collision-matched sizes; trees and nuts are larger. Nuts glow in both themes and retain their daytime colors at night.

Day/night changes now crossfade over four seconds at each 45-second boundary. Forest strips alternate mirrored orientation. Trees and rocks are doubled in size, and the boar is 1.3 times larger, with adjusted collision sizes and jump strength. Obstacles use 3.2–4.2 second spawn intervals and at least 480 pixels of clear space (increasing with speed), including around pits.
