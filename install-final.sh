#!/bin/bash
# 🏦 PILONS FINANCE HUB - Installation FINALE Termux
# Une seule commande pour tout installer et lancer

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🏦 PILONS FINANCE HUB - Installation FINALE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

INSTALL_DIR="$HOME/.pilons-finance"
REPO="https://raw.githubusercontent.com/sdoukoure12/pilons-auto-scanner/main"

# 1. Créer répertoire
echo "📁 Création répertoire..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# 2. Créer venv
echo "🐍 Virtual environment..."
if [ ! -d venv ]; then
    python -m venv venv
fi
source venv/bin/activate

# 3. Installer pip
echo "📦 pip upgrade..."
pip install --upgrade pip wheel setuptools 2>/dev/null || true

# 4. Installer dépendances
echo "📚 Packages Python..."
pip install \
    python-dotenv \
    PyPDF2 \
    Pillow \
    python-docx \
    flask \
    flask-cors \
    requests \
    2>/dev/null || echo "⚠️ Certains packages non disponibles"

# 5. Télécharger le code principal
echo "⬇️  Téléchargement du code..."
if command -v curl &> /dev/null; then
    curl -sL "$REPO/pilons_finance_hub.py" -o pilons_finance_hub.py
elif command -v wget &> /dev/null; then
    wget -q "$REPO/pilons_finance_hub.py" -O pilons_finance_hub.py
else
    echo "❌ curl ou wget requis"
    exit 1
fi

if [ ! -f pilons_finance_hub.py ]; then
    echo "❌ Téléchargement échoué"
    exit 1
fi

# 6. Créer le wrapper
echo "🔧 Création du launcher..."
cat > pilons <<'WRAPPER'
#!/bin/bash
source "$HOME/.pilons-finance/venv/bin/activate"
cd "$HOME/.pilons-finance"
python pilons_finance_hub.py "$@"
WRAPPER

chmod +x pilons

# 7. Configurer le PATH
echo "🔗 Configuration PATH..."
SHELL_RC="$HOME/.bashrc"
if [ ! -f "$SHELL_RC" ]; then
    touch "$SHELL_RC"
fi

if ! grep -q "pilons-finance" "$SHELL_RC" 2>/dev/null; then
    cat >> "$SHELL_RC" <<'PATH_CONFIG'

# 🏦 Pilons Finance Hub
export PATH="$HOME/.pilons-finance:$PATH"
alias pilons='$HOME/.pilons-finance/pilons'
PATH_CONFIG
fi

# 8. Créer répertoires
mkdir -p data logs documents uploads cache

# 9. Créer config
cat > .env <<'ENVFILE'
STORAGE_PATH=$HOME/.pilons-finance/data
LOG_LEVEL=INFO
API_PORT=5000
TERMUX_MODE=true
ENVFILE

# 10. Recharger shell
export PATH="$HOME/.pilons-finance:$PATH"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✨ Installation Terminée avec Succès !"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 PROCHAINES ÉTAPES:"
echo ""
echo "1️⃣  Recharger le shell (IMPORTANT):"
echo "   exec bash"
echo ""
echo "2️⃣  Vérifier l'installation:"
echo "   which pilons"
echo "   pilons --help"
echo ""
echo "3️⃣  EXEMPLES D'UTILISATION:"
echo ""
echo "   📄 Scanner un dossier:"
echo "   pilons scan-folder /storage/documents/"
echo ""
echo "   💰 Identifier revenus:"
echo "   pilons identify-income /storage/documents/facture.pdf"
echo ""
echo "   💳 Portefeuille:"
echo "   pilons wallet balance"
echo "   pilons wallet deposit --amount 1000 --currency USD"
echo "   pilons wallet withdraw --amount 500 --currency USD"
echo "   pilons wallet convert --amount 100 --from USD --to EUR"
echo ""
echo "   🌐 API REST:"
echo "   pilons api start --port 5000"
echo ""
echo "   📄 Scanner un fichier:"
echo "   pilons scan /storage/documents/file.pdf"
echo ""
echo "📂 Dossier: $INSTALL_DIR"
echo "⚙️  Config: $INSTALL_DIR/.env"
echo "📖 Docs: https://github.com/sdoukoure12/pilons-auto-scanner"
echo ""
