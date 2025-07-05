#!/usr/bin/env python3
"""
Database Import Script for Telegram PNL Bot
This script imports MongoDB data from JSON backup files
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from pymongo import MongoClient
from bson import ObjectId
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_datetime(date_string):
    """Parse datetime string from export"""
    try:
        # Handle ISO format dates
        if 'T' in date_string:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        else:
            return datetime.fromisoformat(date_string)
    except:
        return date_string

def process_document(doc):
    """Process document and convert string ObjectIds back to ObjectId objects"""
    if isinstance(doc, dict):
        for key, value in doc.items():
            if key == '_id' and isinstance(value, str):
                try:
                    doc[key] = ObjectId(value)
                except:
                    pass  # Keep as string if not valid ObjectId
            elif key == 'timestamp' and isinstance(value, str):
                doc[key] = parse_datetime(value)
            elif isinstance(value, dict):
                doc[key] = process_document(value)
            elif isinstance(value, list):
                doc[key] = [process_document(item) for item in value]
    return doc

def import_database():
    """Import all MongoDB data from JSON files"""
    
    # Check if backup directory exists
    backup_dir = Path("database_backup")
    if not backup_dir.exists():
        logger.error(f"Backup directory '{backup_dir}' not found!")
        return False
    
    # Check for metadata file
    metadata_file = backup_dir / "export_metadata.json"
    if not metadata_file.exists():
        logger.error(f"Metadata file not found: {metadata_file}")
        return False
    
    # Read metadata
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        logger.info(f"Found backup from {metadata['export_date']}")
        logger.info(f"Collections to import: {metadata['collections']}")
    except Exception as e:
        logger.error(f"Error reading metadata: {e}")
        return False
    
    # Connect to MongoDB
    try:
        client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return False
    
    # Get database
    db = client['telegram']
    
    # Import each collection
    for collection_name in metadata['collections']:
        logger.info(f"Importing collection: {collection_name}")
        
        json_file = backup_dir / f"{collection_name}.json"
        if not json_file.exists():
            logger.warning(f"JSON file not found: {json_file}")
            continue
        
        try:
            # Read JSON file
            with open(json_file, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            if not documents:
                logger.info(f"No documents found in {collection_name}")
                continue
            
            # Process documents to restore ObjectIds and dates
            processed_docs = [process_document(doc) for doc in documents]
            
            # Get or create collection
            collection = db[collection_name]
            
            # Drop existing collection if it exists
            if collection_name in db.list_collection_names():
                logger.info(f"Dropping existing collection: {collection_name}")
                collection.drop()
            
            # Insert documents
            if processed_docs:
                result = collection.insert_many(processed_docs)
                logger.info(f"Imported {len(result.inserted_ids)} documents to {collection_name}")
            else:
                logger.info(f"No documents to import for {collection_name}")
                
        except Exception as e:
            logger.error(f"Error importing collection {collection_name}: {e}")
            continue
    
    # Verify import
    logger.info("Verifying import...")
    for collection_name in metadata['collections']:
        collection = db[collection_name]
        count = collection.count_documents({})
        logger.info(f"Collection {collection_name}: {count} documents")
    
    logger.info("Import completed successfully!")
    
    # Close connection
    client.close()
    return True

def main():
    """Main function"""
    print("📥 MongoDB Database Import Tool")
    print("=" * 50)
    
    print("This will import MongoDB data from JSON backup files.")
    print("⚠️  WARNING: This will REPLACE any existing data in the database!")
    print()
    
    # Check if backup directory exists
    backup_dir = Path("database_backup")
    if not backup_dir.exists():
        print(f"❌ Backup directory '{backup_dir}' not found!")
        print("Please make sure you have copied the backup files to this location.")
        return
    
    print(f"✅ Found backup directory: {backup_dir}")
    
    # List backup files
    json_files = list(backup_dir.glob("*.json"))
    if not json_files:
        print("❌ No JSON backup files found!")
        return
    
    print(f"📁 Found {len(json_files)} backup files:")
    for file in json_files:
        print(f"   - {file.name}")
    
    print()
    confirm = input("Do you want to proceed with the import? (y/N): ").lower().strip()
    if confirm != 'y':
        print("Import cancelled.")
        return
    
    print("\n📤 Starting database import...")
    
    if import_database():
        print("\n✅ Database import completed successfully!")
        print("🤖 Your bot is now ready to run with the imported data!")
    else:
        print("\n❌ Database import failed!")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main() 