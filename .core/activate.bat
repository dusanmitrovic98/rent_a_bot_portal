@echo off
REM Check if .venv exists, create if missing
if not exist "..\.venv\" (
    echo Creating virtual environment...
    python -m venv ..\.venv || exit /b 1
)

REM Activate the environment
call ..\.venv\Scripts\activate.bat