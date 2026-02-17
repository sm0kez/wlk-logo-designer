@echo off
title Walzlagerkoning Logo Designer

:: Ga naar de map waar dit BAT-bestand staat
cd /d "%~dp0"

echo.
echo  ========================================
echo    Walzlagerkoning Logo Designer v3.3
echo    Even geduld, app wordt gestart...
echo  ========================================
echo.
echo  Map: %~dp0
echo.

:: Probeer python te vinden
where python >nul 2>nul
if %errorlevel%==0 (
    python "%~dp0logo_designer.py"
    goto :end
)

where python3 >nul 2>nul
if %errorlevel%==0 (
    python3 "%~dp0logo_designer.py"
    goto :end
)

where py >nul 2>nul
if %errorlevel%==0 (
    py "%~dp0logo_designer.py"
    goto :end
)

:: Python niet gevonden
echo.
echo  ================ FOUT ================
echo  Python is niet gevonden op dit systeem!
echo.
echo  Ga naar: https://www.python.org/downloads/
echo  Download en installeer Python 3.10+
echo.
echo  BELANGRIJK: Vink aan "Add Python to PATH"
echo  ========================================
echo.
pause
goto :eof

:end
if %errorlevel% neq 0 (
    echo.
    echo  Er is een fout opgetreden (code: %errorlevel%)
    echo  Druk op een toets om af te sluiten.
    pause >nul
) else (
    exit
)