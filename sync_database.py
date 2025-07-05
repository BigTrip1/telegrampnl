#!/usr/bin/env python3
"""
Smart Database Synchronization System for Telegram PNL Bot
Ensures both Asset 1 and Asset 2 always have identical, up-to-date databases
Handles merging without duplicates and automatic conflict resolution
"""

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from pymongo import MongoClient
from bson import ObjectId
import logging
import hashlib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseSynchronizer:
    def __init__(self, database_name="telegram"):
        self.database_name = database_name
        self.client = None
        self.db = None
        self.backup_dir = Path("database_backup")
        self.sync_dir = Path("database_sync")
        
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            logger.info("Connected to MongoDB successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def create_record_hash(self, record):
        """Create a unique hash for a record to detect duplicates"""
        # Create hash based on key fields that should be unique
        hash_fields = {
            'user_id': record.get('user_id', ''),
            'username': record.get('username', ''),
            'timestamp': record.get('timestamp', '').isoformat() if hasattr(record.get('timestamp', ''), 'isoformat') else str(record.get('timestamp', '')),
            'profit_usd': record.get('profit_usd', 0),
            'profit_sol': record.get('profit_sol', 0),
            'ticker': record.get('ticker', '')
        }
        
        # Create deterministic hash
        hash_string = json.dumps(hash_fields, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def export_current_database(self, export_path=None):
        """Export current database with metadata"""
        if not export_path:
            export_path = self.sync_dir / f"current_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_path.parent.mkdir(exist_ok=True)
        
        try:
            # Get all collections
            collections = self.db.list_collection_names()
            export_data = {
                "export_timestamp": datetime.now(timezone.utc).isoformat(),
                "database_name": self.database_name,
                "collections": {}
            }
            
            total_records = 0
            
            for collection_name in collections:
                collection = self.db[collection_name]
                documents = list(collection.find())
                
                # Add hash to each document for duplicate detection
                for doc in documents:
                    doc['_sync_hash'] = self.create_record_hash(doc)
                    # Convert ObjectId to string for JSON serialization
                    if '_id' in doc and isinstance(doc['_id'], ObjectId):
                        doc['_id'] = str(doc['_id'])
                
                export_data["collections"][collection_name] = documents
                total_records += len(documents)
                logger.info(f"Exported {len(documents)} documents from {collection_name}")
            
            # Save to JSON
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, cls=DateTimeEncoder, indent=2, ensure_ascii=False)
            
            logger.info(f"Database exported successfully: {total_records} total records")
            logger.info(f"Export saved to: {export_path}")
            
            return str(export_path), total_records
            
        except Exception as e:
            logger.error(f"Error exporting database: {e}")
            return None, 0
    
    def merge_databases(self, remote_export_path, local_export_path=None):
        """Merge remote database with local database, avoiding duplicates"""
        
        # Export current local database if not provided
        if not local_export_path:
            local_export_path, _ = self.export_current_database()
        
        if not local_export_path or not os.path.exists(remote_export_path):
            logger.error("Missing export files for merge")
            return False
        
        try:
            # Load remote data
            with open(remote_export_path, 'r', encoding='utf-8') as f:
                remote_data = json.load(f)
            
            # Load local data
            with open(local_export_path, 'r', encoding='utf-8') as f:
                local_data = json.load(f)
            
            logger.info("Loaded export files for merge")
            
            # Merge each collection
            merge_stats = {}
            
            for collection_name in set(list(remote_data.get("collections", {}).keys()) + 
                                     list(local_data.get("collections", {}).keys())):
                
                remote_docs = remote_data.get("collections", {}).get(collection_name, [])
                local_docs = local_data.get("collections", {}).get(collection_name, [])
                
                merged_docs, stats = self.merge_collection_data(remote_docs, local_docs, collection_name)
                merge_stats[collection_name] = stats
                
                # Update database with merged data
                if merged_docs:
                    self.update_collection(collection_name, merged_docs)
            
            # Generate merge report
            self.generate_merge_report(merge_stats)
            
            return True
            
        except Exception as e:
            logger.error(f"Error merging databases: {e}")
            return False
    
    def merge_collection_data(self, remote_docs, local_docs, collection_name):
        """Merge documents from two collections, avoiding duplicates"""
        
        # Create hash maps for fast lookup
        local_hashes = {}
        remote_hashes = {}
        
        # Process local documents
        for doc in local_docs:
            doc_hash = doc.get('_sync_hash') or self.create_record_hash(doc)
            local_hashes[doc_hash] = doc
        
        # Process remote documents
        for doc in remote_docs:
            doc_hash = doc.get('_sync_hash') or self.create_record_hash(doc)
            remote_hashes[doc_hash] = doc
        
        # Merge logic
        merged_docs = {}
        stats = {
            'local_only': 0,
            'remote_only': 0,
            'common': 0,
            'conflicts_resolved': 0,
            'total_merged': 0
        }
        
        # Add all unique documents
        all_hashes = set(local_hashes.keys()) | set(remote_hashes.keys())
        
        for doc_hash in all_hashes:
            local_doc = local_hashes.get(doc_hash)
            remote_doc = remote_hashes.get(doc_hash)
            
            if local_doc and remote_doc:
                # Document exists in both - resolve conflicts
                resolved_doc = self.resolve_document_conflict(local_doc, remote_doc)
                merged_docs[doc_hash] = resolved_doc
                stats['common'] += 1
                if resolved_doc != local_doc:
                    stats['conflicts_resolved'] += 1
                    
            elif local_doc:
                # Document only in local
                merged_docs[doc_hash] = local_doc
                stats['local_only'] += 1
                
            elif remote_doc:
                # Document only in remote
                merged_docs[doc_hash] = remote_doc
                stats['remote_only'] += 1
        
        stats['total_merged'] = len(merged_docs)
        
        logger.info(f"Collection {collection_name} merge stats: {stats}")
        
        return list(merged_docs.values()), stats
    
    def resolve_document_conflict(self, local_doc, remote_doc):
        """Resolve conflicts between identical records from different sources"""
        
        # For PNL records, prefer the most recent or complete version
        resolved_doc = local_doc.copy()
        
        # Compare timestamps if available
        local_ts = local_doc.get('timestamp')
        remote_ts = remote_doc.get('timestamp')
        
        if remote_ts and local_ts:
            # Convert to comparable format
            if isinstance(remote_ts, str):
                try:
                    remote_ts = datetime.fromisoformat(remote_ts.replace('Z', '+00:00'))
                except:
                    pass
            if isinstance(local_ts, str):
                try:
                    local_ts = datetime.fromisoformat(local_ts.replace('Z', '+00:00'))
                except:
                    pass
            
            # Prefer more recent version
            if hasattr(remote_ts, 'timestamp') and hasattr(local_ts, 'timestamp'):
                if remote_ts > local_ts:
                    resolved_doc = remote_doc.copy()
        
        # Prefer document with more complete data
        local_fields = sum(1 for v in local_doc.values() if v is not None and v != '')
        remote_fields = sum(1 for v in remote_doc.values() if v is not None and v != '')
        
        if remote_fields > local_fields:
            resolved_doc = remote_doc.copy()
        
        # Ensure critical fields are preserved
        for field in ['user_id', 'username', 'profit_usd', 'profit_sol', 'ticker']:
            if field in remote_doc and (field not in resolved_doc or not resolved_doc[field]):
                resolved_doc[field] = remote_doc[field]
        
        return resolved_doc
    
    def update_collection(self, collection_name, documents):
        """Update collection with merged documents"""
        try:
            collection = self.db[collection_name]
            
            # Drop existing collection and recreate
            collection.drop()
            
            if documents:
                # Process documents for insertion
                for doc in documents:
                    # Convert string _id back to ObjectId if needed
                    if '_id' in doc and isinstance(doc['_id'], str):
                        try:
                            doc['_id'] = ObjectId(doc['_id'])
                        except:
                            del doc['_id']  # Let MongoDB generate new ID
                    
                    # Remove sync hash
                    doc.pop('_sync_hash', None)
                    
                    # Convert timestamp strings back to datetime
                    if 'timestamp' in doc and isinstance(doc['timestamp'], str):
                        try:
                            doc['timestamp'] = datetime.fromisoformat(doc['timestamp'].replace('Z', '+00:00'))
                        except:
                            pass
                
                collection.insert_many(documents)
                logger.info(f"Updated collection {collection_name} with {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error updating collection {collection_name}: {e}")
    
    def generate_merge_report(self, merge_stats):
        """Generate a detailed merge report"""
        report_path = self.sync_dir / f"merge_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write("DATABASE SYNCHRONIZATION REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write(f"Database: {self.database_name}\n\n")
            
            total_records = 0
            total_conflicts = 0
            
            for collection_name, stats in merge_stats.items():
                f.write(f"Collection: {collection_name}\n")
                f.write(f"  Local only records: {stats['local_only']}\n")
                f.write(f"  Remote only records: {stats['remote_only']}\n")
                f.write(f"  Common records: {stats['common']}\n")
                f.write(f"  Conflicts resolved: {stats['conflicts_resolved']}\n")
                f.write(f"  Total merged: {stats['total_merged']}\n\n")
                
                total_records += stats['total_merged']
                total_conflicts += stats['conflicts_resolved']
            
            f.write(f"SUMMARY:\n")
            f.write(f"  Total records after merge: {total_records}\n")
            f.write(f"  Total conflicts resolved: {total_conflicts}\n")
            f.write(f"  Merge status: SUCCESS\n")
        
        logger.info(f"Merge report saved to: {report_path}")
        logger.info(f"Total records after merge: {total_records}")
    
    def auto_sync_with_git(self):
        """Automatically sync database with git operations"""
        
        # Create sync directory
        self.sync_dir.mkdir(exist_ok=True)
        
        # Export current database
        export_path, record_count = self.export_current_database(
            self.sync_dir / "latest_database_export.json"
        )
        
        if export_path:
            # Copy to database_backup for git tracking
            shutil.copy2(export_path, self.backup_dir / "latest_sync.json")
            logger.info(f"Database sync completed: {record_count} records exported")
            return True
        else:
            logger.error("Database sync failed")
            return False
    
    def sync_from_remote(self, remote_export_path):
        """Sync database from remote export file"""
        
        if not os.path.exists(remote_export_path):
            logger.warning(f"Remote export file not found: {remote_export_path}")
            return False
        
        # Merge with remote data
        success = self.merge_databases(remote_export_path)
        
        if success:
            # Export updated database
            self.auto_sync_with_git()
            logger.info("Database successfully synchronized with remote data")
        else:
            logger.error("Failed to synchronize with remote data")
        
        return success
    
    def get_database_stats(self):
        """Get current database statistics"""
        stats = {}
        try:
            collections = self.db.list_collection_names()
            for collection_name in collections:
                collection = self.db[collection_name]
                count = collection.count_documents({})
                stats[collection_name] = count
            return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime and ObjectId objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Synchronization Tool")
    parser.add_argument("--export", action="store_true", help="Export current database")
    parser.add_argument("--merge", type=str, help="Merge with remote database file")
    parser.add_argument("--sync", action="store_true", help="Auto-sync with git")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    
    args = parser.parse_args()
    
    # Initialize synchronizer
    sync = DatabaseSynchronizer()
    
    if not sync.connect():
        print("❌ Failed to connect to MongoDB")
        return
    
    if args.export:
        export_path, count = sync.export_current_database()
        if export_path:
            print(f"✅ Database exported: {count} records")
            print(f"📁 File: {export_path}")
        else:
            print("❌ Export failed")
    
    elif args.merge:
        success = sync.merge_databases(args.merge)
        if success:
            print("✅ Database merge completed")
        else:
            print("❌ Merge failed")
    
    elif args.sync:
        success = sync.auto_sync_with_git()
        if success:
            print("✅ Database synchronized with git")
        else:
            print("❌ Sync failed")
    
    elif args.stats:
        stats = sync.get_database_stats()
        print("📊 Database Statistics:")
        for collection, count in stats.items():
            print(f"  {collection}: {count} records")
    
    else:
        print("🔄 Database Synchronization Tool")
        print("Use --help for available options")


if __name__ == "__main__":
    main() 