@echo off
title Cloudflare Tunnel - Django Local Server
echo ========================================================
echo Starting Cloudflare Tunnel for Django (port 8000)...
echo ========================================================
echo.

REM Look for cloudflared in Program Files or PATH
if exist "C:\Program Files (x86)\cloudflared\cloudflared.exe" (
    "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --protocol http2 --url http://localhost:8000
) else if exist "C:\Program Files\cloudflared\cloudflared.exe" (
    "C:\Program Files\cloudflared\cloudflared.exe" tunnel --protocol http2 --url http://localhost:8000
) else (
    cloudflared tunnel --protocol http2 --url http://localhost:8000
)

pause
