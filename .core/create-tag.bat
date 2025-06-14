@echo off
set /p tag=Enter tag version: 
git tag -a %tag% -m "Release %tag% - Refer to CHANGELOG.md for update details"
git push origin %tag%
pause
