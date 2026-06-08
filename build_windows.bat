@echo off
cd /d "%~dp0"

call .venv\Scripts\activate.bat

python -m PyInstaller ^
  --name "Finance Saving App" ^
  --onedir ^
  --windowed ^
  --clean ^
  --noconfirm ^
  --collect-submodules sqlite3 ^
  --add-data "finance_saving_app\data;finance_saving_app\data" ^
  --add-data "finance_saving_app\icons;finance_saving_app\icons" ^
  launcher.py

echo Build complete.
explorer "dist\Finance Saving App"
pause