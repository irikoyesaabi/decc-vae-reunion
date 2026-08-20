@echo off
title DECC/VAE - MISE A JOUR
color 0B

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

echo ================================================================
echo   DECC/VAE - MISE A JOUR
echo   Version avec Python Standalone
echo   Les donnees existantes sont conservees
echo ================================================================
echo.

:: ============================================================
:: 1. VÉRIFICATION DE L'ENVIRONNEMENT
:: ============================================================

echo [1/7] Verification de l'environnement...

if not exist "%ROOT_DIR%python\python.exe" (
    echo [ERREUR] Python Standalone introuvable dans python\
    echo.
    echo Veuillez executer install.bat d'abord.
    pause
    exit /b 1
)

set "PYTHON_EXE=%ROOT_DIR%python\python.exe"

echo    - Python : %PYTHON_EXE%
"%PYTHON_EXE%" --version
if errorlevel 1 (
    echo [ERREUR] Python ne fonctionne pas correctement.
    pause
    exit /b 1
)
echo.

:: ============================================================
:: 2. SAUVEGARDE DES DONNÉES (SÉCURITÉ)
:: ============================================================

echo [2/7] Sauvegarde des donnees existantes...

set "BACKUP_DIR=%ROOT_DIR%backup_avant_maj"
set "TIMESTAMP=%DATE:/=-%_%TIME::=-%"
set "TIMESTAMP=%TIMESTAMP: =0%"

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

:: Sauvegarde de la base de données
if exist "%ROOT_DIR%decc_vae\data\db.sqlite3" (
    copy "%ROOT_DIR%decc_vae\data\db.sqlite3" "%BACKUP_DIR%\db_%TIMESTAMP%.sqlite3" >nul
    echo    - Base de donnees sauvegardee
) else (
    echo    - Aucune base de donnees trouvee
)

:: Sauvegarde des médias
if exist "%ROOT_DIR%decc_vae\media" (
    xcopy "%ROOT_DIR%decc_vae\media" "%BACKUP_DIR%\media_%TIMESTAMP%\" /E /I /Y >nul
    echo    - Fichiers medias sauvegardes
)

:: Sauvegarde des documents
if exist "%ROOT_DIR%documents" (
    xcopy "%ROOT_DIR%documents" "%BACKUP_DIR%\documents_%TIMESTAMP%\" /E /I /Y >nul
    echo    - Documents sauvegardes
)

:: Sauvegarde du fichier .env
if exist "%ROOT_DIR%.env" (
    copy "%ROOT_DIR%.env" "%BACKUP_DIR%\.env_%TIMESTAMP%" >nul
    echo    - Fichier .env sauvegarde
)

echo.

:: ============================================================
:: 3. MISE À JOUR DE PIP ET DES DÉPENDANCES
:: ============================================================

echo [3/7] Mise a jour de pip et des dependances...

:: Mise à jour de pip
echo    - Mise a jour de pip...
"%PYTHON_EXE%" -m pip install --no-cache-dir --upgrade pip
if errorlevel 1 (
    echo [ATTENTION] Mise a jour de pip echouee, poursuite...
)
echo.

:: Installation des dépendances
echo    - Installation des dependances...
if not exist "%ROOT_DIR%requirements.txt" (
    echo [ERREUR] requirements.txt introuvable !
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

:: ============================================================
:: 4. VÉRIFICATION DES DOSSIERS
:: ============================================================

echo [4/7] Verification des dossiers...

if not exist "%ROOT_DIR%decc_vae\manage.py" (
    echo [ERREUR] Application Django introuvable (decc_vae\manage.py).
    pause
    exit /b 1
)

:: Création des dossiers nécessaires
cd /d "%ROOT_DIR%decc_vae"
if not exist "data" mkdir data
if not exist "media" mkdir media
if not exist "logs" mkdir logs
if not exist "staticfiles" mkdir staticfiles
if not exist "media\logos" mkdir media\logos

echo    - Dossiers verifies
echo.

:: ============================================================
:: 5. VÉRIFICATION DU FICHIER .ENV
:: ============================================================

echo [5/7] Verification du fichier .env...

if not exist "%ROOT_DIR%.env" (
    echo    - Fichier .env absent, creation par defaut...
    if exist "%ROOT_DIR%.env.example" (
        copy "%ROOT_DIR%.env.example" "%ROOT_DIR%.env" >nul
        echo    - Fichier .env cree a partir de .env.example
    ) else (
        (
            echo SECRET_KEY=django-insecure-change-me-in-production
            echo DEBUG=True
            echo ALLOWED_HOSTS=127.0.0.1,localhost
            echo DATABASE_ENGINE=sqlite
            echo SQLITE_DB_NAME=data/db.sqlite3
            echo LANGUAGE_CODE=fr-fr
            echo TIME_ZONE=Africa/Niamey
            echo PDF_ENABLED=True
            echo WORD_ENABLED=True
            echo EXCEL_ENABLED=True
            echo LOG_LEVEL=INFO
            echo LOG_FILE=logs/decc_vae.log
        ) > "%ROOT_DIR%.env"
        echo    - Fichier .env cree par defaut
    )
) else (
    echo    - Fichier .env existe
)
echo.

:: ============================================================
:: 6. MIGRATIONS DJANGO
:: ============================================================

echo [6/7] Migrations Django (la base existante n'est pas ecrasee)...

echo    - Creation des migrations...
"%PYTHON_EXE%" manage.py makemigrations reunions
if errorlevel 1 (
    echo [ERREUR] Echec de la creation des migrations.
    cd /d "%ROOT_DIR%"
    pause
    exit /b 1
)

echo    - Application des migrations...
"%PYTHON_EXE%" manage.py migrate
if errorlevel 1 (
    echo [ERREUR] Echec de l'application des migrations.
    cd /d "%ROOT_DIR%"
    pause
    exit /b 1
)

echo    - Migrations appliquees avec succes
echo.

:: ============================================================
:: 7. COLLECTE DES FICHIERS STATIQUES
:: ============================================================

echo [7/7] Collecte des fichiers statiques...

"%PYTHON_EXE%" manage.py collectstatic --noinput --clear
if errorlevel 1 (
    echo [ATTENTION] Collecte des fichiers statiques partiellement echouee
) else (
    echo    - Fichiers statiques collectes avec succes
)

cd /d "%ROOT_DIR%"

:: ============================================================
:: FIN DE LA MISE À JOUR
:: ============================================================

echo.
echo ================================================================
echo   MISE A JOUR TERMINEE AVEC SUCCES !
echo ================================================================
echo.
echo   Sauvegarde disponible dans : %BACKUP_DIR%
echo.
echo   Resume :
echo   - Base de donnees : conservee
echo   - Medias : conserves
echo   - Documents : conserves
echo   - Migrations : appliquees
echo   - Fichiers statiques : collectes
echo.
echo   Lancez start.bat pour demarrer la nouvelle version
echo   Compte admin : admin / admin123 (sauf si modifie)
echo.
pause