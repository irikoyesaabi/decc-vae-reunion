@echo off
title DECC/VAE - INSTALLATION AUTOMATIQUE
color 0A

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

echo ================================================================
echo   DECC/VAE - INSTALLATION AUTOMATIQUE
echo   Version avec Python Standalone Build
echo ================================================================
echo.

:: ============================================================
:: 1. VÉRIFICATION ET INSTALLATION DE MICROSOFT VISUAL C++
:: ============================================================

echo [1/7] Verification de Microsoft Visual C++ Redistributable...

set "VCREDIST_OK=0"

:: DLL runtime (Python Standalone / ReportLab / Pillow)
if exist "%SystemRoot%\System32\vcruntime140.dll" set "VCREDIST_OK=1"
if exist "%SystemRoot%\SysWOW64\vcruntime140.dll" set "VCREDIST_OK=1"

:: Registre VC++ 2015-2022 (x64)
reg query "HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" /v Installed >nul 2>&1
if not errorlevel 1 set "VCREDIST_OK=1"
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" /v Installed >nul 2>&1
if not errorlevel 1 set "VCREDIST_OK=1"
reg query "HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\X64" /v Installed >nul 2>&1
if not errorlevel 1 set "VCREDIST_OK=1"

if "%VCREDIST_OK%"=="1" (
    echo    - Microsoft Visual C++ Redistributable deja present.
    echo.
    goto vcredist_ok
)

echo    - Microsoft Visual C++ Redistributable non trouve.
echo    - Installation requise pour Python et les exports PDF/Excel.
echo.

set "VCREDIST_EXE="
if exist "%ROOT_DIR%redist\vc_redist.x64.exe" set "VCREDIST_EXE=%ROOT_DIR%redist\vc_redist.x64.exe"
if exist "%ROOT_DIR%vendor\vc_redist.x64.exe" set "VCREDIST_EXE=%ROOT_DIR%vendor\vc_redist.x64.exe"
if exist "%ROOT_DIR%vc_redist.x64.exe" set "VCREDIST_EXE=%ROOT_DIR%vc_redist.x64.exe"

if not defined VCREDIST_EXE (
    echo    Telechargement de VC_redist.x64.exe (Visual C++ 2015-2022 x64)...
    if not exist "%ROOT_DIR%vendor" mkdir "%ROOT_DIR%vendor"
    powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile '%ROOT_DIR%vendor\vc_redist.x64.exe' -UseBasicParsing } catch { exit 1 }"
    if errorlevel 1 (
        echo [ERREUR] Echec du telechargement du Redistributable.
        echo Placez vc_redist.x64.exe dans le dossier vendor\ (cle USB hors ligne)
        echo ou telechargez : https://aka.ms/vs/17/release/vc_redist.x64.exe
        pause
        exit /b 1
    )
    set "VCREDIST_EXE=%ROOT_DIR%vendor\vc_redist.x64.exe"
)

echo    Installation de Visual C++ Redistributable (droits administrateur possibles)...
"%VCREDIST_EXE%" /install /passive /norestart
if errorlevel 1 (
    echo [ATTENTION] Installation automatique echouee.
    echo Relancez install.bat en tant qu'administrateur, ou installez manuellement :
    echo   %VCREDIST_EXE%
    pause
    exit /b 1
)
echo    - Microsoft Visual C++ Redistributable installe.
echo.

:vcredist_ok


:: ============================================================
:: 2. VÉRIFICATION ET TÉLÉCHARGEMENT DE PYTHON STANDALONE
:: ============================================================

echo [2/7] Verification de Python Standalone Build...

call "%ROOT_DIR%python_env.bat"
if defined PYTHON_EXE (
    echo    - Python Standalone Build trouve : %PYTHON_EXE%
    "%PYTHON_EXE%" --version
    echo.
    goto python_present
)

echo    - Python Standalone Build non trouve dans python\
echo    - Telechargement en cours...
echo.

:: Définition de la version de Python Standalone à télécharger
set "PYTHON_VERSION=3.11.12"
set "PYTHON_DATE=20250409"
set "PYTHON_ARCH=x86_64-pc-windows-msvc"
set "PYTHON_TYPE=install_only_stripped"
set "PYTHON_FILENAME=cpython-%PYTHON_VERSION%+%PYTHON_DATE%-%PYTHON_ARCH%-%PYTHON_TYPE%.tar.gz"
set "PYTHON_URL=https://github.com/astral-sh/python-build-standalone/releases/download/%PYTHON_DATE%/%PYTHON_FILENAME%"

echo    Version : %PYTHON_VERSION%
echo    Fichier : %PYTHON_FILENAME%
echo.

:: Téléchargement
echo    Telechargement de Python Standalone Build...
powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%TEMP%\%PYTHON_FILENAME%'"
if errorlevel 1 (
    echo [ERREUR] Echec du telechargement.
    echo.
    echo Veuillez telecharger manuellement depuis :
    echo https://github.com/astral-sh/python-build-standalone/releases
    echo.
    pause
    exit /b 1
)

:: Extraction
echo    Extraction de l'archive...
if not exist "%ROOT_DIR%python" mkdir "%ROOT_DIR%python"
tar -xzf "%TEMP%\%PYTHON_FILENAME%" -C "%ROOT_DIR%python" --strip-components=1
if errorlevel 1 (
    echo [ERREUR] Echec de l'extraction.
    echo Veuillez installer 7-Zip ou WinRAR pour extraire manuellement.
    pause
    exit /b 1
)

