@echo off
echo Cai PyInstaller va pynput...
pip install pyinstaller pynput

echo.
echo Dang dong goi...
pyinstaller ^
  --onefile ^
  --noconsole ^
  --name DarkOverlay ^
  --icon NONE ^
  main_windows.py

echo.
echo Xong! File exe nam trong thu muc: dist\DarkOverlay.exe
pause
