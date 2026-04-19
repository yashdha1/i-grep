# igrep

Pattern and semantic search for image and PDF collections.

## One-command install

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
igrep <pattern> n 
igrep -i <pattern> n
igrep -c <pattern> n

# Semantic search
igrep -s <sentence> n 
igrep -s <sentence> n
```

## CLI help

```bash
igrep --help
```
