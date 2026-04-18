#!/usr/bin/env bash
# =============================================================================
# i-grep setup script
# Installs Tesseract (full + fast models) and sets up the Python environment
# Supports: Ubuntu/Debian, Fedora/RHEL, Arch Linux (Linux only)
# =============================================================================

set -e

# Resolve project root (parent of the scripts/ directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
RESET='\033[0m'

info()    { echo -e "${BLUE}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; exit 1; }
step()    { echo -e "\n${BOLD}▶ $*${RESET}"; }

# ── Detect OS (Linux only) ─────────────────────────────────────────────────────
detect_os() {
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        case "$ID" in
            ubuntu|debian|linuxmint|pop)  echo "debian" ;;
            fedora|rhel|centos|rocky)     echo "fedora" ;;
            arch|manjaro|endeavouros)     echo "arch"   ;;
            *)                             echo "unknown" ;;
        esac
    else
        echo "unknown"
    fi
}

OS=$(detect_os)
info "Detected OS: $OS"
if [[ "$OS" == "unknown" ]]; then
    error "This script supports Linux only (Debian/Ubuntu, Fedora/RHEL, Arch). Detected OS is not supported."
fi

# ── 1. Install Tesseract (system package) ─────────────────────────────────────
install_tesseract() {
    step "Installing Tesseract OCR"

    if command -v tesseract &>/dev/null; then
        TESS_VER=$(tesseract --version 2>&1 | head -1)
        success "Tesseract already installed: $TESS_VER"
        return 0
    fi

    case "$OS" in
        debian)
            info "Running: apt-get install tesseract-ocr tesseract-ocr-eng"
            sudo apt-get update -qq
            sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
            ;;
        fedora)
            info "Running: dnf install tesseract tesseract-langpack-eng"
            sudo dnf install -y tesseract tesseract-langpack-eng
            ;;
        arch)
            info "Running: pacman -S tesseract tesseract-data-eng"
            sudo pacman -Sy --noconfirm tesseract tesseract-data-eng
            ;;
        *)
            error "Unsupported OS (Linux only). Please install Tesseract manually:\n  https://tesseract-ocr.github.io/tessdoc/Installation.html"
            ;;
    esac

    success "Tesseract installed: $(tesseract --version 2>&1 | head -1)"
}

# ── 2. Install tessdata_fast models ───────────────────────────────────────────
install_tessdata_fast() {
    step "Installing tessdata_fast models (tess_fast)"

    # Find tessdata directory (Linux)
    TESSDATA_DIR=""
    for dir in /usr/share/tesseract-ocr/5/tessdata \
               /usr/share/tesseract-ocr/4.00/tessdata \
               /usr/share/tessdata \
               /usr/local/share/tessdata; do
        if [[ -d "$dir" ]]; then
            TESSDATA_DIR="$dir"
            break
        fi
    done

    if [[ -z "$TESSDATA_DIR" ]]; then
        warn "Could not auto-detect tessdata directory."
        read -rp "Enter your tessdata path manually: " TESSDATA_DIR
    fi

    info "tessdata directory: $TESSDATA_DIR"

    FAST_URL="https://github.com/tesseract-ocr/tessdata_fast/raw/main"
    FAST_MODEL="eng.traineddata"
    FAST_DEST="$TESSDATA_DIR/eng_fast.traineddata"

    if [[ -f "$FAST_DEST" ]]; then
        success "tessdata_fast model already present: $FAST_DEST"
    else
        info "Downloading eng_fast.traineddata from tessdata_fast …"
        if command -v curl &>/dev/null; then
            sudo curl -L --progress-bar \
                "$FAST_URL/$FAST_MODEL" \
                -o "$FAST_DEST"
        elif command -v wget &>/dev/null; then
            sudo wget -q --show-progress \
                "$FAST_URL/$FAST_MODEL" \
                -O "$FAST_DEST"
        else
            error "Neither curl nor wget found. Install one and re-run."
        fi
        success "Saved to $FAST_DEST"
    fi

    # Export TESSDATA_PREFIX so the project can find it
    export TESSDATA_PREFIX="$TESSDATA_DIR"
    info "TESSDATA_PREFIX=$TESSDATA_PREFIX"

    # Persist to shell rc files
    SHELL_RC=""
    case "$SHELL" in
        */zsh)  SHELL_RC="$HOME/.zshrc" ;;
        */bash) SHELL_RC="$HOME/.bashrc" ;;
        *)      SHELL_RC="$HOME/.profile" ;;
    esac

    EXPORT_LINE="export TESSDATA_PREFIX=\"$TESSDATA_DIR\""
    if ! grep -qF "TESSDATA_PREFIX" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# Added by i-grep setup" >> "$SHELL_RC"
        echo "$EXPORT_LINE" >> "$SHELL_RC"
        success "Added TESSDATA_PREFIX to $SHELL_RC"
    else
        success "TESSDATA_PREFIX already set in $SHELL_RC"
    fi
}

