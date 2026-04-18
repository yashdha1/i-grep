# Windows PowerShell Installer for igrep
# Run with: powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\install.ps1"

$ErrorActionPreference = "Stop"

$defaultRepoUrl = "https://github.com/YashDhadod/igrep.git"
$repoUrl = if ($env:IGREP_REPO_URL) { $env:IGREP_REPO_URL } else { $defaultRepoUrl }

function Resolve-InstallDir() {
    if ($PSScriptRoot) {
        $candidate = (Get-Item "$PSScriptRoot\..").FullName
        if (Test-Path (Join-Path $candidate "pyproject.toml")) {
            return $candidate
        }
    }

    $targetDir = Join-Path $env:USERPROFILE "igrep"

    if (Test-Path (Join-Path $targetDir "pyproject.toml")) {
        Write-Host "[*] Using existing checkout at: $targetDir" -ForegroundColor Cyan
        return $targetDir
    }

    if (-not (Test-Command "git")) {
        throw "git is required for remote install mode. Install git or run installer from a local checkout."
    }

    Write-Host "[*] Local repo not detected. Cloning igrep to: $targetDir" -ForegroundColor Yellow
    if (Test-Path $targetDir) {
        Remove-Item -Recurse -Force $targetDir
    }

    git clone $repoUrl $targetDir
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path (Join-Path $targetDir "pyproject.toml"))) {
        throw "Failed to clone igrep from $repoUrl"
    }

    return $targetDir
}

function Test-Command([string]$name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

function Refresh-SessionPath() {
    $machinePath = [System.Environment]::GetEnvironmentVariable("PATH", "Machine")
    $userPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
    $env:PATH = @($machinePath, $userPath) -join ";"
}

function Add-ToUserPath([string]$dir) {
    $regPath = "HKCU:\Environment"
    $currentPath = (Get-ItemProperty -Path $regPath -Name PATH -ErrorAction SilentlyContinue).PATH
    if ($currentPath -notlike "*$dir*") {
        $newPath = if ($currentPath) { "$currentPath;$dir" } else { $dir }
        Set-ItemProperty -Path $regPath -Name PATH -Value $newPath
        Write-Host "[✓] Added to PATH: $dir" -ForegroundColor Green
    } else {
        $newPath = $currentPath
        Write-Host "[✓] Already in PATH: $dir" -ForegroundColor Green
    }

    [System.Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    if ($env:PATH -notlike "*$dir*") {
        $env:PATH += ";$dir"
    }
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

# Get installation directory. Supports local checkout and remote (irm | iex) bootstrap.
$installDir = Resolve-InstallDir
Write-Host "[*] Installation directory: $installDir" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: uv ──────────────────────────────────────────────────────────────
Write-Host "--- Step 1/4: Python package manager (uv) ---" -ForegroundColor Yellow
if (Test-Command "uv") {
    Write-Host "[✓] uv already installed" -ForegroundColor Green
} else {
    Write-Host "[*] Installing uv..." -ForegroundColor Yellow
    try {
        $ProgressPreference = 'SilentlyContinue'
        irm https://astral.sh/uv/install.ps1 | iex
        Refresh-SessionPath

        if (-not (Test-Command "uv")) {
            $uvCandidateDirs = @(
                "$env:USERPROFILE\.local\bin",
                "$env:USERPROFILE\.cargo\bin"
            )
            foreach ($candidateDir in $uvCandidateDirs) {
                if ((Test-Path $candidateDir) -and ($env:PATH -notlike "*$candidateDir*")) {
                    $env:PATH += ";$candidateDir"
                }
            }
        }

        if (-not (Test-Command "uv")) {
            throw "uv was installed but is not available in this session"
        }

        Write-Host "[✓] uv installed" -ForegroundColor Green
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
} elseif (Test-Command "tesseract") {
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
        Refresh-SessionPath
        if (Test-Path $tessExe) {
            $tessDir = "C:\Program Files\Tesseract-OCR"
            $tessData = "$tessDir\tessdata"
        } elseif (Test-Command "tesseract") {
            $tessDir = Split-Path (Get-Command tesseract).Source
            $tessData = "$tessDir\tessdata"
        }
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
    Write-Host "[!] Failed to install igrep" -ForegroundColor Red
    Pop-Location; Read-Host "Press Enter to exit"; exit 1
}
Write-Host "[✓] igrep installed" -ForegroundColor Green
Pop-Location
Write-Host ""

# ── Step 4: igrep command & DB setup ─────────────────────────────────────────
Write-Host "--- Step 4/4: igrep command & database setup ---" -ForegroundColor Yellow

$wrapperPath = Join-Path $installDir "igrep.bat"
$wrapperContent = @(
    "@echo off",
    "set SCRIPT_DIR=%~dp0",
    "cd /d \"%SCRIPT_DIR%\"",
    "call uv run python main.py %*"
)
Set-Content -Path $wrapperPath -Value $wrapperContent -Encoding ASCII
Write-Host "[✓] Created command wrapper: $wrapperPath" -ForegroundColor Green
Add-ToUserPath $installDir

Write-Host "[*] Running igrep setup (downloads ~90 MB ONNX model)..." -ForegroundColor Yellow
Push-Location $installDir
uv run igrep setup
$setupExitCode = $LASTEXITCODE
Pop-Location
if ($setupExitCode -ne 0) {
    Write-Host "[!] Setup failed. Retry with: uv run igrep setup" -ForegroundColor Red
    Read-Host "Press Enter to exit"; exit 1
}

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

