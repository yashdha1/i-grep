# igrep

Pattern and semantic search for image and PDF collections.

## One-command install (Windows)

From the repository root, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

After install, open a new terminal and use `igrep` directly.

## Linux setup

```bash
chmod +x ./scripts/setup_script.sh
./scripts/setup_script.sh
```

## Quick usage

```bash
# Track a folder
igrep --track "C:\path\to\images"

# Index tracked folders
igrep sync

# Pattern search
igrep "invoice"
igrep -i "invoice"
igrep -c "invoice"

# Semantic search
igrep -s "financial report summary"
igrep -s "financial report summary" 10
```

## CLI help

```bash
igrep --help
```
