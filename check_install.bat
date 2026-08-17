@echo off
title DECC/VAE - Verification
color 0B
set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"
call "%ROOT_DIR%python_env.bat"

echo ================================================================
echo   DECC/VAE - VERIFICATION DE L'INSTALLATION
echo ================================================================
echo.

set "OK=1"
if defined PYTHON_EXE (
    echo [OK] Python : %PYTHON_EXE%
    "%PYTHON_EXE%" --version
) else (
    echo [MANQUE] Python Standalone (dossier python\)
    set "OK=0"
)

if exist "%SystemRoot%\System32\vcruntime140.dll" (
    echo [OK] Visual C++ Redistributable (vcruntime140.dll)
) else (
    echo [MANQUE] Visual C++ Redistributable
    echo         Placez redist\vc_redist.x64.exe puis lancez install.bat
    set "OK=0"
)

if exist "%ROOT_DIR%decc_vae\manage.py" (
    echo [OK] Application Django
) else (
    echo [MANQUE] decc_vae\manage.py
    set "OK=0"
)

if exist "%ROOT_DIR%decc_vae\data\db.sqlite3" (
    echo [OK] Base SQLite
) else (
    echo [INFO] Base SQLite pas encore creee (lancez install.bat)
)

if defined PYTHON_EXE (
    "%PYTHON_EXE%" -c "import django; print('[OK] Django', django.get_version())" 2>nul
    if errorlevel 1 (
        echo [MANQUE] Django non installe
        set "OK=0"
    )
)

echo.
if "%OK%"=="1" (
    echo Installation prete. Lancez start.bat ou launch.vbs
) else (
    echo Des elements manquent. Executez install.bat
)
echo.
pause
