@echo off
echo Starting Kade Connect API...
cd /d "S:\Projects\SLAIC001_Infinite\kade-connect"
"S:\Projects\SLAIC001_Infinite\kade-connect\venv\Scripts\uvicorn.exe" test_app:app --host 0.0.0.0 --port 8000
pause
