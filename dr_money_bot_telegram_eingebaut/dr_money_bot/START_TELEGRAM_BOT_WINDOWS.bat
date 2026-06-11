@echo off
cd /d "%~dp0"
echo DR Money Bot wird gestartet...
python -m pip install -r requirements.txt
python -m app.main_bot
pause
