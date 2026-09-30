#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏦 PILONS FINANCE HUB - Version Complète Termux
Scanner Documents + Portefeuille Crypto/Fiat + API REST
Installation: bash install.sh
Utilisation: pilons-finance scan-folder /chemin/ | pilons-finance identify-income file.pdf
"""

import os
import sys
import json
import re
import sqlite3
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# ============================================================================
# 1️⃣ CONFIGURATION & LOGGING
# ============================================================================

load_dotenv()
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PilonsFinance')

# ============================================================================
# 2️⃣ SCANNER DE DOCUMENTS
# ============================================================================

class DocumentScanner:
    """Scanner documents PDF, images, Word"""
    
    SUPPORTED_FORMATS = {'.pdf', '.jpg', '.jpeg', '.png', '.docx'}
    
    def __init__(self):
        self.storage_path = Path(os.getenv('STORAGE_PATH', './data'))
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def scan(self, file_path: str) -> Dict[str, Any]:
        """Scanner un fichier"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {'status': 'error', 'error': f'Fichier non trouvé: {file_path}'}
        
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return {'status': 'error', 'error': f'Format non supporté: {file_path.suffix}'}
        
        logger.info(f"Scanning: {file_path}")
        
        try:
            if file_path.suffix.lower() == '.pdf':
                return self._scan_pdf(file_path)
            elif file_path.suffix.lower() in {'.jpg', '.jpeg', '.png'}:
                return self._scan_image(file_path)
            elif file_path.suffix.lower() == '.docx':
                return self._scan_docx(file_path)
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _scan_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Scanner PDF"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()
            return {
                'filename': file_path.name,
                'type': 'pdf',
                'text': text,
                'pages': len(reader.pages),
                'status': 'success'
            }
        except ImportError:
            return {'status': 'error', 'error': 'PyPDF2 non installé'}
    
    def _scan_image(self, file_path: Path) -> Dict[str, Any]:
        """Scanner image avec OCR"""
        try:
            from PIL import Image
            import pytesseract
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return {
                'filename': file_path.name,
                'type': 'image',
                'text': text,
                'size': f"{image.width}x{image.height}",
                'status': 'success'
            }
        except ImportError:
            return {'status': 'error', 'error': 'PIL/pytesseract non installé'}
    
    def _scan_docx(self, file_path: Path) -> Dict[str, Any]:
        """Scanner Word"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return {
                'filename': file_path.name,
                'type': 'docx',
                'text': text,
                'paragraphs': len(doc.paragraphs),
                'status': 'success'
            }
        except ImportError:
            return {'status': 'error', 'error': 'python-docx non installé'}

# ============================================================================
# 3️⃣ EXTRACTOR - Extraction de données financières
# ============================================================================

class DataExtractor:
    """Extraction intelligente de revenus, factures, contacts"""
    
    INCOME_PATTERNS = {
        'salary': r'(salary|salaire|rémunération|compensation)[\s:]*[\$€£]?\s*([\d,]+(?:\.\d{2})?)',
        'bonus': r'(bonus|prime)[\s:]*[\$€£]?\s*([\d,]+(?:\.\d{2})?)',
        'income': r'(income|revenu|earnings)[\s:]*[\$€£]?\s*([\d,]+(?:\.\d{2})?)',
        'fee': r'(fee|honoraire|frais)[\s:]*[\$€£]?\s*([\d,]+(?:\.\d{2})?)',
    }
    
    def extract_income(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extraire les revenus"""
        text = document_data.get('text', '').lower()
        
        results = {
            'amount': None,
            'date': None,
            'source': None,
            'type': None,
            'confidence': 0.0,
            'raw_matches': []
        }
        
        # Chercher montants
        for income_type, pattern in self.INCOME_PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount = float(match.group(2).replace(',', ''))
                    if amount > 0:
                        results['raw_matches'].append({
                            'type': income_type,
                            'amount': amount,
                            'text': match.group(0)
                        })
                except:
                    pass
        
        if results['raw_matches']:
            results['raw_matches'].sort(key=lambda x: x['amount'], reverse=True)
            top = results['raw_matches'][0]
            results['amount'] = top['amount']
            results['type'] = top['type']
            results['confidence'] = 0.85
        
        results['date'] = self._extract_date(text)
        results['source'] = self._extract_source(text)
        
        return results
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extraire date"""
        patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None
    
    def _extract_source(self, text: str) -> Optional[str]:
        """Extraire source (employeur)"""
        patterns = [
            r'from\s+([A-Za-z\s&\.]+)',
            r'company[\s:]+([A-Za-z\s&\.]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

# ============================================================================
# 4️⃣ WALLET MANAGER - Portefeuille Crypto/Fiat
# ============================================================================

class WalletManager:
    """Gestion portefeuilles crypto et fiat"""
    
    def __init__(self):
        self.storage_path = Path(os.getenv('STORAGE_PATH', './data'))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.storage_path / 'finance.db'
        self._init_db()
    
    def _init_db(self):
        """Initialiser BD"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS wallets (
            id TEXT PRIMARY KEY,
            network TEXT,
            address TEXT,
            balance REAL,
            currency TEXT,
            created_at TIMESTAMP
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            wallet_id TEXT,
            type TEXT,
            amount REAL,
            currency TEXT,
            timestamp TIMESTAMP,
            status TEXT
        )''')
        
        conn.commit()
        conn.close()
    
    def create(self, network: str) -> Dict[str, Any]:
        """Créer portefeuille"""
        import uuid
        
        wallet_id = str(uuid.uuid4())
        address = f"{network}_{uuid.uuid4()}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO wallets (id, network, address, balance, currency, created_at)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (wallet_id, network, address, 0.0, 'USD', datetime.now()))
        conn.commit()
        conn.close()
        
        logger.info(f"Wallet created: {address}")
        return {'id': wallet_id, 'network': network, 'address': address, 'status': 'success'}
    
    def balance(self) -> Dict[str, float]:
        """Obtenir soldes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT currency, SUM(balance) FROM wallets GROUP BY currency')
        results = cursor.fetchall()
        conn.close()
        return {row[0]: row[1] for row in results}
    
    def deposit(self, amount: float, currency: str) -> Dict[str, Any]:
        """Ajouter fonds"""
        import uuid
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE wallets SET balance = balance + ? WHERE currency = ?', 
                      (amount, currency))
        
        tx_id = str(uuid.uuid4())
        cursor.execute('''INSERT INTO transactions (id, type, amount, currency, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (tx_id, 'deposit', amount, currency, datetime.now(), 'completed'))
        
        conn.commit()
        conn.close()
        
        return {'tx_id': tx_id, 'amount': amount, 'currency': currency, 'status': 'success'}
    
    def withdraw(self, amount: float, currency: str) -> Dict[str, Any]:
        """Retirer fonds"""
        import uuid
        
        balance = self.balance()
        if balance.get(currency, 0) < amount:
            return {'status': 'error', 'error': 'Solde insuffisant'}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE wallets SET balance = balance - ? WHERE currency = ?',
                      (amount, currency))
        
        tx_id = str(uuid.uuid4())
        cursor.execute('''INSERT INTO transactions (id, type, amount, currency, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (tx_id, 'withdraw', amount, currency, datetime.now(), 'completed'))
        
        conn.commit()
        conn.close()
        
        return {'tx_id': tx_id, 'amount': amount, 'currency': currency, 'status': 'success'}
    
    def convert(self, amount: float, from_cur: str, to_cur: str) -> Dict[str, Any]:
        """Convertir devises"""
        rates = {'USD': 1.0, 'EUR': 0.92, 'GBP': 0.79, 'BTC': 0.000025, 'ETH': 0.0005}
        
        if from_cur not in rates or to_cur not in rates:
            return {'status': 'error', 'error': 'Devise non supportée'}
        
        converted = (amount * rates[from_cur]) / rates[to_cur]
        
        return {
            'amount': amount,
            'from': from_cur,
            'to': to_cur,
            'converted': round(converted, 8),
            'rate': round(converted / amount, 8)
        }

# ============================================================================
# 5️⃣ API REST SERVER
# ============================================================================

class APIServer:
    """Serveur API REST Flask"""
    
    def __init__(self):
        try:
            from flask import Flask, jsonify, request
            from flask_cors import CORS
            
            self.flask = Flask
            self.jsonify = jsonify
            self.request = request
            self.CORS = CORS
            self.app_instance = None
        except ImportError:
            logger.warning("Flask non installé. API non disponible.")
    
    def start(self, port: int = 5000):
        """Démarrer API"""
        if not hasattr(self, 'flask'):
            print("❌ Flask non installé. Installez: pip install flask flask-cors")
            return
        
        app = self.flask(__name__)
        self.CORS(app)
        
        scanner = DocumentScanner()
        wallet = WalletManager()
        extractor = DataExtractor()
        
        @app.route('/health', methods=['GET'])
        def health():
            return self.jsonify({'status': 'ok'}), 200
        
        @app.route('/api/wallet/balance', methods=['GET'])
        def api_balance():
            return self.jsonify({'balance': wallet.balance()}), 200
        
        @app.route('/api/wallet/deposit', methods=['POST'])
        def api_deposit():
            data = self.request.get_json()
            result = wallet.deposit(data.get('amount'), data.get('currency', 'USD'))
            return self.jsonify(result), 200
        
        @app.route('/api/documents/extract', methods=['POST'])
        def api_extract():
            data = self.request.get_json()
            income = extractor.extract_income(data)
            return self.jsonify(income), 200
        
        print(f"🌐 API démarrée sur http://0.0.0.0:{port}")
        print(f"📖 Endpoints: /health, /api/wallet/balance, /api/wallet/deposit, /api/documents/extract")
        app.run(host='0.0.0.0', port=port, debug=False)

# ============================================================================
# 6️⃣ CLI - Interface en ligne de commande
# ============================================================================

class PilonsFinanceCLI:
    """Interface CLI complète"""
    
    def __init__(self):
        self.scanner = DocumentScanner()
        self.wallet = WalletManager()
        self.extractor = DataExtractor()
        self.api = APIServer()
    
    def scan_folder(self, folder_path: str):
        """Scanner un dossier"""
        print(f"📁 Scanning: {folder_path}")
        
        folder = Path(folder_path)
        if not folder.exists():
            print(f"❌ Dossier non trouvé: {folder_path}")
            return
        
        results = []
        for file_path in folder.glob('**/*'):
            if file_path.suffix.lower() in DocumentScanner.SUPPORTED_FORMATS:
                print(f"  📄 {file_path.name}... ", end='', flush=True)
                result = self.scanner.scan(str(file_path))
                if result['status'] == 'success':
                    print("✅")
                    results.append(result)
                else:
                    print("❌")
        
        print(f"\n✅ {len(results)} fichiers scannés")
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    def identify_income(self, file_path: str):
        """Identifier revenus"""
        print(f"💰 Identification revenus: {file_path}\n")
        
        result = self.scanner.scan(file_path)
        if result['status'] != 'success':
            print(f"❌ {result['error']}")
            return
        
        income = self.extractor.extract_income(result)
        
        print("📊 RÉSULTATS:")
        print(f"  💵 Montant: {income['amount'] or 'Non détecté'}")
        print(f"  📅 Date: {income['date'] or 'Non détectée'}")
        print(f"  🏢 Source: {income['source'] or 'Non détectée'}")
        print(f"  📝 Type: {income['type'] or 'Non détecté'}")
        print(f"  🎯 Confiance: {income['confidence']*100:.0f}%")
        print(f"\n📋 Données brutes: {json.dumps(income, indent=2, ensure_ascii=False)}")
    
    def wallet_command(self, action: str, **kwargs):
        """Commandes portefeuille"""
        if action == 'balance':
            balance = self.wallet.balance()
            print("📊 Soldes:")
            for currency, amount in balance.items():
                print(f"  {currency}: {amount:.2f}")
        
        elif action == 'deposit':
            result = self.wallet.deposit(kwargs.get('amount', 0), kwargs.get('currency', 'USD'))
            if result['status'] == 'success':
                print(f"✅ Dépôt: {result['amount']} {result['currency']}")
            else:
                print(f"❌ {result.get('error')}")
        
        elif action == 'withdraw':
            result = self.wallet.withdraw(kwargs.get('amount', 0), kwargs.get('currency', 'USD'))
            if result['status'] == 'success':
                print(f"✅ Retrait: {result['amount']} {result['currency']}")
            else:
                print(f"❌ {result.get('error')}")
        
        elif action == 'convert':
            result = self.wallet.convert(
                kwargs.get('amount', 0),
                kwargs.get('from', 'USD'),
                kwargs.get('to', 'EUR')
            )
            if result.get('status') != 'error':
                print(f"🔄 {result['amount']} {result['from']} = {result['converted']} {result['to']}")
            else:
                print(f"❌ {result.get('error')}")
        
        elif action == 'create':
            result = self.wallet.create(kwargs.get('network', 'ethereum'))
            print(f"✅ Portefeuille créé: {result['address']}")

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description='🏦 PILONS FINANCE HUB - Gestionnaire Financier Personnel',
        epilog='Exemples: pilons-finance scan-folder /storage/ | pilons-finance identify-income file.pdf'
    )
    
    subparsers = parser.add_subparsers(dest='cmd', help='Commandes')
    
    # scan-folder
    sp = subparsers.add_parser('scan-folder', help='Scanner un dossier')
    sp.add_argument('folder', help='Chemin du dossier')
    
    # identify-income
    sp = subparsers.add_parser('identify-income', help='Identifier revenus')
    sp.add_argument('file', help='Fichier à analyser')
    
    # scan
    sp = subparsers.add_parser('scan', help='Scanner un fichier')
    sp.add_argument('file', help='Fichier')
    
    # wallet
    sp = subparsers.add_parser('wallet', help='Portefeuille')
    sp.add_argument('action', choices=['balance', 'deposit', 'withdraw', 'convert', 'create'])
    sp.add_argument('--amount', type=float, help='Montant')
    sp.add_argument('--currency', default='USD', help='Devise')
    sp.add_argument('--from', dest='from_cur', help='De')
    sp.add_argument('--to', dest='to_cur', help='Vers')
    sp.add_argument('--network', default='ethereum', help='Réseau')
    
    # api
    sp = subparsers.add_parser('api', help='API REST')
    sp.add_argument('action', choices=['start'], help='Action')
    sp.add_argument('--port', type=int, default=5000, help='Port')
    
    args = parser.parse_args()
    cli = PilonsFinanceCLI()
    
    try:
        if args.cmd == 'scan-folder':
            cli.scan_folder(args.folder)
        elif args.cmd == 'identify-income':
            cli.identify_income(args.file)
        elif args.cmd == 'scan':
            result = cli.scanner.scan(args.file)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.cmd == 'wallet':
            cli.wallet_command(args.action, amount=args.amount, currency=args.currency,
                             from_cur=args.from_cur, to_cur=args.to_cur, network=args.network)
        elif args.cmd == 'api':
            cli.api.start(args.port)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\n⚠️  Annulé")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
