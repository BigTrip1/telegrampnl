#!/usr/bin/env python3
"""
Simple script to run the Telegram PNL Bot with startup checks
"""

import os
import sys
from pathlib import Path

def check_requirements():
    """Check if all requirements are met before starting"""
    print("🔍 Performing startup checks...")
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("❌ .env file not found!")
        print("   Run 'python setup.py' to configure the bot first.")
        return False
    
    # Check if MongoDB is accessible
    try:
        from pymongo import MongoClient
        client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        client.close()
        print("✅ MongoDB connection successful")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("   Make sure MongoDB is running:")
        print("   - Windows: mongod")
        print("   - macOS/Linux: sudo systemctl start mongod")
        return False
    
    # Load environment and check bot token
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token or bot_token == "your_telegram_bot_token_here":
            print("❌ Bot token not configured!")
            print("   Edit your .env file and add your bot token from @BotFather")
            return False
        
        print("✅ Bot token configured")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    print("✅ All startup checks passed")
    return True

def run_bot():
    """Run the bot"""
    try:
        from telegram_bot import main
        main()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Bot error: {e}")
        print("Check the logs above for more details")

def main():
    """Main function"""
    print("🤖 Starting Telegram PNL Bot...")
    print("=" * 50)
    
    # Perform startup checks
    if not check_requirements():
        print("\n❌ Startup checks failed. Please fix the issues above.")
        sys.exit(1)
    
    print("\n🚀 Starting bot...")
    print("Press Ctrl+C to stop the bot")
    print("=" * 50)
    
    # Run the bot
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 