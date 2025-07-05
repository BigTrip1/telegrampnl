#!/usr/bin/env python3
"""
Setup script for Telegram PNL Bot
This script helps with initial setup and configuration testing
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print setup banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                  TELEGRAM PNL BOT SETUP                      ║
    ║                                                               ║
    ║  This script will help you set up your Telegram PNL Bot      ║
    ║  for tracking trading profits in your community.             ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Please upgrade your Python installation.")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_pip():
    """Check if pip is available"""
    print("📦 Checking pip availability...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        print("✅ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip is not available. Please install pip.")
        return False

def install_requirements():
    """Install required packages"""
    print("📋 Installing required packages...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All packages installed successfully")
            return True
        else:
            print(f"❌ Error installing packages: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        return False

def check_mongodb():
    """Check if MongoDB is accessible"""
    print("🍃 Checking MongoDB connection...")
    try:
        from pymongo import MongoClient
        client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        print("✅ MongoDB is running and accessible")
        client.close()
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("   Make sure MongoDB is installed and running:")
        print("   - Windows: Run 'mongod' in command prompt")
        print("   - macOS/Linux: Run 'sudo systemctl start mongod'")
        return False

def setup_env_file():
    """Guide user through environment file setup"""
    print("⚙️  Setting up environment configuration...")
    
    env_file = Path('.env')
    template_file = Path('config.env.template')
    
    if env_file.exists():
        overwrite = input("📄 .env file already exists. Overwrite? (y/N): ").lower()
        if overwrite != 'y':
            print("   Keeping existing .env file")
            return True
    
    if not template_file.exists():
        print("❌ Template file not found. Creating basic .env file...")
        env_content = """# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here

# MongoDB Configuration
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=telegram

# Moderator Configuration (comma-separated user IDs)
MODERATOR_IDS=123456789,987654321

# API Configuration
COINGECKO_API_BASE=https://api.coingecko.com/api/v3

# Channel Configuration (optional)
CHANNEL_ID=@your_channel_username
"""
    else:
        with open(template_file, 'r') as f:
            env_content = f.read()
    
    print("\n📝 Please provide the following information:")
    
    # Get bot token
    while True:
        bot_token = input("🤖 Enter your Telegram bot token (from @BotFather): ").strip()
        if bot_token and bot_token != "your_telegram_bot_token_here":
            break
        print("   Please enter a valid bot token")
    
    # Get moderator IDs
    moderator_ids = input("👮 Enter moderator user IDs (comma-separated, or press Enter to skip): ").strip()
    if not moderator_ids:
        moderator_ids = "123456789"
    
    # Get channel ID
    channel_id = input("📢 Enter channel username (e.g., @mychannel, or press Enter to skip): ").strip()
    if not channel_id:
        channel_id = ""
    
    # Update environment content
    env_content = env_content.replace("your_telegram_bot_token_here", bot_token)
    env_content = env_content.replace("123456789,987654321", moderator_ids)
    if channel_id:
        env_content = env_content.replace("@your_channel_username", channel_id)
    
    # Write .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Environment file created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_configuration():
    """Test the configuration"""
    print("🧪 Testing configuration...")
    
    try:
        # Test environment loading
        from dotenv import load_dotenv
        load_dotenv()
        
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token or bot_token == "your_telegram_bot_token_here":
            print("❌ Bot token not configured properly")
            return False
        
        print("✅ Environment variables loaded")
        
        # Test database connection
        from database import db_manager
        if db_manager.connect():
            print("✅ Database connection successful")
            db_manager.close_connection()
        else:
            print("❌ Database connection failed")
            return False
        
        # Test currency converter
        from utils import currency_converter
        rate = currency_converter.get_sol_usd_rate()
        if rate:
            print(f"✅ Currency conversion working (SOL/USD: ${rate})")
        else:
            print("⚠️  Currency conversion unavailable (will use fallback)")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def show_next_steps():
    """Show what to do next"""
    print("\n🎉 Setup Complete! Here's what to do next:")
    print("\n📋 Next Steps:")
    print("1. 🤖 Test your bot: python telegram_bot.py")
    print("2. 📱 Find your bot on Telegram and send /start")
    print("3. 📊 Try submitting a PNL with /submit")
    print("4. 📈 (Optional) Import historical data: python data_import.py")
    print("\n📚 Documentation:")
    print("- README.md - Complete setup and usage guide")
    print("- ProjectOverview.md - Detailed project documentation")
    print("\n🆘 Need Help?")
    print("- Check logs for error messages")
    print("- Review troubleshooting section in README.md")
    print("- Ensure MongoDB is running before starting the bot")
    print("\n🚀 Ready to start your PNL tracking community!")

def main():
    """Main setup function"""
    print_banner()
    
    # Check system requirements
    if not check_python_version():
        return False
    
    if not check_pip():
        return False
    
    # Install packages
    if not install_requirements():
        return False
    
    # Check MongoDB
    mongodb_ok = check_mongodb()
    if not mongodb_ok:
        print("⚠️  MongoDB not accessible. You'll need to start it before running the bot.")
    
    # Setup environment
    if not setup_env_file():
        return False
    
    # Test configuration
    if test_configuration():
        show_next_steps()
        return True
    else:
        print("\n❌ Setup completed with some issues. Check the configuration and try again.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⛔ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1) 