# ── 3. Install uv (Python package manager) ────────────────────────────────────
install_uv() {
    step "Checking for uv"

    if command -v uv &>/dev/null; then
        success "uv already installed: $(uv --version)"
        return 0
    fi

    info "Installing uv …"
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Source uv into current shell
    export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

    if command -v uv &>/dev/null; then
        success "uv installed: $(uv --version)"
    else
        error "uv installation failed. Try manually: https://docs.astral.sh/uv/"
    fi
}

# ── 4. Install igrep package ─────────────────────────────────────────────────
install_igrep() {
    step "Installing igrep and dependencies"

    if [[ ! -f pyproject.toml ]]; then
        error "pyproject.toml not found. Ensure you are running from the i-grep repo root."
    fi

    uv pip install -e .
    success "igrep installed"
}

# ── 5. Run igrep setup (model + db) ──────────────────────────────────────────
run_igrep_setup() {
    step "Running igrep setup (ONNX model ~90 MB + database)"
    igrep setup
    success "igrep setup complete"
}

# ── Summary ───────────────────────────────────────────────────────────────────
print_summary() {
    echo ""
    echo -e "${GREEN}${BOLD}══════════════════════════════════════════${RESET}"
    echo -e "${GREEN}${BOLD} i-grep is ready to use!${RESET}"
    echo -e "${GREEN}${BOLD}══════════════════════════════════════════${RESET}"
    echo ""
    echo -e "  ${BOLD}Tesseract (accurate):${RESET}  default mode"
    echo -e "  ${BOLD}Tesseract fast:${RESET}        uses eng_fast.traineddata"
    echo ""
    echo -e "  ${BOLD}Quick commands:${RESET}"
    echo '    igrep sync                  # index your images'
    echo '    igrep "pattern"             # pattern search (Tesseract accurate)'
    echo '    igrep -i "pattern"          # case-insensitive'
    echo '    igrep -c "pattern"          # count occurrences'
    echo '    igrep -s "text"             # semantic search (top 5)'
    echo '    igrep -s "text" 10          # semantic search (top 10)'
    echo ""
    echo -e "  ${YELLOW}If TESSDATA_PREFIX was just added to your shell rc,${RESET}"
    echo -e "  ${YELLOW}run: source ~/${SHELL_RC##*/}${RESET}"
    echo ""
}

# ── Main ──────────────────────────────────────────────────────────────────────
main() {
    echo -e "${BOLD}"
    echo "  ██╗ ██████╗ ██████╗ ███████╗██████╗ "
    echo "  ██║██╔════╝ ██╔══██╗██╔════╝██╔══██╗"
    echo "  ██║██║  ███╗██████╔╝█████╗  ██████╔╝"
    echo "  ██║██║   ██║██╔══██╗██╔══╝  ██╔═══╝ "
    echo "  ██║╚██████╔╝██║  ██║███████╗██║     "
    echo "  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝     "
    echo -e "  i-grep setup script${RESET}"
    echo ""

    install_tesseract
    install_tessdata_fast
    install_uv
    install_igrep
    run_igrep_setup
    print_summary
}

main "$@"