:: Nettoyage
del "%TEMP%\%PYTHON_FILENAME%" 2>nul
echo    - Python Standalone Build installe avec succes.
echo.

:python_present
call "%ROOT_DIR%python_env.bat"


:: ============================================================
:: 3. CONFIGURATION DE L'ENVIRONNEMENT
:: ============================================================

echo [3/7] Verification de l'environnement Python...
if not defined PYTHON_EXE (
    echo [ERREUR] python.exe introuvable dans python\ ou python\install\
    pause
    exit /b 1
)
"%PYTHON_EXE%" --version
if errorlevel 1 (
    echo [ERREUR] Python ne fonctionne pas correctement.
    pause
    exit /b 1
)
echo.


:: ============================================================
:: 4. VÉRIFICATION ET INSTALLATION DE PIP
:: ============================================================

echo [4/7] Verification de pip...

"%PYTHON_EXE%" -m pip --version >nul 2>&1
if errorlevel 1 (
    echo    - pip non trouve. Installation en cours...
    
    :: Téléchargement de get-pip.py
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%TEMP%\get-pip.py'"
    if errorlevel 1 (
        echo [ERREUR] Echec du telechargement de get-pip.py.
        pause
        exit /b 1
    )
    
    :: Installation de pip
    "%PYTHON_EXE%" "%TEMP%\get-pip.py" --no-warn-script-location
    if errorlevel 1 (
        echo [ERREUR] Echec de l'installation de pip.
        pause
        exit /b 1
    )
    
    del "%TEMP%\get-pip.py" 2>nul
    echo    - pip installe avec succes.
) else (
    echo    - pip deja installe.
)
echo.


:: ============================================================
:: 5. INSTALLATION DES DÉPENDANCES
:: ============================================================

echo [5/7] Installation des dependances...

:: Mise à jour de pip
echo    - Mise a jour de pip...
"%PYTHON_EXE%" -m pip install --no-cache-dir --upgrade pip

:: Installation des dépendances
echo    - Installation des dependances (cela peut prendre quelques minutes)...
"%PYTHON_EXE%" -m pip install --no-cache-dir -r requirements.txt
if errorlevel 1 (
    echo [ERREUR] Echec de l'installation des dependances.
    pause
    exit /b 1
)
echo.


:: ============================================================
:: 6. CONFIGURATION DE LA BASE DE DONNÉES
:: ============================================================

echo [6/7] Configuration de la base de donnees...

cd "%ROOT_DIR%decc_vae"

:: Création des dossiers nécessaires
if not exist "data" mkdir data
if not exist "media" mkdir media
if not exist "logs" mkdir logs
if not exist "staticfiles" mkdir staticfiles

:: Vérification du fichier .env
if not exist "%ROOT_DIR%.env" (
    echo    - Fichier .env non trouve. Creation par defaut...
    if exist "%ROOT_DIR%.env.example" (
        copy "%ROOT_DIR%.env.example" "%ROOT_DIR%.env" >nul
    ) else (
        echo SECRET_KEY=django-insecure-change-me-in-production > "%ROOT_DIR%.env"
        echo DEBUG=True >> "%ROOT_DIR%.env"
        echo ALLOWED_HOSTS=127.0.0.1,localhost >> "%ROOT_DIR%.env"
        echo DATABASE_ENGINE=sqlite >> "%ROOT_DIR%.env"
        echo SQLITE_DB_NAME=data/db.sqlite3 >> "%ROOT_DIR%.env"
    )
    echo    - Fichier .env cree.
)

:: Création des migrations
echo    - Creation des migrations...
"%PYTHON_EXE%" manage.py makemigrations reunions
if errorlevel 1 (
    echo [ERREUR] Echec de la creation des migrations.
    cd "%ROOT_DIR%"
    pause
    exit /b 1
)

:: Application des migrations
echo    - Application des migrations...
"%PYTHON_EXE%" manage.py migrate
if errorlevel 1 (
    echo [ERREUR] Echec de l'application des migrations.
    cd "%ROOT_DIR%"
    pause
    exit /b 1
)

:: Collecte des fichiers statiques
echo    - Collecte des fichiers statiques...
"%PYTHON_EXE%" manage.py collectstatic --noinput --clear
if errorlevel 1 (
    echo [ATTENTION] Echec de la collecte des fichiers statiques.
)

cd "%ROOT_DIR%"
echo.


:: ============================================================
:: 7. CRÉATION DU SUPERUTILISATEUR
:: ============================================================

echo [7/7] Creation du superutilisateur...

cd "%ROOT_DIR%decc_vae"
"%PYTHON_EXE%" create_superuser.py
if errorlevel 1 (
    echo [ATTENTION] Echec de la creation du superutilisateur.
    echo Vous pourrez le creer manuellement avec : python manage.py createsuperuser
)

cd "%ROOT_DIR%"

echo.
echo ================================================================
echo   INSTALLATION TERMINEE AVEC SUCCES !
echo ================================================================
echo.
echo   Python Standalone Build : %PYTHON_VERSION%
echo   Base de donnees : SQLite (par defaut)
echo   Compte admin : admin / admin123
echo.
echo   Pour lancer l'application : double-cliquez sur start.bat
echo.
pause