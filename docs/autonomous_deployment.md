# 🚀 Autonomous Bot Deployment Guide

## Overview
This guide provides multiple ways to run your Telegram PNL Bot autonomously without keeping a terminal window open.

## 🔧 **Option 1: Windows Service (Recommended for Windows)**

### A. Using NSSM (Non-Sucking Service Manager)

**Step 1: Download NSSM**
```bash
# Download from: https://nssm.cc/download
# Extract nssm.exe to a folder (e.g., C:\nssm\)
```

**Step 2: Install as Windows Service**
```bash
# Open Command Prompt as Administrator
cd C:\nssm\
nssm install "TelegramPNLBot" "C:\Users\Vince\AppData\Local\Programs\Python\Python312\python.exe" "C:\Users\Vince\OneDrive\Desktop\telegrampnl\run_bot.py"

# Set working directory
nssm set "TelegramPNLBot" AppDirectory "C:\Users\Vince\OneDrive\Desktop\telegrampnl"

# Set it to restart on failure
nssm set "TelegramPNLBot" AppExit Default Restart
nssm set "TelegramPNLBot" AppRestartDelay 5000

# Start the service
nssm start "TelegramPNLBot"
```

**Step 3: Manage the Service**
```bash
# Check status
nssm status "TelegramPNLBot"

# Stop service
nssm stop "TelegramPNLBot"

# Remove service (if needed)
nssm remove "TelegramPNLBot" confirm
```

### B. Using Windows Task Scheduler

**Step 1: Create Batch File**
Create `start_bot.bat` in your project folder:
```batch
@echo off
cd /d "C:\Users\Vince\OneDrive\Desktop\telegrampnl"
python run_bot.py
pause
```

**Step 2: Create Scheduled Task**
1. Open Task Scheduler (Windows + R → `taskschd.msc`)
2. Create Basic Task → Name: "Telegram PNL Bot"
3. Trigger: "When the computer starts"
4. Action: "Start a program"
5. Program: `C:\Users\Vince\OneDrive\Desktop\telegrampnl\start_bot.bat`
6. ✅ "Run with highest privileges"
7. ✅ "Run whether user is logged on or not"

## ☁️ **Option 2: Cloud Hosting (24/7 Uptime)**

### A. Railway (Free Tier Available)

**Step 1: Prepare for Railway**

Create `Procfile` in your project root:
```
web: python run_bot.py
```

Create `railway.toml`:
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python run_bot.py"
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
```

**Step 2: Deploy to Railway**
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Deploy from GitHub
4. Add environment variables in Railway dashboard
5. Your bot runs 24/7 with automatic restarts!

### B. Heroku (Free Tier Discontinued, Paid Plans Available)

Create `Procfile`:
```
worker: python run_bot.py
```

Create `runtime.txt`:
```
python-3.12.3
```

Deploy:
```bash
# Install Heroku CLI
# heroku create your-pnl-bot
# git add .
# git commit -m "Deploy bot"
# git push heroku main
```

### C. Render (Free Tier Available)

1. Connect GitHub repository
2. Choose "Background Worker" service type
3. Set start command: `python run_bot.py`
4. Add environment variables
5. Deploy!

## 🐳 **Option 3: Docker Container**

### A. Create Dockerfile

Create `Dockerfile` in project root:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Run the bot
CMD ["python", "run_bot.py"]
```

### B. Create docker-compose.yml

```yaml
version: '3.8'

services:
  telegram-bot:
    build: .
    container_name: telegram-pnl-bot
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - MONGODB_HOST=mongodb
      - MONGODB_PORT=27017
      - MONGODB_DATABASE=telegram
      - MODERATOR_IDS=${MODERATOR_IDS}
      - CHANNEL_IDS=${CHANNEL_IDS}
    depends_on:
      - mongodb
    restart: unless-stopped
    networks:
      - bot-network

  mongodb:
    image: mongo:7
    container_name: telegram-bot-mongodb
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    restart: unless-stopped
    networks:
      - bot-network

volumes:
  mongodb_data:

networks:
  bot-network:
    driver: bridge
```

### C. Run with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f telegram-bot

# Stop
docker-compose down
```

## 🖥️ **Option 4: VPS/Server Deployment**

### A. Using systemd (Linux/WSL)

Create `/etc/systemd/system/telegram-pnl-bot.service`:
```ini
[Unit]
Description=Telegram PNL Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/telegrampnl
Environment=PATH=/usr/bin:/usr/local/bin
ExecStart=/usr/bin/python3 run_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-pnl-bot
sudo systemctl start telegram-pnl-bot

# Check status
sudo systemctl status telegram-pnl-bot
```

### B. Using PM2 (Process Manager)

```bash
# Install PM2
npm install -g pm2

# Start bot with PM2
pm2 start run_bot.py --name "telegram-pnl-bot" --interpreter python3

# Save PM2 configuration
pm2 save
pm2 startup

# Monitor
pm2 status
pm2 logs telegram-pnl-bot
```

## 🔧 **Option 5: Screen/Tmux (Simple but Effective)**

### Using Screen (Linux/WSL/Git Bash)

```bash
# Start a screen session
screen -S telegram-bot

# Inside screen, run your bot
cd /c/Users/Vince/OneDrive/Desktop/telegrampnl
python run_bot.py

# Detach from screen (Ctrl+A, then D)
# Your bot keeps running!

# Reattach later
screen -r telegram-bot
```

## 📊 **Monitoring & Maintenance**

### Enhanced Logging for Production

Update your bot to include better logging:

Create `production_logger.py`:
```python
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_production_logging():
    """Set up production-grade logging"""
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console output
            logging.StreamHandler(),
            # File output with rotation
            RotatingFileHandler(
                'logs/telegram_bot.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
        ]
    )
    
    return logging.getLogger(__name__)
```

### Health Check Endpoint

Add to your bot for monitoring:

```python
async def health_check(update: Update, context) -> None:
    """Health check endpoint for monitoring"""
    await update.message.reply_text(
        f"✅ Bot is healthy!\n"
        f"🕐 Uptime: {datetime.now()}\n"
        f"📊 Active sessions: {len(self.user_sessions)}"
    )
```

## 🚨 **Important Notes**

### For All Deployment Methods:

1. **Environment Variables**: Ensure all your env variables are set
2. **Database Access**: MongoDB must be accessible to your bot
3. **Error Handling**: The "Message to be replied not found" error in your logs is normal - it happens when users delete messages during conversations

### Fix the Reply Error:

Add this to your command functions:
```python
async def safe_reply(self, update: Update, message: str, **kwargs):
    """Safely reply to messages"""
    try:
        return await update.message.reply_text(message, **kwargs)
    except Exception as e:
        logger.warning(f"Failed to reply: {e}")
        # Try sending without reply
        return await update.effective_chat.send_message(message, **kwargs)
```

## 🎯 **Recommendation for You**

**For Windows (Your Current Setup):**
1. **Start with NSSM** (Option 1A) - easiest for Windows
2. **Upgrade to Railway** (Option 2A) - for 24/7 cloud hosting

**For Maximum Reliability:**
- Use Railway/Render for hosting
- Keep local MongoDB or upgrade to MongoDB Atlas
- Set up monitoring with health checks

Would you like me to help you implement any of these deployment options? 