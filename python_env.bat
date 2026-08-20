@echo off
REM Localise le Python Standalone Build (dossier python\)
if not defined ROOT_DIR set "ROOT_DIR=%~dp0"

set "PYTHON_EXE="
set "PYTHONHOME="

if exist "%ROOT_DIR%python\python.exe" (
    set "PYTHON_EXE=%ROOT_DIR%python\python.exe"
    set "PYTHONHOME=%ROOT_DIR%python"
    goto :python_env_done
)
if exist "%ROOT_DIR%python\install\python.exe" (
    set "PYTHON_EXE=%ROOT_DIR%python\install\python.exe"
    set "PYTHONHOME=%ROOT_DIR%python\install"
    goto :python_env_done
)

:python_env_done
if defined PYTHONHOME (
    set "PATH=%PYTHONHOME%;%PYTHONHOME%\Scripts;%PATH%"
)
