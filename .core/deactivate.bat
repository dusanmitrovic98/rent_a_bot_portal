@echo off
REM Check if environment is active
if not defined VIRTUAL_ENV (
    echo No active virtual environment.
    exit /b 1
)

deactivate