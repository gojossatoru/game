# Little Boar — Forest Run

A native offline desktop runner built with Python and pygame-ce. No browser or server is used. Custom procedural artwork depicts a striped baby boar and a layered forest; the reference images are not bundled assets.

## Windows

Install Python 3.12 or newer, then double-click `build-windows.bat`. The resulting `dist/LittleBoar.exe` runs without Python or internet. Windows executables must be built on Windows. Alternatively, push this repository to GitHub and download `LittleBoar-Windows` from the Build Windows game workflow's artifacts.

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
