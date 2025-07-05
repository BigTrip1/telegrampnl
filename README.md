# 🏛️ PNL Trading Bot - Complete System

## ✅ **Quick Start**

### **1. Launch Your Bot**
```bash
# Double-click this file to start everything:
LAUNCH_PNL_BOT.bat
```

### **2. Alternative Methods**
```bash
# Direct Python execution:
python telegram_bot.py

# Alternative runner:
python run_bot.py

# Manual dependency installation:
MANUAL_INSTALL_DEPENDENCIES.bat
```

---

## 📁 **Directory Structure**

### **📂 Root Files (Core System)**
```
📁 telegrampnl/
├── 🤖 telegram_bot.py          # Main bot application
├── 🗄️ database.py              # Database manager
├── 🛠️ utils.py                 # Utilities and helpers
├── 🚀 run_bot.py               # Alternative bot runner
├── 📦 requirements.txt         # Python dependencies
├── 🔧 LAUNCH_PNL_BOT.bat       # Main launcher (CLICK THIS!)
├── 🛠️ MANUAL_INSTALL_DEPENDENCIES.bat  # Backup installer
└── 📖 README.md                # This file
```

### **📂 Organized Folders**

#### **📁 docs/** - Technical Documentation
- System documentation and technical guides
- API references and development docs
- Battle system documentation

#### **📁 guides/** - User Guides
- Step-by-step user tutorials
- PNL submission guides
- Deployment instructions

#### **📁 marketing/** - Marketing Materials
- Social media posts
- Community announcements
- Battle system promotions

#### **📁 config/** - Configuration Files
- Environment templates
- Docker configuration
- BotFather commands
- Deployment configs

#### **📁 utilities/** - Utility Scripts
- Data import tools
- Setup scripts
- Maintenance utilities

---

## 🎯 **Features**

### **📊 Complete PNL Analytics (49+ Commands)**
- `/submit` - Submit trades with screenshots
- `/leaderboard` - View rankings
- `/mystats` - Personal analytics
- `/monthlyreport` - Monthly summaries
- **+45 more analytical commands**

### **🔥 Battle System (NEW!)**

#### **⚔️ Profit Battles**
- **Objective**: Earn the most USD profit during the battle period
- **Command**: `/profitbattle`
- **Duration**: 15 minutes to 4 weeks (customizable)
- **Participants**: 2-8 players

#### **⚡ Trade Wars**
- **Objective**: Execute the most trades during the battle period
- **Command**: `/tradewar`
- **Duration**: 15 minutes to 4 weeks (customizable)
- **Participants**: 2-8 players

#### **🏆 Battle Features**
- Real-time leaderboard tracking
- Automatic battle completion
- Epic victory announcements
- Battle points system
- Hall of champions

#### **🎮 Battle Commands**
- `/profitbattle` - Start profit battles
- `/tradewar` - Start trade count wars
- `/battlerules` - Complete battle guide
- `/battlpoints` - Your battle stats
- `/battleleaderboard` - Battle champions

### **🏛️ Advanced Features**
- **Multi-channel posting**
- **Auto photo detection**
- **Real-time monitoring**
- **Achievement system**
- **Token intelligence**

---

## 🚀 **Installation**

### **Method 1: One-Click Launch (Recommended)**
1. **Double-click `LAUNCH_PNL_BOT.bat`**
2. **Wait for setup to complete**
3. **Bot starts automatically**

### **Method 2: Manual Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Start bot
python telegram_bot.py
```

### **Method 3: Troubleshooting**
```bash
# If you have issues, use the manual installer
MANUAL_INSTALL_DEPENDENCIES.bat
```

---

## 📋 **Requirements**

### **System Requirements**
- **Python 3.8+** (3.12.3 recommended)
- **MongoDB** (local or cloud)
- **Windows 10/11** (for .bat launchers)

### **Dependencies**
- `python-telegram-bot==20.7`
- `pymongo`
- `requests`
- `python-dotenv`
- `pillow`
- `pytz`

---

## ⚙️ **Configuration**

### **Environment Variables**
Create a `.env` file in the root directory:
```env
BOT_TOKEN=your_telegram_bot_token_here
MONGODB_URI=mongodb://localhost:27017/pnl_bot
CHANNEL_CONFIG={"pnl_channel": "channel_id_here"}
```

### **MongoDB Setup**
- **Local:** Install MongoDB Community Server
- **Cloud:** Use MongoDB Atlas
- **Connection:** Auto-configured in launcher

---

## 🔧 **Usage**

### **For Users**
1. **Start bot:** Double-click `LAUNCH_PNL_BOT.bat`
2. **Add trades:** Use `/submit` command in Telegram
3. **View stats:** Use `/mystats` or `/leaderboard`
4. **Start battles:** Use `/profitbattle` or `/tradewar`

### **For Developers**
1. **Core files:** `telegram_bot.py`, `database.py`, `utils.py`
2. **Documentation:** Check `docs/` folder
3. **Configuration:** Check `config/` folder
4. **Utilities:** Check `utilities/` folder

---

## 📞 **Support**

### **Common Issues**
- **Dependencies:** Use `MANUAL_INSTALL_DEPENDENCIES.bat`
- **Permissions:** Run as administrator
- **Documentation:** Check `docs/INSTALLATION_TROUBLESHOOTING.md`

### **File Locations**
- **User guides:** `guides/` folder
- **Technical docs:** `docs/` folder
- **Configuration:** `config/` folder
- **Troubleshooting:** `docs/INSTALLATION_TROUBLESHOOTING.md`

---

## 🏆 **System Status**

✅ **Fully Functional** - All 49+ commands working  
✅ **Battle System** - Epic gladiator competitions  
✅ **Database** - MongoDB integration  
✅ **Multi-channel** - Professional posting  
✅ **Auto-installer** - One-click setup  
✅ **Error Handling** - Robust and reliable  

---

## 🎯 **Quick Commands**

### **Essential Commands**
```bash
# Start bot (main method)
Double-click: LAUNCH_PNL_BOT.bat

# Start bot (alternative)
python telegram_bot.py

# Install dependencies manually
Double-click: MANUAL_INSTALL_DEPENDENCIES.bat

# Check logs
# Watch the Python terminal for real-time logs
```

### **Development Commands**
```bash
# Import historical data
python utilities/data_import.py

# System setup
python utilities/setup.py

# Database operations
python -c "from database import db_manager; db_manager.test_connection()"
```

---

**🏛️ Your complete PNL trading bot system is ready! Double-click `LAUNCH_PNL_BOT.bat` to begin!** ⚔️ 