#!/usr/bin/env python3
"""
igrep Windows Setup Utility
Build exe with:
    cd scripts && uv tool run pyinstaller --onefile --console --name="igrep-setup" setup_gui.py
"""

import subprocess
import sys
import os
from pathlib import Path
import ctypes

# Default Tesseract install location on Windows (UB-Mannheim installer)
TESSERACT_DEFAULT = r"C:\Program Files\Tesseract-OCR"
TESSERACT_EXE    = os.path.join(TESSERACT_DEFAULT, "tesseract.exe")
TESSDATA_DEFAULT = os.path.join(TESSERACT_DEFAULT, "tessdata")


# ── Helpers ───────────────────────────────────────────────────────────────────

def is_admin() -> bool:
    try:
        return ctypes.windll.shell.IsUserAnAdmin()
    except Exception:
        return False


def run_command(cmd: str, description: str) -> bool:
    """Run a shell command, stream its output, return True on success."""
    print(f"\n[*] {description}...")
    try:
        result = subprocess.run(cmd, shell=True, text=True)
        if result.returncode == 0:
            print(f"[✓] {description} - Success")
            return True
        print(f"[!] {description} - Failed (exit {result.returncode})")
        return False
    except Exception as exc:
        print(f"[!] {description} - Error: {exc}")
        return False


def _broadcast_env_change() -> None:
    """Tell Explorer and open terminals that environment variables changed."""
    try:
        HWND_BROADCAST  = 0xFFFF
        WM_SETTINGCHANGE = 0x001A
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", 2, 5000, None
        )
    except Exception:
        pass


def _set_user_env(name: str, value: str) -> None:
    """Persist a user-level environment variable and broadcast the change."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
        winreg.CloseKey(key)
        os.environ[name] = value          # visible to this process immediately
        _broadcast_env_change()
        print(f"[✓] {name} = {value}")
    except Exception as exc:
        print(f"[!] Could not set {name}: {exc}")


def _add_to_user_path(directory: str) -> None:
    """Add directory to user PATH (HKCU) if not already present, then broadcast."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS
        )
        try:
            current = winreg.QueryValueEx(key, "PATH")[0]
        except OSError:
            current = ""
        dirs = [d for d in current.split(";") if d]
        if directory.lower() not in [d.lower() for d in dirs]:
            dirs.append(directory)
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, ";".join(dirs))
            print(f"[✓] Added to PATH: {directory}")
        else:
            print(f"[✓] Already in PATH: {directory}")
        winreg.CloseKey(key)
        # Also make it available in the current process
        os.environ["PATH"] = os.environ.get("PATH", "") + ";" + directory
        _broadcast_env_change()
    except Exception as exc:
        print(f"[!] Could not modify PATH: {exc}")


def _get_install_dir() -> str:
    """Resolve the project root regardless of how the script is run.

    When frozen (PyInstaller exe in dist/) we walk up from the exe until we
    find the directory containing both main.py and pyproject.toml.
    """
    if getattr(sys, 'frozen', False):
        candidate = Path(sys.executable).resolve().parent
        for _ in range(5):
            if (candidate / "main.py").is_file() and (candidate / "pyproject.toml").is_file():
                return str(candidate)
            candidate = candidate.parent
        return os.path.dirname(sys.executable)
    return str(Path(__file__).resolve().parent.parent)


# ── Installation steps ────────────────────────────────────────────────────────

def install_uv() -> bool:
    """Ensure uv is available, install if missing."""
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        print("[✓] uv is already installed")
        return True
    except Exception:
        print("[*] Installing uv...")
        cmd = (
            'powershell -NoProfile -ExecutionPolicy Bypass '
            '-Command "irm https://astral.sh/uv/install.ps1 | iex"'
        )
        ok = run_command(cmd, "uv installation")
        if ok:
            # Refresh PATH so uv is usable immediately
            uv_bin = os.path.join(os.environ.get("USERPROFILE", ""), ".local", "bin")
            os.environ["PATH"] = os.environ.get("PATH", "") + ";" + uv_bin
        return ok


