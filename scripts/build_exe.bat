@echo off
REM Build script to create igrep-setup.exe using PyInstaller
REM Usage: .\build_exe.bat

echo.
echo =========================================
echo   Building igrep-setup.exe
echo =========================================
echo -e "${BOLD}"
echo "  ██╗ ██████╗ ██████╗ ███████╗██████╗ "
echo "  ██║██╔════╝ ██╔══██╗██╔════╝██╔══██╗"
echo "  ██║██║  ███╗██████╔╝█████╗  ██████╔╝"
echo "  ██║██║   ██║██╔══██╗██╔══╝  ██╔═══╝ "
echo "  ██║╚██████╔╝██║  ██║███████╗██║     "
echo "  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝     "
echo ""

REM Ensure uv is available
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [!] uv not found. Please install it first:
    echo     irm https://astral.sh/uv/install.ps1 ^| iex
    pause
    exit /b 1
)
echo [OK] uv found

REM Install PyInstaller via uv (isolated tool environment - no pip needed)
echo [*] Installing PyInstaller via uv...
uv tool install pyinstaller
if %ERRORLEVEL% NEQ 0 (
    echo [!] Failed to install PyInstaller
    pause
    exit /b 1
)
echo [OK] PyInstaller ready

echo [*] Building executable...
REM Run from project root; output goes to project_root\dist\
pushd "%~dp0.."
uv tool run pyinstaller --onefile --console --name="igrep-setup" scripts\setup_gui.py
set BUILD_EXIT=%ERRORLEVEL%
popd

if %BUILD_EXIT% NEQ 0 (
    echo [!] Build failed
    pause
    exit /b 1
)

echo.
echo [OK] Build successful!
echo.
echo The executable is located at:
echo   dist\igrep-setup.exe  (in the project root)
echo.
echo Users can now:
echo   1. Download igrep-setup.exe
echo   2. Double-click to run the installer
pause
