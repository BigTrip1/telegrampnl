#!/usr/bin/env python3
"""
Database Export Script for Telegram PNL Bot
This script exports all MongoDB data to JSON files for easy migration
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

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime and ObjectId objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def export_database():
    """Export all MongoDB data to JSON files"""
    
    # Create export directory
    export_dir = Path("database_backup")
    export_dir.mkdir(exist_ok=True)
    
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
    
    # Get all collections
    collections = db.list_collection_names()
    logger.info(f"Found collections: {collections}")
    
    # Export each collection
    for collection_name in collections:
        logger.info(f"Exporting collection: {collection_name}")
        
        try:
            collection = db[collection_name]
            
            # Get all documents
            documents = list(collection.find())
            
            # Export to JSON file
            output_file = export_dir / f"{collection_name}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(documents, f, cls=DateTimeEncoder, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(documents)} documents to {output_file}")
            
        except Exception as e:
            logger.error(f"Error exporting collection {collection_name}: {e}")
            continue
    
    # Create metadata file
    metadata = {
        "export_date": datetime.now(timezone.utc).isoformat(),
        "database_name": "telegram",
        "collections": collections,
        "total_collections": len(collections)
    }
    
    metadata_file = export_dir / "export_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Export completed! Files saved to {export_dir}")
    logger.info(f"Metadata saved to {metadata_file}")
    
    # Close connection
    client.close()
    return True

def main():
    """Main function"""
    print("🗄️ MongoDB Database Export Tool")
    print("=" * 50)
    
    print("This will export all your MongoDB data to JSON files.")
    print("The backup will be saved in the 'database_backup' folder.")
    print()
    
    confirm = input("Do you want to proceed? (y/N): ").lower().strip()
    if confirm != 'y':
        print("Export cancelled.")
        return
    
    print("\n📤 Starting database export...")
    
    if export_database():
        print("\n✅ Database export completed successfully!")
        print("\n📁 Your backup files are in the 'database_backup' folder")
        print("🔄 You can now copy this folder to your new computer")
        print("\n⚠️  Important: Keep these files secure as they contain your trade data!")
    else:
        print("\n❌ Database export failed!")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main() 