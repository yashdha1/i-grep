@echo off

REM Resolve project root (parent of the scripts\ folder)
set SCRIPT_DIR=%~dp0
set INSTALL_DIR=%SCRIPT_DIR%..
pushd "%INSTALL_DIR%"
set INSTALL_DIR=%CD%
popd

echo.
echo ==========================================
echo -e "${BOLD}"
echo "  ██╗ ██████╗ ██████╗ ███████╗██████╗ "
echo "  ██║██╔════╝ ██╔══██╗██╔════╝██╔══██╗"
echo "  ██║██║  ███╗██████╔╝█████╗  ██████╔╝"
echo "  ██║██║   ██║██╔══██╗██╔══╝  ██╔═══╝ "
echo "  ██║╚██████╔╝██║  ██║███████╗██║     "
echo "  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝     "
echo ""
echo ==========================================
echo          Windows Installation
echo ==========================================
echo.

REM ── Step 1: uv ────────────────────────────────────────────────────────────
echo --- Step 1/4: Python package manager (uv) ---
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [*] Installing uv...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    if %ERRORLEVEL% NEQ 0 (
        echo [!] Failed to install uv. Install from https://github.com/astral-sh/uv
        pause
        exit /b 1
    )
    set PATH=%PATH%;%USERPROFILE%\.local\bin;%USERPROFILE%\.cargo\bin
    echo [OK] uv installed
) else (
    echo [OK] uv already installed
)
echo.

REM ── Step 2: Tesseract OCR ─────────────────────────────────────────────────
echo --- Step 2/4: Tesseract OCR ---
set TESS_DIR=C:\Program Files\Tesseract-OCR
set TESS_EXE=%TESS_DIR%\tesseract.exe
set TESS_DATA=%TESS_DIR%\tessdata

if exist "%TESS_EXE%" (
    echo [OK] Tesseract already installed at: %TESS_DIR%
) else (
    where tesseract >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Tesseract already on PATH
        for %%I in (tesseract.exe) do set TESS_DIR=%%~dp$PATH:I
        set TESS_DIR=%TESS_DIR:~0,-1%
        set TESS_DATA=%TESS_DIR%\tessdata
    ) else (
        echo [*] Installing Tesseract via winget...
        winget install --id UB-Mannheim.TesseractOCR --accept-source-agreements --accept-package-agreements --silent
        if %ERRORLEVEL% NEQ 0 (
            echo [!] winget install failed.
            echo [*] Install manually: https://github.com/UB-Mannheim/tesseract/wiki
            echo [*] Continuing...
        ) else (
            echo [OK] Tesseract installed
        )
    )
)

REM Set TESSDATA_PREFIX and add Tesseract to PATH
if exist "%TESS_DATA%" (
    setx TESSDATA_PREFIX "%TESS_DATA%" >nul
    set TESSDATA_PREFIX=%TESS_DATA%
    echo [OK] TESSDATA_PREFIX set to: %TESS_DATA%
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=[System.Environment]::GetEnvironmentVariable('PATH','User'); if(-not $p){$p=''}; if($p -notlike '*%TESS_DIR%*'){[System.Environment]::SetEnvironmentVariable('PATH', ($p.TrimEnd(';') + ';%TESS_DIR%').Trim(';'), 'User')}"
    echo [OK] Tesseract added to PATH
) else (
    echo [!] tessdata folder not found - set TESSDATA_PREFIX manually after installing Tesseract
)
echo.

REM ── Step 3: Python dependencies ───────────────────────────────────────────
echo --- Step 3/4: Python dependencies ---
echo [*] Installing to: %INSTALL_DIR%
pushd "%INSTALL_DIR%"
call uv sync
if %ERRORLEVEL% NEQ 0 (
    echo [!] Failed to install dependencies
    popd
    pause
    exit /b 1
)
echo [OK] Dependencies installed
popd
echo.

REM ── Step 4: igrep command and DB setup ────────────────────────────────────
echo --- Step 4/4: igrep command and database setup ---

echo [*] Creating igrep wrapper...
set WRAPPER_PATH=%INSTALL_DIR%\igrep.bat
(
    echo @echo off
    echo set SCRIPT_DIR=%%~dp0
    echo cd /d "%%SCRIPT_DIR%%"
    echo call uv run python main.py %%*
) > "%WRAPPER_PATH%"
echo [OK] Wrapper created: %WRAPPER_PATH%

echo [*] Adding igrep to user PATH...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=[System.Environment]::GetEnvironmentVariable('PATH','User'); if(-not $p){$p=''}; if($p -notlike '*%INSTALL_DIR%*'){[System.Environment]::SetEnvironmentVariable('PATH', ($p.TrimEnd(';') + ';%INSTALL_DIR%').Trim(';'), 'User')}"
echo [OK] Added to PATH

echo [*] Running igrep setup (downloads ~90-100 MB embedding model)...
pushd "%INSTALL_DIR%"
call uv run python main.py setup
set SETUP_EXIT=%ERRORLEVEL%
popd
if %SETUP_EXIT% NEQ 0 (
    echo [!] Setup step failed - you can retry with: uv run igrep setup
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   Installation Complete!
echo ==========================================
echo.
echo   IMPORTANT: Open a NEW terminal window before running igrep.
echo   (PATH changes only apply to new sessions.)
echo.
echo Quick start:
echo   igrep --track "C:\path\to\your\images"
echo   igrep sync
echo   igrep "search term"
echo.
pause

