@echo off
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 exit /b 1
.venv\Scripts\python -m pip install -r requirements.txt pyinstaller==6.22.3
if errorlevel 1 exit /b 1
.venv\Scripts\python -m PyInstaller --noconfirm --clean --onedir --noupx --windowed --add-data "sprites;sprites" --name LittleBoar game.py
if errorlevel 1 exit /b 1
echo Game ready: dist\LittleBoar\LittleBoar.exe
pause