def _find_tessdata() -> str:
    """Return the best tessdata directory we can find."""
    candidates = [
        TESSDATA_DEFAULT,
        r"C:\Program Files (x86)\Tesseract-OCR\tessdata",
        r"C:\ProgramData\Tesseract-OCR\tessdata",
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    return TESSDATA_DEFAULT   # fall back to expected default


def _configure_tesseract_env() -> None:
    """Set TESSDATA_PREFIX and add Tesseract bin dir to PATH."""
    tessdata = _find_tessdata()
    tess_bin = str(Path(tessdata).parent)

    print("\n[*] Configuring Tesseract environment...")
    _set_user_env("TESSDATA_PREFIX", tessdata)
    _add_to_user_path(tess_bin)


def install_tesseract() -> bool:
    """Install Tesseract via winget if not already present."""
    # Already installed?
    if os.path.isfile(TESSERACT_EXE):
        print(f"[✓] Tesseract already installed at: {TESSERACT_DEFAULT}")
        _configure_tesseract_env()
        return True

    # Already on PATH?
    try:
        r = subprocess.run(["tesseract", "--version"], capture_output=True, text=True)
        if r.returncode == 0:
            print("[✓] Tesseract already on PATH")
            _configure_tesseract_env()
            return True
    except Exception:
        pass

    print("\n[*] Installing Tesseract OCR via winget...")
    ok = run_command(
        "winget install --id UB-Mannheim.TesseractOCR "
        "--accept-source-agreements --accept-package-agreements --silent",
        "Tesseract OCR installation",
    )
    if not ok:
        print("\n[!] winget install failed.")
        print("[*] Install Tesseract manually from:")
        print("    https://github.com/UB-Mannheim/tesseract/wiki")
        print(f"    Recommended install path: {TESSERACT_DEFAULT}")
        print("[*] Continuing — other steps will still complete.")
        return False

    _configure_tesseract_env()
    return True


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    print("\n" + "=" * 52)
    print("  igrep - Image/PDF Search Tool")
    print("  Windows Setup")
    print("=" * 52)

    if not is_admin():
        print("\n[!] Note: Running without admin privileges.")
        print("[*] Right-click → 'Run as Administrator' for best results")
        print("[*] (needed for system-wide PATH changes)")
        input("\nPress Enter to continue anyway...")

    install_dir = _get_install_dir()
    print(f"\n[*] Installation directory: {install_dir}")

    # ── Step 1: uv ────────────────────────────────────────────────────────
    print("\n" + "-" * 40)
    print("  Step 1/4 — Python package manager (uv)")
    print("-" * 40)
    if not install_uv():
        print("\n[!] uv is required. Install from https://github.com/astral-sh/uv")
        input("\nPress Enter to exit...")
        return 1

    # ── Step 2: Tesseract OCR ─────────────────────────────────────────────
    print("\n" + "-" * 40)
    print("  Step 2/4 — Tesseract OCR (for image text extraction)")
    print("-" * 40)
    install_tesseract()   # non-fatal; user can install manually later

    # ── Step 3: Python dependencies ───────────────────────────────────────
    print("\n" + "-" * 40)
    print("  Step 3/4 — Python dependencies")
    print("-" * 40)
    os.chdir(install_dir)
    if not run_command("uv sync", "Installing Python dependencies"):
        print("\n[!] Failed to install dependencies")
        input("\nPress Enter to exit...")
        return 1

    # ── Step 4: igrep environment setup ───────────────────────────────────
    print("\n" + "-" * 40)
    print("  Step 4/4 — igrep command & database setup")
    print("-" * 40)

    # Create igrep.bat wrapper
    batch_path = Path(install_dir) / "igrep.bat"
    batch_content = (
        "@echo off\n"
        f'cd /d "{install_dir}"\n'
        "call uv run python main.py %*\n"
    )
    batch_path.write_text(batch_content, encoding="ascii")
    print(f"[✓] Wrapper created: {batch_path}")

    # Add install dir to user PATH
    print("\n[*] Registering igrep on user PATH...")
    _add_to_user_path(install_dir)

    # Download embedding model + initialise DB
    print("\n[*] Running igrep setup (downloads ~90-100 MB embedding model)...")
    run_command("uv run python main.py setup", "igrep setup")

    # ── Done ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 52)
    print("  Installation Complete!")
    print("=" * 52)
    print("\n  IMPORTANT — Open a NEW terminal window before using igrep.")
    print("  (PATH changes only apply to new sessions.)\n")
    print("Quick start:")
    print(r'  igrep --track "C:\path\to\your\images"')
    print("  igrep sync")
    print('  igrep "search term"')
    print("\nAll commands:")
    print('  igrep "search term"      — Pattern search')
    print('  igrep -i "search term"   — Ignore case')
    print('  igrep -c "search term"   — Count occurrences')
    print('  igrep -s "search term"   — Semantic search')
    print(r'  igrep --track "C:\path"  — Add folder to index')
    print('  igrep --track            — List tracked folders')
    print('  igrep sync               — Index tracked folders')
    print('  igrep setup              — Re-init DB / re-download model')
    print()
    input("Press Enter to exit...")
    return 0


if __name__ == "__main__":
    sys.exit(main())

