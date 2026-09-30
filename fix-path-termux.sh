#!/bin/bash
# 🏦 PILONS FINANCE HUB - Installation Termux FINALE
# Correction complète du PATH et lancement

set -e

INSTALL_DIR="$HOME/.pilons-finance"
cd "$INSTALL_DIR"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔧 Correction du PATH Termux"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Créer le wrapper exécutable
echo "📝 Création du wrapper..."
cat > "$INSTALL_DIR/pilons" <<'WRAPPER'
#!/bin/bash
source "$HOME/.pilons-finance/venv/bin/activate"
cd "$HOME/.pilons-finance"
python pilons_finance_hub.py "$@"
WRAPPER

chmod +x "$INSTALL_DIR/pilons"
echo "✅ Wrapper créé: $INSTALL_DIR/pilons"

# Trouver le bon fichier RC
echo "🔍 Recherche du fichier shell..."
SHELL_RC=""
for rc in "$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.profile"; do
    if [ -f "$rc" ]; then
        SHELL_RC="$rc"
        break
    fi
done

# Si aucun n'existe, en créer un
if [ -z "$SHELL_RC" ]; then
    SHELL_RC="$HOME/.bashrc"
    touch "$SHELL_RC"
    echo "📄 Création: $SHELL_RC"
fi

echo "📌 Fichier: $SHELL_RC"

# Ajouter le PATH
if ! grep -q "pilons-finance" "$SHELL_RC" 2>/dev/null; then
    cat >> "$SHELL_RC" <<'PATH_EXPORT'

# 🏦 Pilons Finance Hub
export PATH="$HOME/.pilons-finance:$PATH"
PATH_EXPORT
    echo "✅ PATH ajouté"
else
    echo "✓ PATH déjà configuré"
fi

# Créer un alias direct
if ! grep -q "alias pilons=" "$SHELL_RC" 2>/dev/null; then
    cat >> "$SHELL_RC" <<'ALIAS_EXPORT'

# Alias Pilons
alias pilons='$HOME/.pilons-finance/pilons'
ALIAS_EXPORT
    echo "✅ Alias créé"
fi

# Charger la configuration
export PATH="$HOME/.pilons-finance:$PATH"
source "$SHELL_RC"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✨ Configuration Complète !"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Prochaines étapes:"
echo ""
echo "1️⃣  Recharger le shell:"
echo "   exec bash"
echo ""
echo "2️⃣  Vérifier l'installation:"
echo "   pilons --help"
echo ""
echo "3️⃣  Scanner un dossier:"
echo "   pilons scan-folder /storage/documents/"
echo ""
echo "4️⃣  Identifier les revenus:"
echo "   pilons identify-income /storage/documents/facture.pdf"
echo ""
echo "5️⃣  Voir le portefeuille:"
echo "   pilons wallet balance"
echo ""
echo "📂 Dossier: $INSTALL_DIR"
echo ""
