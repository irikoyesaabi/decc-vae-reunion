@echo off
title DECC/VAE - Arret du serveur
color 0C

echo.
echo ================================================================
echo   ARRET DU SERVEUR
echo ================================================================
echo.

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    set "PID=%%a"
    goto found_pid
)

echo [INFO] Aucun serveur en cours.
pause
exit /b 0

:found_pid
echo [INFO] Arret du processus PID: %PID%
taskkill /F /PID %PID% >nul 2>&1
echo [OK] Serveur arrete.
pause