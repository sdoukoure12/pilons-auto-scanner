#!/bin/bash
# 🏦 PILONS FINANCE HUB - Corrections et installation automatique
# Ce script corrige le problème de commande "pilons" et active le lancement

set -e

INSTALL_DIR="$HOME/.pilons-finance"
SHELL_RC="$HOME/.bashrc"

if [ ! -f "$SHELL_RC" ]; then
    SHELL_RC="$HOME/.profile"
fi

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Créer le wrapper exécutable si absent
cat > "$INSTALL_DIR/pilons" <<'EOF'
#!/bin/bash
# 🔧 Lancement Pilons Finance Hub
source "$HOME/.pilons-finance/venv/bin/activate"
cd "$HOME/.pilons-finance"
python pilons_finance_hub.py "$@"
EOF
chmod +x "$INSTALL_DIR/pilons"

# Ajouter le PATH permanent
if ! grep -q "\.pilons-finance" "$SHELL_RC" 2>/dev/null; then
    cat >> "$SHELL_RC" <<'EOF'

# Pilons Finance Hub
export PATH="$HOME/.pilons-finance:$PATH"
EOF
fi

# Vérifier si Python et venv existent
if [ -f "$INSTALL_DIR/venv/bin/activate" ]; then
    source "$INSTALL_DIR/venv/bin/activate"
    python -V
else
    echo "❌ Environnement virtuel introuvable. Relancez bash install.sh"
    exit 1
fi

# Vérifier le fichier principal
if [ ! -f "$INSTALL_DIR/pilons_finance_hub.py" ]; then
    echo "❌ Fichier principal introuvable: pilons_finance_hub.py"
    exit 1
fi

# Vérifier la commande
export PATH="$HOME/.pilons-finance:$PATH"
source "$SHELL_RC" 2>/dev/null || true

which pilons || echo "⚠️ Commande pilons non détectée après PATH; relancez le terminal"

printf "\n✅ Wrapper installé. Test :\n"
printf "   pilons --help\n\n"
