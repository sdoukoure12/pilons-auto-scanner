#!/bin/bash
# 🏦 PILONS FINANCE HUB - Installation Termux
# Une seule commande pour tout installer

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🏦 PILONS FINANCE HUB - Installation Termux"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Vérifier Termux
if [ ! -d "$PREFIX" ]; then
    echo "❌ Termux non détecté."
    exit 1
fi

INSTALL_DIR="$HOME/.pilons-finance"

# 1. Mise à jour
echo "📦 Mise à jour système..."
pkg update -y && pkg upgrade -y 2>/dev/null || true

# 2. Installer dépendances
echo "🔧 Installation dépendances..."
pkg install -y python python-pip git curl wget openssl libssl-dev build-essential clang make 2>/dev/null || true

# 3. Créer répertoire
echo "📁 Création: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# 4. Virtual Environment
echo "🐍 Création venv..."
python -m venv venv
source venv/bin/activate

# 5. Installer packages Python
echo "📚 Installation packages Python..."
pip install --upgrade pip wheel setuptools 2>/dev/null || true
pip install \
    PyPDF2 \
    Pillow \
    pytesseract \
    python-docx \
    flask \
    flask-cors \
    requests \
    python-dotenv \
    cryptography \
    web3 \
    2>/dev/null || echo "⚠️ Certains packages non disponibles (normal en Termux)"

# 6. Créer répertoires
echo "📂 Création répertoires..."
mkdir -p data logs documents uploads

# 7. Créer fichier .env
echo "⚙️ Configuration..."
cat > .env << 'ENVFILE'
STORAGE_PATH=$HOME/.pilons-finance/data
LOG_LEVEL=INFO
API_PORT=5000
API_SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_key
OPENAI_API_KEY=your_api_key_here
TERMUX_MODE=true
ENVFILE

# 8. Créer alias
echo "🔗 Configuration alias..."
SHELL_RC="$HOME/.bashrc"
if [ ! -f "$SHELL_RC" ]; then
    SHELL_RC="$HOME/.profile"
fi

if ! grep -q "pilons-finance" "$SHELL_RC" 2>/dev/null; then
    cat >> "$SHELL_RC" << 'ALIAS'

# 🏦 Pilons Finance Hub
export PATH="$HOME/.pilons-finance:$PATH"
alias pilons='cd $HOME/.pilons-finance && source venv/bin/activate && python pilons_finance_hub.py'
ALIAS
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✨ Installation Terminée !"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Commandes disponibles:"
echo ""
echo "  1. Scanner un dossier:"
echo "     pilons scan-folder /storage/documents/"
echo ""
echo "  2. Identifier revenus:"
echo "     pilons identify-income document.pdf"
echo ""
echo "  3. Portefeuille:"
echo "     pilons wallet balance"
echo "     pilons wallet deposit --amount 1000 --currency USD"
echo ""
echo "  4. API REST:"
echo "     pilons api start --port 5000"
echo ""
echo "🔧 Éditer config:"
echo "   nano $INSTALL_DIR/.env"
echo ""
echo "📂 Dossier installation:"
echo "   $INSTALL_DIR"
echo ""
