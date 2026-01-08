@echo off
echo Installing requirements...
pip install -r requirements.txt
pip install pyinstaller

echo Cleaning up previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

echo Building Balise_Tester...
pyinstaller --noconfirm --onefile --windowed --name "Balise_Tester_v1.0" --add-data "data;data" --add-data "assets;assets" main.py

echo Build complete. Executable is in the dist folder.
pause
