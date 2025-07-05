# Telegram PNL Bot 🚀

**The Ultimate Trading Analytics & Community Competition Platform**

A sophisticated Telegram bot for tracking trading performance, community leaderboards, and epic profit battles. Built for serious traders who want professional-grade analytics with gamified competition.

## 🌟 Key Features

### 📊 **Advanced Trading Analytics**
- **Personal Dashboard** (`/mystats`) - Complete trading performance overview
- **Smart Username Matching** - Handles @username and username formats seamlessly
- **ROI Calculations** - Accurate returns using USD-converted investment amounts
- **Win Rate Analysis** - Detailed profit/loss statistics
- **Portfolio Diversification** - Token distribution insights
- **Trade History** - Complete chronological trading records

### 🏆 **Dynamic Leaderboards**
- **All-Time Champions** - Ultimate profit rankings
- **Time-Based Boards** - Monthly, weekly, and daily leaders
- **Trade Volume Kings** - Most active traders
- **ROI Masters** - Best percentage returns
- **Investment Categories** - Small cap, mid cap, large cap rankings
- **Real-Time Updates** - Live recalculation with enhanced aggregation

### ⚔️ **Epic Battle System**
- **Profit Battles** - Compete for highest USD profit
- **Trade Wars** - Volume-based trading competitions
- **Custom Durations** - From 15 minutes to 4 weeks
- **Gladiator Themes** - Epic announcements and victory celebrations
- **Battle Points** - Persistent ranking system across all battles
- **Real-Time Tracking** - Live updates during competitions

### 🎮 **Gamification & Social**
- **Achievement System** - Trading badges and milestones
- **Streak Tracking** - Win/loss streaks monitoring
- **Community Challenges** - Group competitions and events
- **Token Intelligence** - Most profitable tokens analysis
- **Market Sentiment** - Community trading trends

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- MongoDB Atlas account
- Telegram Bot Token (from @BotFather)
- Channel/Group admin permissions

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/telegram-pnl-bot.git
cd telegram-pnl-bot
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment Setup**
Create `.env` file:
```env
BOT_TOKEN=your_telegram_bot_token
MONGODB_URI=your_mongodb_connection_string
CHANNEL_IDS=your_channel_id_1,your_channel_id_2
MODERATOR_IDS=your_user_id,other_mod_id

# Test Mode (optional)
TEST_MODE=false
TEST_CHAT_IDS=test_chat_id_1,test_chat_id_2
```

4. **Database Setup**
```bash
python database.py  # Initialize collections and indexes
```

5. **Launch Bot**
```bash
python telegram_bot.py
```

## 📱 Mobile-Optimized Features

### **Smart Photo Detection**
- Upload any screenshot → Bot automatically asks if it's a PNL entry
- Works in groups and private chats
- Supports both photo and document image formats
- Clean form interface with message cleanup

### **Streamlined Submission**
1. Upload screenshot 📸
2. Select currency (USD/SOL) 💰
3. Enter ticker symbol 🎯
4. Input investment amount 💵
5. Enter profit/loss ⚡

**Result**: Clean final post with all form messages automatically deleted!

## 🏛️ Battle System Guide

### **Starting Battles**

**Profit Battle** (`/profitbattle`):
- Objective: Earn highest USD profit
- Duration: 15 minutes to 4 weeks
- Players: 2-8 participants
- Scoring: Total profit during battle period

**Trade War** (`/tradewar`):
- Objective: Execute most trades
- Duration: 15 minutes to 4 weeks  
- Players: 2-8 participants
- Scoring: Total trade count (profit irrelevant)

### **Battle Setup Process**
1. Choose battle type
2. Select number of players (2-8)
3. Set duration (presets or custom)
4. Add participants (@username format)
5. Confirm and commence!

### **Battle Points System**
- 🥇 **1st Place**: 100 points + Champion badge
- 🥈 **2nd Place**: 75 points + Silver medal
- 🥉 **3rd Place**: 50 points + Bronze medal
- 🎖️ **Participation**: 25 points + Warrior badge

### **Epic Announcements**
- Gladiator-themed battle starts
- Leader change notifications
- Victory celebrations with detailed stats
- Hall of fame recognition

## 🔧 Command Reference

