# Build script for creating igrep-setup.exe using PyInstaller
# Usage: .\build_exe.ps1

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Building igrep-setup.exe" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Ensure uv is available (required to manage the environment)
Write-Host "[*] Checking for uv..." -ForegroundColor Yellow
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "[!] uv not found. Please install it first:" -ForegroundColor Red
    Write-Host "    irm https://astral.sh/uv/install.ps1 | iex" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[✓] uv found" -ForegroundColor Green
Write-Host ""

# Install PyInstaller via uv (isolated tool environment - no pip needed)
Write-Host "[*] Installing PyInstaller via uv..." -ForegroundColor Yellow
uv tool install pyinstaller
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Failed to install PyInstaller" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[✓] PyInstaller ready" -ForegroundColor Green
Write-Host ""

# Build from project root so imports resolve correctly
Write-Host "[*] Building executable..." -ForegroundColor Yellow
$projectRoot = (Get-Item "$PSScriptRoot\..").FullName
Push-Location $projectRoot
uv tool run pyinstaller --onefile --console --name="igrep-setup" scripts\setup_gui.py
$buildExit = $LASTEXITCODE
Pop-Location

if ($buildExit -ne 0) {
    Write-Host "[!] Build failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[✓] Build successful!" -ForegroundColor Green
Write-Host ""
Write-Host "The executable is located at:" -ForegroundColor Cyan
Write-Host "  dist\igrep-setup.exe  (in the project root)" -ForegroundColor White
Write-Host ""
Write-Host "Distribution instructions:" -ForegroundColor Cyan
Write-Host "  1. Copy dist\igrep-setup.exe to a folder"
Write-Host "  2. Users can double-click to run the installer"
Write-Host "  3. Or distribute as a release on GitHub"
Write-Host ""

Read-Host "Press Enter to exit"
