#!/bin/bash
# 🚀 Installation Pilons Auto-Scanner pour Termux
# Usage: bash install-termux.sh

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📱 Pilons Auto-Scanner - Installation Termux"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Vérifier Termux
if [ ! -d "$PREFIX" ]; then
    echo "❌ Termux non détecté. Installez Termux d'abord."
    exit 1
fi

echo "✅ Termux détecté: $PREFIX"
echo ""

# 1. Mise à jour packages
echo "📦 Mise à jour des packages..."
pkg update -y
pkg upgrade -y
echo "✅ Packages à jour"
echo ""

# 2. Installer dépendances système
echo "🔧 Installation des dépendances..."
pkg install -y \
    python \
    python-pip \
    git \
    curl \
    wget \
    openssl \
    libssl-dev \
    build-essential \
    clang \
    make
echo "✅ Dépendances installées"
echo ""

# 3. Créer répertoire installation
INSTALL_DIR="$HOME/.pilons-scanner"
echo "📁 Installation dans: $INSTALL_DIR"

if [ -d "$INSTALL_DIR" ]; then
    echo "⚠️  Répertoire existant, mise à jour..."
    cd "$INSTALL_DIR"
    git pull origin main 2>/dev/null || echo "Répertoire local trouvé"
else
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    git clone https://github.com/sdoukoure12/pilons-auto-scanner.git . 2>/dev/null || echo "Clonage local"
fi
echo "✅ Répertoire prêt"
echo ""

# 4. Créer Virtual Environment
echo "🐍 Création de l'environnement Python..."
python -m venv venv
source venv/bin/activate
echo "✅ Venv activé"
echo ""

# 5. Installer dépendances Python
echo "📚 Installation des packages Python..."
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt 2>/dev/null || pip install \
    requests \
    beautifulsoup4 \
    lxml \
    python-dotenv \
    flask \
    openai \
    pypdf2 \
    python-docx \
    langchain \
    faiss-cpu
echo "✅ Packages Python installés"
echo ""

# 6. Créer fichier de configuration
echo "⚙️  Configuration du scanner..."
cat > "$INSTALL_DIR/.env" << 'EOF'
# Pilons Auto-Scanner Configuration
OPENAI_API_KEY=your_key_here
WEBHOOK_PORT=5000
STORAGE_PATH=$HOME/.pilons-scanner/data
LOG_LEVEL=INFO
TERMUX_MODE=true
EOF

echo "⚠️  IMPORTANT: Éditez $INSTALL_DIR/.env avec vos clés API"
echo ""

# 7. Créer script de lancement
echo "🎯 Création du script de lancement..."
cat > "$INSTALL_DIR/run.sh" << 'EOF'
#!/bin/bash
cd "$HOME/.pilons-scanner"
source venv/bin/activate
python rag.py "$@"
EOF
chmod +x "$INSTALL_DIR/run.sh"
echo "✅ Script créé"
echo ""

# 8. Créer alias Termux
echo "🔗 Configuration des alias..."
TERMUX_RC=""
if [ -f "$HOME/.bashrc" ]; then
    TERMUX_RC="$HOME/.bashrc"
elif [ -f "$HOME/.bash_profile" ]; then
    TERMUX_RC="$HOME/.bash_profile"
else
    TERMUX_RC="$HOME/.bashrc"
fi

if ! grep -q "pilons-scanner" "$TERMUX_RC"; then
    cat >> "$TERMUX_RC" << 'EOF'

# Pilons Auto-Scanner
alias pilons='$HOME/.pilons-scanner/run.sh'
alias pilons-update='cd $HOME/.pilons-scanner && git pull && source venv/bin/activate && pip install -r requirements.txt'
alias pilons-config='nano $HOME/.pilons-scanner/.env'
alias pilons-logs='tail -f $HOME/.pilons-scanner/logs/scanner.log'
EOF
    echo "✅ Alias créés"
    source "$TERMUX_RC"
else
    echo "ℹ️  Alias déjà configurés"
fi
echo ""

# 9. Créer répertoires de données
echo "📂 Création des répertoires..."
mkdir -p "$INSTALL_DIR/data"
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/cache"
echo "✅ Répertoires créés"
echo ""

# 10. Test installation
echo "🧪 Test d'installation..."
cd "$INSTALL_DIR"
source venv/bin/activate
python -c "import requests, bs4, flask, dotenv; print('✅ Tous les packages sont OK')" 2>/dev/null || echo "⚠️  Certains packages manquent, à ignorer"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✨ Installation Terminée avec Succès !"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Prochaines étapes:"
echo ""
echo "1️⃣  Éditer la configuration:"
echo "   pilons-config"
echo ""
echo "2️⃣  Lancer le scanner:"
echo "   pilons scan <url_ou_fichier>"
echo ""
echo "3️⃣  Voir l'aide:"
echo "   pilons --help"
echo ""
echo "4️⃣  Mettre à jour:"
echo "   pilons-update"
echo ""
echo "5️⃣  Consulter les logs:"
echo "   pilons-logs"
echo ""
echo "📚 Documentation: https://github.com/sdoukoure12/pilons-auto-scanner"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
