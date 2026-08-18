@echo off
title DECC/VAE - MISE A JOUR
color 0B

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

echo ================================================================
echo   DECC/VAE - MISE A JOUR (sans reinstaller Python)
echo   La base SQLite existante est conservee.
echo ================================================================
echo.

if not exist "%ROOT_DIR%python_env.bat" (
    echo [ERREUR] python_env.bat introuvable.
    pause
    exit /b 1
)

call "%ROOT_DIR%python_env.bat"
if not defined PYTHON_EXE (
    echo [ERREUR] Python Standalone introuvable dans python\
    echo Executez d'abord install.bat
    pause
    exit /b 1
)

echo [1/5] Python : %PYTHON_EXE%
"%PYTHON_EXE%" --version
if errorlevel 1 (
    echo [ERREUR] Python ne fonctionne pas.
    pause
    exit /b 1
)
echo.

echo [2/5] Mise a jour de pip...
"%PYTHON_EXE%" -m pip install --no-cache-dir --upgrade pip
if errorlevel 1 (
    echo [ATTENTION] Mise a jour de pip echouee, poursuite...
)
echo.

echo [3/5] Mise a jour des dependances (requirements.txt)...
if not exist "%ROOT_DIR%requirements.txt" (
    echo [ERREUR] requirements.txt introuvable.
    pause
    exit /b 1
)
"%PYTHON_EXE%" -m pip install --no-cache-dir -r "%ROOT_DIR%requirements.txt"
if errorlevel 1 (
    echo [ERREUR] Echec de l'installation des dependances.
    pause
    exit /b 1
)
echo.

if not exist "%ROOT_DIR%decc_vae\manage.py" (
    echo [ERREUR] Application Django introuvable (decc_vae\manage.py).
    pause
    exit /b 1
)

cd /d "%ROOT_DIR%decc_vae"
if not exist "data" mkdir data
if not exist "media" mkdir media
if not exist "logs" mkdir logs
if not exist "staticfiles" mkdir staticfiles

if not exist "%ROOT_DIR%.env" (
    echo    - Fichier .env absent, creation...
    if exist "%ROOT_DIR%.env.example" (
        copy "%ROOT_DIR%.env.example" "%ROOT_DIR%.env" >nul
    ) else (
        echo SECRET_KEY=django-insecure-change-me-in-production> "%ROOT_DIR%.env"
        echo DEBUG=True>> "%ROOT_DIR%.env"
        echo ALLOWED_HOSTS=127.0.0.1,localhost>> "%ROOT_DIR%.env"
        echo DATABASE_ENGINE=sqlite>> "%ROOT_DIR%.env"
        echo SQLITE_DB_NAME=data/db.sqlite3>> "%ROOT_DIR%.env"
    )
)

echo [4/5] Migrations Django (la base existante n'est pas ecrasee)...
"%PYTHON_EXE%" manage.py makemigrations reunions
"%PYTHON_EXE%" manage.py migrate
if errorlevel 1 (
    echo [ERREUR] Echec des migrations.
    cd /d "%ROOT_DIR%"
    pause
    exit /b 1
)
echo.

echo [5/5] Collecte des fichiers statiques...
"%PYTHON_EXE%" manage.py collectstatic --noinput
if errorlevel 1 (
    echo [ATTENTION] collectstatic a echoue.
)

cd /d "%ROOT_DIR%"

echo.
echo ================================================================
echo   MISE A JOUR TERMINEE
echo ================================================================
echo   Relancez l'application avec start.bat
echo   Compte admin inchange (sauf si vous l'avez deja modifie).
echo.
pause
