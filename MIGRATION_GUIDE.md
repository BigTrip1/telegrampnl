# 🚀 Telegram PNL Bot Migration Guide

This guide will help you migrate your Telegram PNL Bot to a new computer with all your data intact.

## 📋 Prerequisites

Before starting, make sure you have:
- ✅ **Python 3.8+** installed on both computers
- ✅ **MongoDB** installed and running on both computers
- ✅ **Git** installed on both computers
- ✅ **Cursor** (or any code editor) on the new computer
- ✅ Your **Telegram Bot Token** from @BotFather

## 📤 Step 1: Export Data from Current Computer

### 1.1 Export Database
```bash
# In your current project directory
python export_database.py
```

This will create a `database_backup` folder with all your MongoDB data.

### 1.2 Initialize Git Repository (if not already done)
```bash
git init
git add .
git commit -m "Initial commit - telegram pnl bot"
```

### 1.3 Push to GitHub
```bash
# Replace with your GitHub repository URL
git remote add origin https://github.com/your-username/your-repo-name.git
git branch -M main
git push -u origin main
```

## 📥 Step 2: Set Up on New Computer

### 2.1 Clone Repository
```bash
# Navigate to where you want the project
cd /path/to/your/projects
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2.2 Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2.3 Install Dependencies
```bash
pip install -r requirements.txt
```

### 2.4 Copy Database Backup
Copy the `database_backup` folder from your old computer to the new project directory.

### 2.5 Import Database
```bash
python import_database.py
```

### 2.6 Configure Environment
```bash
# Copy the template
cp config/env.production.template .env

# Edit the .env file with your actual values
```

**Edit your `.env` file with these values:**
```bash
# Telegram Bot Configuration
BOT_TOKEN=your_actual_bot_token_here

# MongoDB Configuration
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=telegram

# Moderator Configuration (your user ID)
MODERATOR_IDS=your_user_id_here

# API Configuration
COINGECKO_API_BASE=https://api.coingecko.com/api/v3

# Channel Configuration
CHANNEL_IDS=your_channel_ids_here

# Production Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## 🧪 Step 3: Test the Setup

### 3.1 Test Database Connection
```bash
python -c "from database import DatabaseManager; dm = DatabaseManager(); print('✅ Database connected!' if dm.connect() else '❌ Database connection failed!')"
```

### 3.2 Test Bot Configuration
```bash
python run_bot.py
```

If everything is set up correctly, you should see:
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

## 🔧 Troubleshooting

### MongoDB Issues
```bash
# Check if MongoDB is running
# Windows
net start MongoDB

# macOS
brew services start mongodb/brew/mongodb-community

# Linux
sudo systemctl start mongod
sudo systemctl enable mongod
```

### Permission Issues
```bash
# Make sure Python scripts are executable
chmod +x export_database.py
chmod +x import_database.py
chmod +x run_bot.py
```

### Python Path Issues
```bash
# If you get import errors, try:
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## 📊 Verify Migration Success

### Check Database Records
```bash
python -c "from database import DatabaseManager; dm = DatabaseManager(); dm.connect(); print(f'Total PNL records: {dm.pnls_collection.count_documents({})}')"
```

### Check Bot Functionality
1. Start the bot: `python run_bot.py`
2. Send `/start` to your bot
3. Try `/leaderboard` to see if your data is intact
4. Try `/stats` with your username

## 🎯 Final Steps

### 1. Update GitHub Repository
```bash
git add .
git commit -m "Updated configuration for new computer"
git push
```

### 2. Set Up Auto-Start (Optional)
Create a service or scheduled task to auto-start your bot on system boot.

### 3. Monitor Logs
```bash
# Monitor bot logs
tail -f logs/bot.log
```

## 🔐 Security Reminders

- ✅ Never commit your `.env` file to GitHub
- ✅ Keep your bot token secure
- ✅ Regularly backup your database
- ✅ Use strong passwords for your MongoDB instance
- ✅ Keep your server updated

## 📞 Support

If you encounter any issues:
1. Check the logs for error messages
2. Verify all dependencies are installed
3. Ensure MongoDB is running
4. Check your `.env` file configuration
5. Review the troubleshooting section above

## 🚀 You're All Set!

Your Telegram PNL Bot should now be running on your new computer with all your historical data intact. The migration is complete!

---

**Remember:** Always keep your database backed up regularly using the `export_database.py` script! 