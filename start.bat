@echo off
title DECC/VAE - Demarrage
color 0B

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

call "%ROOT_DIR%python_env.bat"
if not defined PYTHON_EXE (
    echo [ERREUR] Python Standalone introuvable dans python\
    echo Executez d'abord install.bat
    pause
    exit /b 1
)

if not exist "%ROOT_DIR%decc_vae\manage.py" (
    echo [ERREUR] Application Django introuvable.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo   DECC/VAE - Serveur local
echo   http://127.0.0.1:8000
echo   Compte : admin / admin123
echo   CTRL+C pour arreter (ou stop.bat)
echo ================================================================
echo.

start "" "http://127.0.0.1:8000"

cd /d "%ROOT_DIR%decc_vae"
"%PYTHON_EXE%" manage.py runserver 127.0.0.1:8000 --noreload
cd /d "%ROOT_DIR%"
pause