### **🚀 Getting Started**
- `/start` - Bot welcome & feature overview
- `/help` - Complete command guide
- `/submit` - Submit PNL with screenshot
- `/pnlguide` - Detailed submission instructions

### **🏆 Leaderboards**
- `/leaderboard` - All-time profit champions
- `/monthlyleaderboard` - This month's top performers
- `/weeklyleaderboard` - This week's winners
- `/dailyleaderboard` - Today's leaders
- `/tradeleader` - Most active traders
- `/profitgoat` - Highest single profit holder

### **📊 Personal Analytics**
- `/mystats` - Complete trading dashboard
- `/myhistory` - Your trading journey
- `/compare @username` - Head-to-head analysis
- `/portfolio` - Token diversification insights
- `/monthlyreport` - Personal monthly summary

### **⚔️ Battle Commands**
- `/profitbattle` - Start profit competition
- `/tradewar` - Start trade count war
- `/battlerules` - Complete battle guide
- `/battlpoints` - Your battle record
- `/battleleaderboard` - Hall of champions

### **🎯 Token Intelligence**
- `/tokenleader` - Most profitable tokens
- `/tokenstats TICKER` - Deep token analysis
- `/trendingcoins` - What's hot right now
- `/search TICKER` - Find trades by token

### **🎮 Gamification**
- `/achievements` - Your trading badges
- `/streaks` - Win/loss streak tracking
- `/milestones` - Progress toward goals
- `/randomtrade` - Get inspired by epic wins

## 🔧 Technical Architecture

### **Database Schema**
- **PNLs Collection**: Trading records with enhanced indexing
- **Battles Collection**: Competition tracking and results
- **Users Collection**: Battle points and achievements
- **Advanced Aggregation**: Real-time leaderboard calculations

### **Enhanced Features**
- **Username Normalization**: Handles @username vs username variations
- **Currency Conversion**: Real-time SOL/USD rates via CoinGecko
- **ROI Accuracy**: Uses USD-converted investment amounts
- **Mobile Optimization**: Photo detection and clean interfaces
- **Test Mode**: Safe testing without posting to channels

### **Performance Optimizations**
- MongoDB aggregation pipelines for complex queries
- Efficient indexing for fast leaderboard generation
- Caching for currency conversion rates
- Parallel database operations

## 🧪 Testing & Development

### **Test Mode**
```env
TEST_MODE=true
TEST_CHAT_IDS=your_test_chat_id
```

**Benefits**:
- PNL submissions won't post to actual channels
- Safe testing environment
- All features work normally
- Use `/testmode` to check status

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Check code quality
python -m py_compile telegram_bot.py
python -m py_compile database.py
```

## 📈 Recent Updates

### **v2.1.0 - Enhanced Analytics & Battle System**
- ✅ **Fixed /mystats command** - Resolved calculation errors and improved accuracy
- ✅ **Enhanced Username Matching** - Comprehensive @username and username support
- ✅ **Improved ROI Calculations** - Now uses USD-converted investment amounts
- ✅ **Battle System Overhaul** - Gladiator-themed competitions with points
- ✅ **Leaderboard Enhancements** - Better aggregation and performance indicators
- ✅ **Mobile Optimization** - Photo auto-detection and clean interfaces
- ✅ **Test Mode Implementation** - Safe testing environment

### **v2.0.0 - Major Platform Upgrade**
- ✅ **Complete Database Redesign** - Enhanced aggregation pipelines
- ✅ **Battle System Launch** - Profit battles and trade wars
- ✅ **Advanced Analytics** - Comprehensive trading insights
- ✅ **Mobile-First Design** - Optimized for mobile users
- ✅ **Community Features** - Social trading and competitions

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check `/help` command in bot
- **Issues**: GitHub Issues section
- **Community**: Join our Telegram group
- **Contact**: Reach out to bot administrators

## 🌟 Acknowledgments

- Built with python-telegram-bot library
- MongoDB for robust data storage
- CoinGecko API for real-time pricing
- Community feedback and testing

---

**Ready to revolutionize your trading analytics?** 🚀

Add the bot to your group and start tracking your trading journey with professional-grade insights and epic community competitions!

*"Those who dare to trade, dare to win!"* ⚔️ 