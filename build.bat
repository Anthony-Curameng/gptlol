@echo off
py -m pytest
if errorlevel 1 exit /b 1

py -m PyInstaller wk-calculator.spec --noconfirm --clean
