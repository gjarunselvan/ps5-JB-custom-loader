@echo off
echo Starting PS5 Payload Manager...
start http://localhost:8000
cd manager_app
python server.py
pause
