@echo off
cd /d "%~dp0"

echo ========================================
echo   Kagurazaka Core - Build Tool
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python not found. Install Python 3.10+
    pause
    exit /b 1
)

echo [*] Installing deps...
pip install -r "..\new core\requirements.txt" >nul 2>&1
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [*] Installing PyInstaller...
    pip install pyinstaller
)

taskkill /f /im Kagurazaka.exe >nul 2>&1

if exist "dist\Kagurazaka.exe" (
    echo [*] Removing old build...
    del /f /q "dist\Kagurazaka.exe" 2>nul
)
if exist "build\" rmdir /s /q "build" 2>nul

echo.
echo [*] Building Kagurazaka.exe (2-5 min) ...
echo.
pyinstaller build.spec --clean --noconfirm

if exist "dist\Kagurazaka.exe" (
    echo.
    echo ========================================
    echo   Build SUCCESS!
    echo   Output: dist\Kagurazaka.exe
    echo ========================================
    powershell -Command "$s=(Get-Item 'dist\Kagurazaka.exe').Length; Write-Host '   Size:' ([math]::Round($s/1MB,1)) 'MB'"
) else (
    echo.
    echo [!] Build FAILED. Check errors above.
)

pause
