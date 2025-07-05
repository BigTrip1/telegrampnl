# 🤖 **Trading Analytics Bot - Complete Command Documentation**

*Comprehensive guide to all commands, features, and calculations*

---

## 📚 **Table of Contents**

1. [Getting Started Commands](#getting-started)
2. [Submission Commands](#submission)
3. [Leaderboard Commands](#leaderboards)
4. [Personal Analytics](#personal-analytics)
5. [Token Intelligence](#token-intelligence)
6. [Advanced Rankings](#advanced-rankings)
7. [Search & Discovery](#search-discovery)
8. [Achievements & Gamification](#achievements)
9. [Market Intelligence](#market-intelligence)
10. [Community Overview](#community-overview)
11. [Utility Commands](#utility)

---

## 🚀 **Getting Started** {#getting-started}

### `/start`
**Description:** Welcome message and bot introduction  
**Calculation:** None  
**Purpose:** Provides overview of all features and quick start guide for new users  

### `/help`
**Description:** Comprehensive command reference and usage guide  
**Calculation:** None  
**Purpose:** Complete documentation of all commands with examples  

### `/pnlguide`
**Description:** Detailed step-by-step submission tutorial  
**Calculation:** None  
**Purpose:** Teaches users how to submit trades using both auto-detection and manual methods  

---

## 📊 **Submission Commands** {#submission}

### `/submit`
**Description:** Start interactive trade submission process  
**Calculation:** None (entry point)  
**Purpose:** Initiates 5-step guided form:
1. Screenshot upload
2. Currency selection (USD/SOL)
3. Ticker input
4. Investment amount
5. Profit/loss amount

### `/cancel`
**Description:** Cancel any ongoing submission process  
**Calculation:** None  
**Purpose:** Safely exits submission flow and cleans up temporary data  

---

## 🏆 **Leaderboard Commands** {#leaderboards}

### `/leaderboard`
**Description:** All-time profit leaders  
**Database Query:** Groups by username, sums profit_usd  
**Calculation:**
```sql
SELECT username, SUM(profit_usd) as total_profit_usd, COUNT(*) as trade_count
FROM pnls GROUP BY username ORDER BY total_profit_usd DESC
```
**Purpose:** Shows top 10 traders by total USD profit across all time

### `/monthlyleaderboard`
**Description:** Current month's top performers  
**Database Query:** Same as leaderboard but filtered by current month  
**Calculation:**
```sql
SELECT username, SUM(profit_usd) as total_profit_usd, COUNT(*) as trade_count
FROM pnls WHERE timestamp >= start_of_month AND timestamp < start_of_next_month
GROUP BY username ORDER BY total_profit_usd DESC
```
**Purpose:** Monthly competition rankings

### `/weeklyleaderboard`
**Description:** Current week's winners (Monday-Sunday)  
**Database Query:** Leaderboard filtered to current week  
**Calculation:** Uses `date_helper.get_current_week_range()` for Monday 00:00 to Sunday 23:59  
**Purpose:** Short-term performance tracking

### `/dailyleaderboard`
**Description:** Today's top traders  
**Database Query:** Leaderboard filtered to current day  
**Calculation:** Filters trades from 00:00:00 to 23:59:59 of current day  
**Purpose:** Daily competition and real-time performance

### `/tradeleader`
**Description:** Most active traders by trade count  
**Database Query:** Groups by username, counts trades  
**Calculation:**
```sql
SELECT username, COUNT(*) as trade_count, SUM(profit_usd) as total_profit_usd
FROM pnls GROUP BY username ORDER BY trade_count DESC
```
**Purpose:** Rewards trading activity and frequency

### `/profitgoat`
**Description:** Single highest profit holder  
**Database Query:** All-time leaderboard limited to 1 result  
**Calculation:** Same as leaderboard but LIMIT 1  
**Purpose:** Celebrates the ultimate profit champion

---

## 📈 **Personal Analytics** {#personal-analytics}

### `/mystats`
**Description:** Complete personal trading dashboard  
**Database Query:** Aggregates all user's trades  
**Calculations:**
- **Total Profit:** `SUM(profit_usd)`
- **Trade Count:** `COUNT(*)`
- **Win Rate:** `(winning_trades / total_trades) * 100`
- **ROI:** `(total_profit / total_investment) * 100`
- **Best Trade:** `MAX(profit_usd)`
- **Worst Trade:** `MIN(profit_usd)`
- **Average Profit:** `total_profit / trade_count`
**Purpose:** Personal performance analysis and progress tracking

### `/myhistory`
**Description:** Recent 20 trades with full details  
**Database Query:** User's trades ordered by timestamp DESC  
**Calculation:** Shows date, ticker, investment, profit, percentage gain  
**Purpose:** Trade-by-trade review and learning

### `/compare @username`
**Description:** Head-to-head comparison with another trader  
**Database Query:** Gets stats for both users  
**Calculations:**
- Side-by-side profit comparison
- Trade count comparison  
- Win rate comparison
- Best trade comparison
**Purpose:** Competitive analysis and benchmarking

### `/portfolio`
**Description:** Token diversification analysis  
**Database Query:** Groups user's trades by ticker  
**Calculations:**
- **Token Allocation:** `investment_per_token / total_investment * 100`
- **Token Performance:** Profit per token
- **Success Rate per Token:** Win rate by ticker
**Purpose:** Portfolio optimization insights

### `/monthlyreport`
**Description:** Comprehensive monthly trading summary  
**Database Query:** User's trades filtered to current month  
**Calculations:**
- Monthly profit trends
- Best performing tokens
- Trading frequency analysis
- Month-over-month growth
**Purpose:** Monthly performance review

---

## 🧠 **Token Intelligence** {#token-intelligence}

### `/tokenleader`
**Description:** Most profitable tokens community-wide  
**Database Query:** Groups all trades by ticker  
**Calculations:**
```sql
SELECT ticker, SUM(profit_usd) as total_profit, COUNT(*) as total_trades,
COUNT(DISTINCT username) as trader_count
FROM pnls GROUP BY ticker ORDER BY total_profit DESC
```
**Purpose:** Identifies best performing tokens

### `/tokenstats TICKER`
**Description:** Deep analysis of specific token  
**Database Query:** Filters all trades for specified ticker  
**Calculations:**
- **Total Profit:** `SUM(profit_usd)`
- **Success Rate:** `(profitable_trades / total_trades) * 100`
- **Average Profit:** `total_profit / trade_count`
- **Best Trade:** `MAX(profit_usd)`
- **Worst Trade:** `MIN(profit_usd)`
- **Trader Count:** `COUNT(DISTINCT username)`
**Purpose:** Token-specific investment research

### `/trendingcoins`
**Description:** Most actively traded tokens (last 7 days)  
**Database Query:** Trade count by ticker in recent days  
**Calculation:** Filters by `timestamp >= (now - 7 days)`, groups by ticker  
**Purpose:** Identifies current market focus

### `/profitability TICKER`
**Description:** Token success rates and profitability metrics  
**Database Query:** Comprehensive token analysis  
**Calculations:**
- **Profitability Score:** Weighted average of success rate and profit
- **Risk Assessment:** Standard deviation of returns
- **Trader Adoption:** Unique trader count
**Purpose:** Investment decision support

---

## 💎 **Advanced Rankings** {#advanced-rankings}

### `/roi`
**Description:** Best percentage returns (ROI leaders)  
**Database Query:** Groups by username with ROI calculation  
**Calculation:**
```sql
SELECT username, (SUM(profit_usd) / SUM(initial_investment)) * 100 as roi_percentage
FROM pnls WHERE initial_investment > 0 GROUP BY username ORDER BY roi_percentage DESC
```
**Purpose:** Identifies most efficient traders

### `/bigballer` (Whale Leaderboard)
**Description:** Highest investment amounts  
**Database Query:** Groups by username  
**Calculations:**
- **Max Investment:** `MAX(initial_investment)`
- **Total Investment:** `SUM(initial_investment)`
- **Average Investment:** `AVG(initial_investment)`
**Purpose:** Tracks high-stakes traders

### `/percentking`
**Description:** Best single-trade percentage gains  
**Database Query:** Individual trades with percentage calculation  
**Calculation:**
```sql
SELECT *, (profit_usd / initial_investment) * 100 as percent_gain
FROM pnls WHERE initial_investment > 0 ORDER BY percent_gain DESC
```
**Purpose:** Celebrates exceptional individual performances

### `/consistenttrader`
**Description:** Most reliable traders (high win rate + multiple trades)  
**Database Query:** Traders with minimum 3 trades  
**Calculations:**
- **Consistency Score:** `(win_rate * trade_count_weight)`
- **Win Rate:** `(winning_trades / total_trades) * 100`
- **Minimum Trades:** Filter for `trade_count >= 3`
**Purpose:** Identifies steady, reliable performers

### `/lossleader`
**Description:** Transparency board - biggest losses  
**Database Query:** Individual losing trades  
**Calculation:** `WHERE profit_usd < 0 ORDER BY profit_usd ASC`  
**Purpose:** Promotes honesty and learning from losses

### `/smallcap`, `/midcap`, `/largecap`
**Description:** Investment-size filtered leaderboards  
**Database Queries:** Filtered by investment ranges  
**Calculations:**
- **Small Cap:** `initial_investment < $100`
- **Mid Cap:** `$100 <= initial_investment <= $1000`
- **Large Cap:** `initial_investment > $1000`
**Purpose:** Fair competition across investment sizes

---

## 🔍 **Search & Discovery** {#search-discovery}

### `/search TICKER`
**Description:** Find all trades for specific token  
**Database Query:** `WHERE ticker = 'SPECIFIED_TICKER'`  
**Calculation:** Returns all matching trades with profit details  
**Purpose:** Token-specific trade research

### `/finduser @username`
**Description:** Search specific user's trading history  
**Database Query:** `WHERE username = 'SPECIFIED_USER'`  
**Calculation:** User's recent trades with performance metrics  
**Purpose:** User research and learning

### `/topgainer [period]`
**Description:** Best performer in specified timeframe  
**Database Query:** Filtered by period (today/week/month)  
**Calculation:** Highest percentage gain in specified period  
**Purpose:** Identifies recent high performers

### `/todaysbiggest`
**Description:** Today's biggest winner  
**Database Query:** `WHERE date = today ORDER BY profit_usd DESC LIMIT 1`  
**Calculation:** Single highest profit trade today  
**Purpose:** Daily celebration and motivation

---

## 🎮 **Achievements & Gamification** {#achievements}

### `/achievements`
**Description:** Personal trading badges and milestones  
**Database Query:** User's stats analyzed against achievement thresholds  
**Calculations:**
- **Trade Volume Badges:** 1, 10, 50, 100+ trades
- **Profit Badges:** $100, $1K, $10K+ profit
- **Win Rate Badges:** 50%+, 75%+, 90%+ win rates
- **Streak Badges:** Consecutive wins
**Purpose:** Gamification and motivation

### `/streaks`
**Description:** Current and best winning/losing streaks  
**Database Query:** User's trades ordered by timestamp  
**Calculation:** Analyzes consecutive profitable/unprofitable trades  
**Purpose:** Momentum tracking and psychological insights

### `/milestones`
**Description:** Progress towards next achievements  
**Database Query:** Current stats vs. next thresholds  
**Calculation:** Percentage completion to next badge level  
**Purpose:** Goal setting and motivation

### `/randomtrade`
**Description:** Random successful trade for inspiration  
**Database Query:** `WHERE profit_usd > 0 ORDER BY RANDOM() LIMIT 1`  
**Calculation:** Randomly selected profitable trade  
**Purpose:** Inspiration and strategy learning

---

## 📊 **Market Intelligence** {#market-intelligence}

### `/marketsentiment`
**Description:** Community-wide trading mood analysis  
**Database Query:** Recent trades analyzed  
**Calculations:**
- **Bullish Sentiment:** `profitable_trades_percentage`
- **Trading Activity:** Recent trade volume trends
- **Popular Tokens:** Most traded tickers
**Purpose:** Market psychology insights

### `/popularityindex`
**Description:** Token popularity rankings  
**Database Query:** Trade frequency by token  
**Calculation:**
```sql
SELECT ticker, COUNT(*) as trade_count, COUNT(DISTINCT username) as trader_count
FROM pnls GROUP BY ticker ORDER BY trade_count DESC
```
**Purpose:** Identifies community favorites

### `/timetrendz`
**Description:** Best trading times and patterns  
**Database Query:** Trades grouped by time periods  
**Calculations:**
- **Hourly Performance:** Average profit by hour
- **Daily Performance:** Average profit by day of week
- **Monthly Trends:** Seasonal performance patterns
**Purpose:** Timing optimization strategies

### `/hall_of_fame`
**Description:** All-time legends and record holders  
**Database Query:** Multiple queries for various records  
**Calculations:**
- **Highest Single Profit**
- **Best ROI**
- **Most Trades**
- **Longest Win Streak**
- **Biggest Comeback**
**Purpose:** Celebrates exceptional achievements

---

## 🌌 **Community Overview** {#community-overview}

### `/loretotalprofit`
**Description:** Total combined profit across ALL individual trades  
**Database Query:** Aggregates every single trade in database  
**Calculations:**
```sql
SELECT 
  SUM(profit_usd) as total_profit_usd,
  SUM(profit_sol) as total_profit_sol,
  COUNT(*) as total_trades,
  SUM(initial_investment) as total_investment,
  COUNT(DISTINCT username) as trader_count,
  COUNT(DISTINCT ticker) as token_count,
  SUM(CASE WHEN profit_usd > 0 THEN 1 ELSE 0 END) as winning_trades,
  SUM(CASE WHEN profit_usd < 0 THEN 1 ELSE 0 END) as losing_trades,
  (SUM(profit_usd) / SUM(initial_investment)) * 100 as overall_roi,
  (SUM(CASE WHEN profit_usd > 0 THEN 1 ELSE 0 END) / COUNT(*)) * 100 as win_rate
FROM pnls
```
**Advanced Calculations:**
- **Overall ROI:** Total profit divided by total investment
- **Community Win Rate:** Percentage of all trades that were profitable
- **Real-time SOL Value:** Current SOL profits converted to USD
**Purpose:** Complete community financial overview

---

## 🔧 **Utility Commands** {#utility}

### `/filters`
**Description:** Complete command list with categories  
**Calculation:** None  
**Purpose:** Quick reference guide to all available commands

### `/lore`
**Description:** Opens Lore.trade platform within Telegram  
**Calculation:** None  
**Purpose:** Direct access to trading platform

### `/export` *(Moderators Only)*
**Description:** Export all community data to Excel  
**Database Query:** `SELECT * FROM pnls`  
**Calculations:**
- **Data Formatting:** Converts all data to Excel format
- **UK Date Formatting:** Ensures dd/mm/yyyy format
- **SOL Precision:** 3 decimal places for SOL amounts
**Purpose:** Data backup and advanced analysis

---

## 📊 **Mathematical Foundations**

### **Core Calculations Used Throughout**

#### **ROI (Return on Investment)**
```
ROI = (Total Profit / Total Investment) × 100
```
- Used in: `/roi`, `/mystats`, `/loretotalprofit`
- Measures efficiency of capital usage

#### **Win Rate**
```
Win Rate = (Profitable Trades / Total Trades) × 100
```
- Used in: All leaderboards, personal stats
- Measures trading success consistency

#### **Percentage Gain (Individual Trade)**
```
Percentage Gain = (Profit / Initial Investment) × 100
```
- Used in: `/percentking`, trade displays
- Measures individual trade performance

#### **Average Profit**
```
Average Profit = Total Profit / Number of Trades
```
- Used in: `/mystats`, token analysis
- Measures typical trade performance

#### **Success Rate (Token-Specific)**
```
Success Rate = (Profitable Token Trades / Total Token Trades) × 100
```
- Used in: `/tokenstats`, token analysis
- Measures token reliability

### **Data Integrity Features**

1. **Timezone Handling:** All dates stored and displayed in UTC, converted to UK format (dd/mm/yyyy)
2. **Currency Precision:** USD to 2 decimals, SOL to 3 decimals consistently
3. **Username Normalization:** All usernames standardized with single @ prefix
4. **Aggregation Accuracy:** All calculations verified with manual cross-checks
5. **Real-time Rates:** SOL/USD conversion using live market data

### **Database Optimizations**

- **Grouped Aggregations:** Efficient MongoDB pipelines for complex calculations
- **Indexed Queries:** Fast lookups on username, ticker, and timestamp fields
- **Memory Management:** Paginated results for large datasets
- **Error Handling:** Graceful fallbacks for all calculations

---

## 🎯 **Command Categories Summary**

| Category | Commands | Purpose |
|----------|----------|---------|
| **Getting Started** | 3 commands | Onboarding and help |
| **Submission** | 2 commands | Trade entry |
| **Leaderboards** | 6 commands | Competition rankings |
| **Personal Analytics** | 5 commands | Individual performance |
| **Token Intelligence** | 4 commands | Token research |
| **Advanced Rankings** | 8 commands | Specialized leaderboards |
| **Search & Discovery** | 4 commands | Data exploration |
| **Achievements** | 4 commands | Gamification |
| **Market Intelligence** | 4 commands | Community insights |
| **Community Overview** | 1 command | Total community stats |
| **Utility** | 3 commands | Tools and access |

**Total: 44+ Commands** providing comprehensive trading analytics and community engagement.

---

*Last Updated: January 3, 2025*  
*All calculations verified for 100% accuracy*  
*Compatible with MongoDB aggregation pipelines* 