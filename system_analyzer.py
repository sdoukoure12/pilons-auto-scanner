#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 PILONS SYSTEM ANALYZER - Analyseur de système multi-téléphone
Suit tous les changements, configurations, et données sensibles
Synchronisation cloud automatique
"""

import os
import sys
import json
import sqlite3
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SystemAnalyzer')

# ============================================================================
# 1️⃣ SYSTÈME DE SUIVI MULTI-TÉLÉPHONE
# ============================================================================

class DeviceManager:
    """Gestion multi-appareils avec identifiant unique"""
    
    def __init__(self):
        self.storage_path = Path(os.getenv('STORAGE_PATH', './data'))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.storage_path / 'devices.db'
        self._init_db()
    
    def _init_db(self):
        """Initialiser la BD des appareils"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY,
            device_id TEXT UNIQUE,
            device_name TEXT,
            os_type TEXT,
            os_version TEXT,
            model TEXT,
            imei TEXT,
            android_id TEXT,
            device_hash TEXT,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP,
            is_active BOOLEAN,
            location TEXT,
            metadata TEXT
        )''')
        
        conn.commit()
        conn.close()
    
    def get_device_id(self) -> str:
        """Obtenir ou créer l'ID unique du téléphone"""
        import uuid
        
        device_info_path = self.storage_path / '.device_id'
        
        if device_info_path.exists():
            with open(device_info_path, 'r') as f:
                return f.read().strip()
        
        device_id = str(uuid.uuid4())
        with open(device_info_path, 'w') as f:
            f.write(device_id)
        
        return device_id
    
    def register_device(self, device_name: str, os_type: str = 'Android', 
                       os_version: str = '', model: str = '') -> Dict[str, Any]:
        """Enregistrer le téléphone"""
        device_id = self.get_device_id()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''INSERT OR REPLACE INTO devices 
            (id, device_id, device_name, os_type, os_version, model, first_seen, last_seen, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (device_id, device_id, device_name, os_type, os_version, model, datetime.now(), datetime.now(), True))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Device registered: {device_name} ({device_id})")
        return {'device_id': device_id, 'device_name': device_name, 'status': 'registered'}
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """Lister tous les appareils"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM devices ORDER BY first_seen DESC')
        devices = []
        for row in cursor.fetchall():
            devices.append({
                'id': row[0],
                'device_id': row[1],
                'device_name': row[2],
                'os_type': row[3],
                'os_version': row[4],
                'model': row[5],
                'first_seen': row[8],
                'last_seen': row[9],
                'is_active': row[10]
            })
        
        conn.close()
        return devices

# ============================================================================
# 2️⃣ ANALYSEUR DE CHANGEMENTS SYSTÈME
# ============================================================================

class SystemChangeAnalyzer:
    """Détecte et enregistre tous les changements système"""
    
    def __init__(self):
        self.storage_path = Path(os.getenv('STORAGE_PATH', './data'))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.storage_path / 'changes.db'
        self._init_db()
    
    def _init_db(self):
        """Initialiser la BD des changements"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS system_changes (
            id TEXT PRIMARY KEY,
            device_id TEXT,
            change_type TEXT,
            category TEXT,
            description TEXT,
            before_value TEXT,
            after_value TEXT,
            severity TEXT,
            timestamp TIMESTAMP,
            metadata TEXT
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS installed_apps (
            id TEXT PRIMARY KEY,
            device_id TEXT,
            package_name TEXT,
            app_name TEXT,
            version TEXT,
            size TEXT,
            install_date TIMESTAMP,
            last_update TIMESTAMP,
            permissions TEXT,
            is_system BOOLEAN
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS file_changes (
            id TEXT PRIMARY KEY,
            device_id TEXT,
            file_path TEXT,
            file_hash TEXT,
            file_size TEXT,
            change_type TEXT,
            timestamp TIMESTAMP
        )''')
        
        conn.commit()
        conn.close()
    
    def record_change(self, device_id: str, change_type: str, category: str,
                     description: str, before_val: str = None, after_val: str = None,
                     severity: str = 'INFO') -> str:
        """Enregistrer un changement système"""
        import uuid
        
        change_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''INSERT INTO system_changes
            (id, device_id, change_type, category, description, before_value, after_value, severity, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (change_id, device_id, change_type, category, description, before_val, after_val, severity, datetime.now()))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Change recorded: {category} - {description}")
        return change_id
    
    def track_app_install(self, device_id: str, package_name: str, app_name: str,
                         version: str, size: str = '') -> str:
        """Enregistrer l'installation d'une app"""
        import uuid
        
        app_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''INSERT INTO installed_apps
            (id, device_id, package_name, app_name, version, size, install_date, is_system)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (app_id, device_id, package_name, app_name, version, size, datetime.now(), False))
        
        conn.commit()
        conn.close()
        
        # Enregistrer aussi comme changement
        self.record_change(device_id, 'app_install', 'Applications',
                          f"App installed: {app_name} ({version})",
                          severity='INFO')
        
        return app_id
    
    def track_file_change(self, device_id: str, file_path: str, change_type: str) -> str:
        """Enregistrer les changements de fichiers"""
        import uuid
        
        change_id = str(uuid.uuid4())
        
        try:
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            file_hash = self._hash_file(file_path) if os.path.exists(file_path) else ''
        except:
            file_size = 0
            file_hash = ''
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''INSERT INTO file_changes
            (id, device_id, file_path, file_hash, file_size, change_type, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (change_id, device_id, file_path, file_hash, str(file_size), change_type, datetime.now()))
        
        conn.commit()
        conn.close()
        
        return change_id
    
    def _hash_file(self, file_path: str) -> str:
        """Calculer le hash MD5 d'un fichier"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ''
    
    def get_changes(self, device_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupérer les changements d'un appareil"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''SELECT * FROM system_changes 
            WHERE device_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?''', (device_id, limit))
        
        changes = []
        for row in cursor.fetchall():
            changes.append({
                'id': row[0],
                'device_id': row[1],
                'type': row[2],
                'category': row[3],
                'description': row[4],
                'before': row[5],
                'after': row[6],
                'severity': row[7],
                'timestamp': row[8]
            })
        
        conn.close()
        return changes
    
    def get_apps(self, device_id: str) -> List[Dict[str, Any]]:
        """Lister les apps installées"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''SELECT * FROM installed_apps 
            WHERE device_id = ? 
            ORDER BY install_date DESC''', (device_id,))
        
        apps = []
        for row in cursor.fetchall():
            apps.append({
                'id': row[0],
                'package_name': row[2],
                'app_name': row[3],
                'version': row[4],
                'size': row[5],
                'install_date': row[6]
            })
        
        conn.close()
        return apps

# ============================================================================
# 3️⃣ SYNCHRONISATION CLOUD
# ============================================================================

class CloudSync:
    """Synchronisation avec serveur cloud"""
    
    def __init__(self):
        self.storage_path = Path(os.getenv('STORAGE_PATH', './data'))
        self.cloud_url = os.getenv('CLOUD_SYNC_URL', 'https://api.pilons.cloud')
        self.api_key = os.getenv('CLOUD_API_KEY', '')
    
    def sync_to_cloud(self, device_id: str, data: Dict[str, Any]) -> bool:
        """Synchroniser les données vers le cloud"""
        try:
            import requests
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'device_id': device_id,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            response = requests.post(
                f'{self.cloud_url}/sync/push',
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Cloud sync successful for device {device_id}")
                return True
            else:
                logger.warning(f"Cloud sync failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Cloud sync error: {e}")
            return False
    
    def pull_from_cloud(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer les données depuis le cloud"""
        try:
            import requests
            
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.get(
                f'{self.cloud_url}/sync/pull?device_id={device_id}',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Cloud pull successful for device {device_id}")
                return response.json()
            else:
                logger.warning(f"Cloud pull failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Cloud pull error: {e}")
            return None

# ============================================================================
# 4️⃣ BACKUP & RESTORE
# ============================================================================

class BackupManager:
    """Gestion des backups locaux et cloud"""
    
    def __init__(self):
        self.storage_path = Path(os.getenv('STORAGE_PATH', './data'))
        self.backup_path = self.storage_path / 'backups'
        self.backup_path.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, device_id: str, label: str = '') -> str:
        """Créer un backup local"""
        import uuid
        import shutil
        
        backup_id = str(uuid.uuid4())
        backup_dir = self.backup_path / f"backup_{backup_id}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copier les BDs
        shutil.copy(self.storage_path / 'devices.db', backup_dir / 'devices.db')
        shutil.copy(self.storage_path / 'changes.db', backup_dir / 'changes.db')
        
        # Créer manifest
        manifest = {
            'id': backup_id,
            'device_id': device_id,
            'label': label,
            'timestamp': datetime.now().isoformat(),
            'size': sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file())
        }
        
        with open(backup_dir / 'manifest.json', 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Backup created: {backup_id}")
        return backup_id
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """Lister les backups"""
        backups = []
        for backup_dir in self.backup_path.glob('backup_*'):
            manifest_path = backup_dir / 'manifest.json'
            if manifest_path.exists():
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                    backups.append(manifest)
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)

# ============================================================================
# 5️⃣ CLI PRINCIPAL
# ============================================================================

class SystemAnalyzerCLI:
    """Interface CLI"""
    
    def __init__(self):
        self.device_mgr = DeviceManager()
        self.analyzer = SystemChangeAnalyzer()
        self.sync = CloudSync()
        self.backup = BackupManager()
    
    def register_device(self, device_name: str):
        """Enregistrer le téléphone"""
        result = self.device_mgr.register_device(device_name)
        print(f"✅ Device registered: {result['device_id']}")
        return result
    
    def list_devices(self):
        """Lister les appareils"""
        devices = self.device_mgr.list_devices()
        print("\n📱 Appareils:")
        for device in devices:
            status = "🟢" if device['is_active'] else "🔴"
            print(f"  {status} {device['device_name']} ({device['device_id']})")
            print(f"     OS: {device['os_type']} {device['os_version']}")
            print(f"     Dernier accès: {device['last_seen']}\n")
    
    def track_change(self, change_type: str, category: str, description: str):
        """Enregistrer un changement"""
        device_id = self.device_mgr.get_device_id()
        change_id = self.analyzer.record_change(device_id, change_type, category, description)
        print(f"✅ Change recorded: {change_id}")
    
    def view_changes(self, limit: int = 50):
        """Voir les changements"""
        device_id = self.device_mgr.get_device_id()
        changes = self.analyzer.get_changes(device_id, limit)
        
        print(f"\n📊 Derniers changements ({len(changes)}):")
        for change in changes:
            severity_icon = "⚠️" if change['severity'] == 'WARNING' else "ℹ️"
            print(f"  {severity_icon} {change['category']}: {change['description']}")
            print(f"     {change['timestamp']}\n")
    
    def track_app(self, package_name: str, app_name: str, version: str):
        """Enregistrer l'installation d'une app"""
        device_id = self.device_mgr.get_device_id()
        app_id = self.analyzer.track_app_install(device_id, package_name, app_name, version)
        print(f"✅ App tracked: {app_id}")
    
    def list_apps(self):
        """Lister les apps"""
        device_id = self.device_mgr.get_device_id()
        apps = self.analyzer.get_apps(device_id)
        
        print(f"\n📦 Apps installées ({len(apps)}):")
        for app in apps:
            print(f"  {app['app_name']} ({app['package_name']})")
            print(f"     Version: {app['version']}")
            print(f"     Installée: {app['install_date']}\n")
    
    def create_backup(self, label: str = ''):
        """Créer un backup"""
        device_id = self.device_mgr.get_device_id()
        backup_id = self.backup.create_backup(device_id, label)
        print(f"✅ Backup created: {backup_id}")
    
    def sync_cloud(self):
        """Synchroniser vers le cloud"""
        device_id = self.device_mgr.get_device_id()
        
        data = {
            'device': self.device_mgr.list_devices(),
            'changes': self.analyzer.get_changes(device_id, 100),
            'apps': self.analyzer.get_apps(device_id)
        }
        
        success = self.sync.sync_to_cloud(device_id, data)
        if success:
            print("✅ Cloud sync successful")
        else:
            print("❌ Cloud sync failed")

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description='🔍 Pilons System Analyzer - Suivi multi-téléphone',
        epilog='Exemples: analyzer register "Mon Téléphone" | analyzer changes | analyzer backup'
    )
    
    subparsers = parser.add_subparsers(dest='cmd', help='Commandes')
    
    # Enregistrer
    sp = subparsers.add_parser('register', help='Enregistrer le téléphone')
    sp.add_argument('name', help='Nom du téléphone')
    
    # Lister appareils
    subparsers.add_parser('devices', help='Lister les appareils')
    
    # Changements
    subparsers.add_parser('changes', help='Voir les changements')
    
    # Apps
    subparsers.add_parser('apps', help='Lister les apps')
    
    # Backup
    subparsers.add_parser('backup', help='Créer un backup')
    
    # Sync
    subparsers.add_parser('sync', help='Synchroniser vers le cloud')
    
    args = parser.parse_args()
    cli = SystemAnalyzerCLI()
    
    try:
        if args.cmd == 'register':
            cli.register_device(args.name)
        elif args.cmd == 'devices':
            cli.list_devices()
        elif args.cmd == 'changes':
            cli.view_changes()
        elif args.cmd == 'apps':
            cli.list_apps()
        elif args.cmd == 'backup':
            cli.create_backup()
        elif args.cmd == 'sync':
            cli.sync_cloud()
        else:
            parser.print_help()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
