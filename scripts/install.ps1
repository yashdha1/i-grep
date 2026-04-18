# Windows PowerShell Installer for igrep
# Run with: powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\install.ps1"

$ErrorActionPreference = "Stop"

function Add-ToUserPath([string]$dir) {
    $regPath = "HKCU:\Environment"
    $current = (Get-ItemProperty -Path $regPath -Name PATH -ErrorAction SilentlyContinue).PATH
    if ($current -notlike "*$dir*") {
        $new = if ($current) { "$current;$dir" } else { $dir }
        Set-ItemProperty -Path $regPath -Name PATH -Value $new
        Write-Host "[✓] Added to PATH: $dir" -ForegroundColor Green
    } else {
        Write-Host "[✓] Already in PATH: $dir" -ForegroundColor Green
    }
    # Broadcast change so open Explorer windows pick it up
    $env:PATH += ";$dir"
    [System.Environment]::SetEnvironmentVariable("PATH", $new, "User")
}

function Set-UserEnv([string]$name, [string]$value) {
    [System.Environment]::SetEnvironmentVariable($name, $value, "User")
    Set-Item "env:$name" $value
    Write-Host "[✓] $name = $value" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  igrep - Image/PDF Search Tool" -ForegroundColor Cyan
Write-Host "  Windows Installation" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$isAdmin = ([Security.Principal.WindowsIdentity]::GetCurrent().Groups -contains "S-1-5-32-544")
if (-not $isAdmin) {
    Write-Host "[!] Not running as Administrator." -ForegroundColor Yellow
    Write-Host "[*] Right-click install.ps1 → 'Run with PowerShell as Admin' for best results." -ForegroundColor Yellow
    Write-Host ""
}

# Get installation directory (project root = parent of scripts/)
$installDir = (Get-Item "$PSScriptRoot\..").FullName
Write-Host "[*] Installation directory: $installDir" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: uv ──────────────────────────────────────────────────────────────
Write-Host "--- Step 1/4: Python package manager (uv) ---" -ForegroundColor Yellow
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host "[✓] uv already installed" -ForegroundColor Green
} else {
    Write-Host "[*] Installing uv..." -ForegroundColor Yellow
    try {
        $ProgressPreference = 'SilentlyContinue'
        irm https://astral.sh/uv/install.ps1 | iex
        Write-Host "[✓] uv installed" -ForegroundColor Green
        # Make uv available in current session
        $env:PATH += ";$env:USERPROFILE\.local\bin"
    } catch {
        Write-Host "[!] Failed to install uv. Install from https://github.com/astral-sh/uv" -ForegroundColor Red
        Read-Host "Press Enter to exit"; exit 1
    }
}
Write-Host ""

# ── Step 2: Tesseract OCR ────────────────────────────────────────────────────
Write-Host "--- Step 2/4: Tesseract OCR ---" -ForegroundColor Yellow
$tessDir  = "C:\Program Files\Tesseract-OCR"
$tessExe  = "$tessDir\tesseract.exe"
$tessData = "$tessDir\tessdata"

if (Test-Path $tessExe) {
    Write-Host "[✓] Tesseract already installed at: $tessDir" -ForegroundColor Green
} elseif (Get-Command tesseract -ErrorAction SilentlyContinue) {
    Write-Host "[✓] Tesseract already on PATH" -ForegroundColor Green
    $tessDir  = Split-Path (Get-Command tesseract).Source
    $tessData = "$tessDir\tessdata"
} else {
    Write-Host "[*] Installing Tesseract via winget..." -ForegroundColor Yellow
    winget install --id UB-Mannheim.TesseractOCR --accept-source-agreements --accept-package-agreements --silent
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] winget install failed." -ForegroundColor Yellow
        Write-Host "[*] Install manually: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Yellow
        Write-Host "[*] Continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "[✓] Tesseract installed" -ForegroundColor Green
    }
}

# Configure Tesseract environment
if (Test-Path $tessData) {
    Set-UserEnv "TESSDATA_PREFIX" $tessData
    Add-ToUserPath $tessDir
} else {
    Write-Host "[!] tessdata not found at $tessData — set TESSDATA_PREFIX manually after installing Tesseract" -ForegroundColor Yellow
}
Write-Host ""

# ── Step 3: Python dependencies ──────────────────────────────────────────────
Write-Host "--- Step 3/4: Python dependencies ---" -ForegroundColor Yellow
Push-Location $installDir
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Failed to install dependencies" -ForegroundColor Red
    Pop-Location; Read-Host "Press Enter to exit"; exit 1
}
Write-Host "[✓] Dependencies installed" -ForegroundColor Green
Pop-Location
Write-Host ""

# ── Step 4: igrep command & DB setup ─────────────────────────────────────────
Write-Host "--- Step 4/4: igrep command & database setup ---" -ForegroundColor Yellow

$wrapperPath = Join-Path $installDir "igrep.bat"
$batchContent = "@echo off`r`ncd /d `"$installDir`"`r`ncall uv run python main.py %*`r`n"
[System.IO.File]::WriteAllText($wrapperPath, $batchContent, [System.Text.Encoding]::ASCII)
Write-Host "[✓] Wrapper created: $wrapperPath" -ForegroundColor Green

Add-ToUserPath $installDir

Write-Host "[*] Running igrep setup (downloads ~90-100 MB embedding model)..." -ForegroundColor Yellow
Push-Location $installDir
uv run python main.py setup
Pop-Location

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  IMPORTANT: Open a NEW terminal window before running igrep." -ForegroundColor Yellow
Write-Host "  (PATH changes apply to new sessions only.)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Quick start:" -ForegroundColor Cyan
Write-Host '  igrep --track "C:\path\to\your\images"'
Write-Host "  igrep sync"
Write-Host '  igrep "search term"'
Write-Host ""
Read-Host "Press Enter to exit"

