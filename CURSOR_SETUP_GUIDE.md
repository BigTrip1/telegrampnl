# 🎯 Cursor AI Setup Guide for Telegram PNL Bot

**This guide is specifically designed for Cursor AI to help set up the Telegram PNL Bot on a new computer.**

## 🤖 **For Cursor AI Assistant - Project Overview**

You are helping to set up a **Telegram PNL Bot** that tracks trading profits and losses for a community. This bot:

- 📊 **Tracks PNL submissions** from users via Telegram
- 🏆 **Maintains leaderboards** (daily, weekly, monthly, all-time)
- ⚔️ **Runs trading battles** between users
- 🎯 **Provides analytics** on tokens, users, and trading performance
- 💾 **Uses MongoDB** for data persistence
- 🚀 **Built with Python** using python-telegram-bot library

### **Key Files You Need to Know:**
- `telegram_bot.py` - Main bot logic (3203 lines)
- `database.py` - MongoDB operations (1688 lines)
- `utils.py` - Utility functions and formatters (959 lines)
- `run_bot.py` - Bot startup script with checks
- `requirements.txt` - Python dependencies
- `database_backup/` - **Contains 190 PNL records** for migration

## 🎯 **Current Status - What We Have:**

✅ **Database Backup Ready**: 190 PNL records exported from original computer
✅ **All Code Pushed**: Complete bot codebase in repository
✅ **Migration Tools Ready**: Import/export scripts available
✅ **Documentation Complete**: Comprehensive guides included

## 🚀 **Step-by-Step Setup Process**

### **Step 1: Project Setup**
```bash
# Clone the repository
git clone https://github.com/BigTrip1/telegrampnl.git
cd telegrampnl

# Create virtual environment (recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **Step 2: MongoDB Setup**
```bash
# Make sure MongoDB is installed and running
# Windows: net start MongoDB
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod

# Test MongoDB connection
python -c "from pymongo import MongoClient; client = MongoClient('localhost', 27017); client.admin.command('ping'); print('✅ MongoDB connected!')"
```

### **Step 3: Database Import**
```bash
# Import the 190 PNL records from the backup
python import_database.py
```

**This will:**
- Import the `pnls` collection with 190 trading records
- Restore all user data, profits, and trading history
- Preserve all timestamps and ObjectIds

### **Step 4: Environment Configuration**
```bash
# Copy template to create environment file
cp config/env.production.template .env
```

**Edit the `.env` file with these values:**
```env
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_from_botfather

# MongoDB Configuration (usually these defaults work)
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=telegram

# Moderator Configuration
MODERATOR_IDS=your_telegram_user_id

# API Configuration
COINGECKO_API_BASE=https://api.coingecko.com/api/v3

# Channel Configuration (update with your channel/group IDs)
CHANNEL_IDS=your_channel_ids_here

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### **Step 5: Start the Bot**
```bash
python run_bot.py
```

**Expected Output:**
```
🤖 Starting Telegram PNL Bot...
==================================================
🔍 Performing startup checks...
✅ MongoDB connection successful
✅ Bot token configured
✅ All startup checks passed

🚀 Starting bot...
Press Ctrl+C to stop the bot
==================================================
```

## 🔧 **Troubleshooting Common Issues**

### **MongoDB Connection Issues**
```bash
# Check if MongoDB is running
# Windows:
net start MongoDB
# macOS:
brew services list | grep mongodb
# Linux:
sudo systemctl status mongod
```

### **Python Dependencies Issues**
```bash
# If you get import errors, try:
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### **Bot Token Issues**
- Get token from @BotFather on Telegram
- Make sure token is correctly set in `.env` file
- Token should start with something like `1234567890:ABC...`

### **Database Import Issues**
```bash
# Check if backup files exist
ls database_backup/
# Should show: pnls.json, export_metadata.json

# Check MongoDB collections after import
python -c "from database import DatabaseManager; dm = DatabaseManager(); dm.connect(); print(f'PNL records: {dm.pnls_collection.count_documents({})}')"
```

## 🎯 **Key Bot Commands to Test**

Once running, test these commands in Telegram:

- `/start` - Welcome message
- `/help` - Command list
- `/leaderboard` - Show current leaderboard
- `/stats @username` - User statistics
- `/submit` - Submit a PNL (screenshot required)
- `/tradewar` - Start a trading battle

## 📊 **Database Schema Overview**

### **PNL Collection Structure:**
```json
{
  "_id": "ObjectId",
  "user_id": "telegram_user_id",
  "username": "telegram_username",
  "profit_usd": 123.45,
  "profit_sol": 0.565,
  "ticker": "TOKEN",
  "timestamp": "2024-01-01T00:00:00Z",
  "screenshot_url": "image_url",
  "verified": true/false
}
```

### **Battle Collection Structure:**
```json
{
  "_id": "ObjectId",
  "battle_type": "tradewar",
  "participants": ["user1", "user2"],
  "start_time": "timestamp",
  "end_time": "timestamp",
  "status": "active/completed",
  "winner": "username"
}
```

## 🔥 **Important Notes for Cursor AI**

1. **Profit Display Format**: User prefers Solana profits with decimal formatting (e.g., `0.565 sol`, `12.987 sol`)

2. **Battle System**: Uses **trade count** (number of trades) as the metric, not volume

3. **Database Connection**: Always use `DatabaseManager` class from `database.py`

4. **Error Handling**: Bot has comprehensive error handling and logging

5. **Security**: Never commit `.env` files - they contain sensitive tokens

## 🎨 **Bot Features Overview**

### **Core Features:**
- 📈 **PNL Tracking**: Users submit trading screenshots
- 🏆 **Leaderboards**: Multiple timeframes and metrics
- ⚔️ **Trading Battles**: Competitive trading contests
- 📊 **Analytics**: Token popularity, user stats, market sentiment
- 🎯 **Achievements**: User milestones and streaks

### **Advanced Features:**
- 🔍 **Search**: Find trades by ticker or username
- 📱 **Export**: User data export to Excel
- 🎭 **Portfolios**: User portfolio tracking
- 📈 **Trends**: Market sentiment analysis
- 🏅 **Hall of Fame**: Top performers showcase

## 🚀 **Ready to Run!**

After completing these steps, your Telegram PNL Bot will be:
- ✅ **Fully functional** with all original features
- ✅ **Database restored** with 190 historical records
- ✅ **Ready for users** to submit new PNLs
- ✅ **Battle system active** for trading competitions

The bot maintains all user data, leaderboards, and trading history from the original installation.

## 📞 **Need Help?**

If you encounter issues:
1. Check the error logs in the terminal
2. Verify MongoDB is running
3. Confirm `.env` file is properly configured
4. Test database connection with provided commands
5. Refer to `MIGRATION_GUIDE.md` for additional troubleshooting

**The bot is production-ready and battle-tested with 190+ trading records!** 🎯 