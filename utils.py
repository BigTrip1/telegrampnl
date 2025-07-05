"""
Utility functions for the Telegram PNL Bot
"""

import requests
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple
import re

# Set up logging
logger = logging.getLogger(__name__)

# Import database manager for enhanced features
try:
    from database import db_manager
except ImportError:
    db_manager = None

class CurrencyConverter:
    def __init__(self, api_base: str = "https://api.coingecko.com/api/v3"):
        self.api_base = api_base
        self._cached_rate = None
        self._cache_time = None
        self._cache_duration = 300  # 5 minutes cache
    
    def get_sol_usd_rate(self) -> Optional[float]:
        """Get current SOL/USD exchange rate with caching"""
        try:
            # Check if we have a valid cached rate
            if (self._cached_rate and self._cache_time and 
                (datetime.now() - self._cache_time).seconds < self._cache_duration):
                return self._cached_rate
            
            # Fetch new rate
            url = f"{self.api_base}/simple/price?ids=solana&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            rate = data['solana']['usd']
            
            # Cache the rate
            self._cached_rate = rate
            self._cache_time = datetime.now()
            
            logger.info(f"Updated SOL/USD rate: ${rate}")
            return rate
            
        except Exception as e:
            logger.error(f"Error fetching SOL/USD rate: {e}")
            # Return cached rate if available, otherwise default
            return self._cached_rate if self._cached_rate else 100.0
    
    def usd_to_sol(self, usd_amount: float) -> float:
        """Convert USD to SOL equivalent"""
        rate = self.get_sol_usd_rate()
        return usd_amount / rate if rate else usd_amount / 100.0
    
    def sol_to_usd(self, sol_amount: float) -> float:
        """Convert SOL to USD equivalent"""
        rate = self.get_sol_usd_rate()
        return sol_amount * rate if rate else sol_amount * 100.0


class DateHelper:
    @staticmethod
    def get_current_week_range() -> Tuple[datetime, datetime]:
        """Get start and end of current week (Monday to Sunday)"""
        now = datetime.now(timezone.utc)
        start_of_week = now - timedelta(days=now.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = start_of_week + timedelta(days=7)
        return start_of_week, end_of_week
    
    @staticmethod
    def get_today_range() -> Tuple[datetime, datetime]:
        """Get start and end of today"""
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        return start_of_day, end_of_day
    
    @staticmethod
    def get_current_month_year() -> Tuple[int, int]:
        """Get current month and year"""
        now = datetime.now(timezone.utc)
        return now.year, now.month


class MessageFormatter:
    @staticmethod
    def format_date_uk(date_value) -> str:
        """Format datetime to UK format (dd/mm/yyyy)"""
        if date_value is None:
            return "N/A"
        return date_value.strftime("%d/%m/%Y")
    
    @staticmethod
    def format_date_uk_short(date_value) -> str:
        """Format datetime to UK short format (dd/mm)"""
        if date_value is None:
            return "N/A"
        return date_value.strftime("%d/%m")
    
    @staticmethod
    def format_date_uk_with_time(date_value) -> str:
        """Format datetime to UK format with time (dd/mm/yyyy HH:MM UTC)"""
        if date_value is None:
            return "N/A"
        return date_value.strftime("%d/%m/%Y %H:%M UTC")
    
    @staticmethod
    def format_leaderboard_message(title: str, leaders: list, currency_converter: CurrencyConverter) -> str:
        """Format leaderboard data into a readable message"""
        if not leaders:
            return f"🏆 **{title}**\n\nNo data available yet. Start trading to see the leaderboard!"
        
        message = f"🏆 **{title}**\n\n"
        
        for i, leader in enumerate(leaders, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            username = leader.get('username', f"User {leader['_id']}")
            usd_profit = leader.get('total_profit_usd', 0)
            sol_profit = leader.get('total_profit_sol', 0)
            
            # Format currency values
            usd_str = f"${usd_profit:,.2f}" if usd_profit >= 0 else f"-${abs(usd_profit):,.2f}"
            sol_str = f"{sol_profit:.3f} SOL" if sol_profit >= 0 else f"-{abs(sol_profit):.3f} SOL"
            
            message += f"{emoji} **{username}**\n"
            message += f"   💰 {usd_str} | {sol_str}\n"
            
            if 'trade_count' in leader:
                message += f"   📊 {leader['trade_count']} trades\n"
            message += "\n"
        
        return message
    
    @staticmethod
    def format_trade_leaderboard_message(title: str, leaders: list) -> str:
        """Format trade count leaderboard message"""
        if not leaders:
            return f"📊 **{title}**\n\nNo trades recorded yet!"
        
        message = f"📊 **{title}**\n\n"
        
        for i, leader in enumerate(leaders, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            username = leader.get('username', f"User {leader['_id']}")
            trade_count = leader.get('trade_count', 0)
            usd_profit = leader.get('total_profit_usd', 0)
            
            usd_str = f"${usd_profit:,.2f}" if usd_profit >= 0 else f"-${abs(usd_profit):,.2f}"
            
            message += f"{emoji} **{username}**\n"
            message += f"   🔢 {trade_count} trades | 💰 {usd_str}\n\n"
        
        return message
    
    @staticmethod
    def format_profit_goat_message(goat_data: dict) -> str:
        """Format profit GOAT message"""
        if not goat_data:
            return "🐐 **Profit GOAT**\n\nNo data available yet!"
        
        username = goat_data.get('username', f"User {goat_data['_id']}")
        usd_profit = goat_data.get('total_profit_usd', 0)
        sol_profit = goat_data.get('total_profit_sol', 0)
        trade_count = goat_data.get('trade_count', 0)
        
        usd_str = f"${usd_profit:,.2f}" if usd_profit >= 0 else f"-${abs(usd_profit):,.2f}"
        sol_str = f"{sol_profit:.3f} SOL" if sol_profit >= 0 else f"-{abs(sol_profit):.3f} SOL"
        
        message = f"🐐 **Profit GOAT** 🐐\n\n"
        message += f"👑 **{username}** is the ultimate profit champion!\n\n"
        message += f"💰 **Total Profit**: {usd_str} | {sol_str}\n"
        message += f"📊 **Total Trades**: {trade_count}\n"
        message += f"📈 **Average per Trade**: ${usd_profit/trade_count:,.2f}" if trade_count > 0 else ""
        
        return message
    
    @staticmethod
    def format_submission_message(user_data: dict, currency_converter: CurrencyConverter) -> str:
        """Format enhanced PNL submission message with achievements and community insights"""
        
        username = user_data.get('username', 'Unknown User')
        user_id = str(user_data.get('user_id', ''))
        ticker = user_data.get('ticker', 'N/A')
        initial_investment = user_data.get('initial_investment', 0)
        profit_usd = user_data.get('profit_usd', 0)
        profit_sol = user_data.get('profit_sol', 0)
        currency = user_data.get('currency', 'USD')
        timestamp = user_data.get('timestamp', datetime.now(timezone.utc))
        
        # Format currency values
        usd_str = f"${profit_usd:,.2f}" if profit_usd >= 0 else f"-${abs(profit_usd):,.2f}"
        sol_str = f"{profit_sol:.3f} SOL" if profit_sol >= 0 else f"-{abs(profit_sol):.3f} SOL"
        initial_str = f"${initial_investment:,.2f}" if currency == 'USD' else f"{initial_investment:.3f} SOL"
        
        # Calculate percentage return
        if initial_investment > 0:
            if currency == 'USD':
                return_pct = (profit_usd / initial_investment) * 100
            else:
                return_pct = (profit_sol / initial_investment) * 100
            return_str = f"{return_pct:+.2f}%"
        else:
            return_str = "N/A"
        
        # Choose emoji based on profit
        main_emoji = "🟢" if profit_usd > 0 else "🔴" if profit_usd < 0 else "⚪"
        
        # Start building the enhanced message
        message = f"{main_emoji} **PNL SUBMISSION** {main_emoji}\n\n"
        
        # Basic trade information
        message += f"👤 **Trader**: {username}\n"
        message += f"🎯 **Ticker**: {ticker}\n"
        message += f"💵 **Investment**: {initial_str}\n"
        message += f"💰 **Profit**: {usd_str} | {sol_str}\n"
        message += f"📊 **Return**: {return_str}\n"
        message += f"📅 **Date**: {MessageFormatter.format_date_uk_with_time(timestamp)}\n"
        
        # Get user's updated stats for achievements and insights
        try:
            if not db_manager:
                raise ImportError("Database manager not available")
            
            user_stats = db_manager.get_user_stats(user_id, username)
            if user_stats:
                # === ACHIEVEMENT-FOCUSED SECTION ===
                message += f"\n🏆 **ACHIEVEMENT STATUS** 🏆\n"
                
                # Check for new achievements
                achievements = db_manager.get_user_achievements(user_id, username)
                total_achievements = achievements.get('total_achievements', 0)
                
                # Show key achievements
                if total_achievements > 0:
                    recent_achievements = achievements.get('achievements', [])[-3:]  # Last 3 achievements
                    message += f"🎖️ **Badges**: {total_achievements} unlocked\n"
                    for achievement in recent_achievements:
                        message += f"   {achievement}\n"
                else:
                    message += f"🎯 **First Achievement**: {achievements.get('next_milestone', 'Keep trading!')}\n"
                
                # Streak information
                streaks = db_manager.get_user_streaks(user_id, username)
                current_streak = streaks.get('current_streak', 0)
                streak_type = streaks.get('streak_type', 'neutral')
                
                if current_streak > 0:
                    streak_emoji = "🔥" if streak_type == 'winning' else "😅"
                    message += f"{streak_emoji} **Current Streak**: {current_streak} {streak_type}\n"
                
                # Milestone progress
                milestones = db_manager.get_user_milestones(user_id, username)
                next_milestone = milestones.get('next_milestone', 'Keep trading!')
                progress = milestones.get('progress', 0)
                
                if progress > 0:
                    progress_bar = "▓" * int(progress / 10) + "▒" * (10 - int(progress / 10))
                    message += f"🎯 **Next Goal**: {next_milestone}\n"
                    message += f"📈 **Progress**: [{progress_bar}] {progress:.0f}%\n"
                
                # === DATA-HEAVY SECTION ===
                message += f"\n📊 **COMMUNITY INSIGHTS** 📊\n"
                
                # Personal performance metrics
                win_rate = user_stats.get('win_rate', 0)
                total_trades = user_stats.get('total_trades', 0)
                roi = user_stats.get('roi', 0)
                
                message += f"📈 **Your Stats**: {total_trades} trades | {win_rate:.1f}% win rate | {roi:+.1f}% ROI\n"
                
                # Community comparison
                try:
                    # Get leaderboard position (approximate)
                    all_leaders = db_manager.get_all_time_leaderboard(100)  # Get top 100
                    user_rank = None
                    for i, leader in enumerate(all_leaders, 1):
                        if leader.get('_id') == user_id or leader.get('username') == username:
                            user_rank = i
                            break
                    
                    if user_rank:
                        if user_rank <= 10:
                            message += f"🏆 **Community Rank**: #{user_rank} (TOP 10!) 👑\n"
                        elif user_rank <= 25:
                            message += f"🥇 **Community Rank**: #{user_rank} (TOP 25!) 🌟\n"
                        else:
                            message += f"📊 **Community Rank**: #{user_rank}\n"
                    
                    # Token performance insight
                    token_stats = db_manager.get_token_stats(ticker)
                    if token_stats:
                        token_success_rate = token_stats.get('success_rate', 0)
                        if token_success_rate > 60:
                            message += f"🎯 **{ticker} Intel**: {token_success_rate:.1f}% community success rate 🚀\n"
                        elif token_success_rate < 40:
                            message += f"⚠️ **{ticker} Intel**: {token_success_rate:.1f}% community success rate - risky pick!\n"
                        else:
                            message += f"📊 **{ticker} Intel**: {token_success_rate:.1f}% community success rate\n"
                    
                    # Performance tier
                    if return_pct > 100:
                        message += f"🚀 **Performance**: MOON SHOT! (+{return_pct:.0f}%)\n"
                    elif return_pct > 50:
                        message += f"🔥 **Performance**: EXCELLENT! (+{return_pct:.0f}%)\n"
                    elif return_pct > 0:
                        message += f"✅ **Performance**: Profitable (+{return_pct:.1f}%)\n"
                    elif return_pct < -50:
                        message += f"💎 **Performance**: Diamond hands test (-{abs(return_pct):.0f}%)\n"
                    else:
                        message += f"📉 **Performance**: Learning experience ({return_pct:.1f}%)\n"
                        
                except Exception as e:
                    logger.warning(f"Could not get community insights: {e}")
                    message += f"📊 **Community Data**: Loading...\n"
                    
        except Exception as e:
            logger.warning(f"Could not get user achievements/stats: {e}")
            # Fallback to basic message if achievements fail
            message += f"\n🎯 **Status**: Trade recorded successfully!\n"
        
        # Final motivational message
        message += f"\n✨ **Keep pushing your limits!** ✨\n"
        message += f"📈 Use `/mystats` to track progress | 🏆 `/leaderboard` for rankings"
        
        return message

    # ===== NEW MESSAGE FORMATTERS FOR ENHANCED FEATURES =====
    
    @staticmethod
    def format_user_stats_message(stats: dict, username: str) -> str:
        """Format user personal statistics"""
        if not stats:
            return f"📊 **{username}'s Trading Statistics**\n\nNo trading data found."
        
        message = f"📊 **{username}'s Trading Dashboard** 📊\n\n"
        
        # Basic stats
        message += f"📈 **Total Trades**: {stats.get('total_trades', 0)}\n"
        message += f"💰 **Total Profit**: ${stats.get('total_profit_usd', 0):,.2f}\n"
        message += f"💵 **Total Invested**: ${stats.get('total_investment', 0):,.2f}\n"
        message += f"🎯 **ROI**: {stats.get('roi', 0):.2f}%\n\n"
        
        # Win/Loss stats
        message += f"✅ **Winning Trades**: {stats.get('winning_trades', 0)}\n"
        message += f"❌ **Losing Trades**: {stats.get('losing_trades', 0)}\n"
        message += f"📊 **Win Rate**: {stats.get('win_rate', 0):.1f}%\n\n"
        
        # Performance stats
        message += f"🚀 **Best Trade**: ${stats.get('best_trade', 0):,.2f}\n"
        message += f"😅 **Worst Trade**: ${stats.get('worst_trade', 0):,.2f}\n"
        message += f"📈 **Average Profit**: ${stats.get('avg_profit', 0):.2f}\n\n"
        
        # Portfolio stats
        message += f"🎭 **Tokens Traded**: {stats.get('token_count', 0)}\n"
        
        return message
    
    @staticmethod
    def format_user_history_message(history: list, username: str) -> str:
        """Format user trading history"""
        if not history:
            return f"📈 **{username}'s Trading History**\n\nNo trades found."
        
        message = f"📈 **{username}'s Recent Trades** 📈\n\n"
        
        for i, trade in enumerate(history[:10], 1):  # Show last 10 trades
            profit = trade.get('profit_usd', 0)
            emoji = "🟢" if profit > 0 else "🔴" if profit < 0 else "⚪"
            
            message += f"{i}. {emoji} **{trade.get('ticker', 'N/A')}**\n"
            message += f"   💰 ${profit:,.2f}\n"
            
            if 'timestamp' in trade:
                date_str = MessageFormatter.format_date_uk(trade['timestamp'])
                message += f"   📅 {date_str}\n"
            message += "\n"
        
        if len(history) > 10:
            message += f"... and {len(history) - 10} more trades\n"
        
        return message
    
    @staticmethod
    def format_comparison_message(user1_stats: dict, user2_stats: dict, user1_name: str, user2_name: str) -> str:
        """Format trader comparison"""
        message = f"⚡ **Trader Comparison** ⚡\n\n"
        message += f"**{user1_name}** 🆚 **{user2_name}**\n\n"
        
        # Compare key metrics
        metrics = [
            ("Total Profit", "total_profit_usd", "$"),
            ("Total Trades", "total_trades", ""),
            ("Win Rate", "win_rate", "%"),
            ("ROI", "roi", "%"),
            ("Best Trade", "best_trade", "$"),
            ("Tokens Traded", "token_count", "")
        ]
        
        for metric_name, key, symbol in metrics:
            val1 = user1_stats.get(key, 0)
            val2 = user2_stats.get(key, 0)
            
            if symbol == "$":
                val1_str = f"${val1:,.2f}"
                val2_str = f"${val2:,.2f}"
            elif symbol == "%":
                val1_str = f"{val1:.1f}%"
                val2_str = f"{val2:.1f}%"
            else:
                val1_str = str(int(val1))
                val2_str = str(int(val2))
            
            winner = "🏆" if val1 > val2 else "" if val1 == val2 else "🏆"
            loser = "" if val1 >= val2 else "🏆"
            
            message += f"**{metric_name}**: {val1_str} {winner} vs {val2_str} {loser}\n"
        
        return message
    
    @staticmethod
    def format_roi_leaderboard_message(title: str, leaders: list) -> str:
        """Format ROI-based leaderboard"""
        if not leaders:
            return f"🚀 **{title}**\n\nNo data available yet."
        
        message = f"🚀 **{title}**\n\n"
        
        for i, leader in enumerate(leaders, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            username = leader.get('username', f"User {leader['_id']}")
            roi = leader.get('roi_percentage', 0)
            profit = leader.get('total_profit_usd', 0)
            trades = leader.get('trade_count', 0)
            
            message += f"{emoji} **{username}**\n"
            message += f"   🚀 ROI: {roi:+.2f}%\n"
            message += f"   💰 Profit: ${profit:,.2f} | 📊 {trades} trades\n\n"
        
        return message
    
    @staticmethod
    def format_token_leaderboard_message(tokens: list) -> str:
        """Format token leaderboard"""
        if not tokens:
            return "🎯 **Most Profitable Tokens**\n\nNo token data available."
        
        message = "🎯 **Most Profitable Tokens** 🎯\n\n"
        
        for i, token in enumerate(tokens, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            ticker = token.get('_id', 'N/A')
            profit = token.get('total_profit_usd', 0)
            trades = token.get('total_trades', 0)
            avg_profit = token.get('avg_profit', 0)
            traders = token.get('trader_count', 0)
            
            message += f"{emoji} **{ticker}**\n"
            message += f"   💰 Total: ${profit:,.2f}\n"
            message += f"   📊 {trades} trades | 👥 {traders} traders\n"
            message += f"   📈 Avg: ${avg_profit:.2f}\n\n"
        
        return message
    
    @staticmethod
    def format_token_stats_message(ticker: str, stats: dict) -> str:
        """Format detailed token statistics"""
        if not stats:
            return f"📊 **{ticker} Statistics**\n\nNo data found for {ticker}."
        
        message = f"📊 **{ticker} Detailed Stats** 📊\n\n"
        message += f"📈 **Total Trades**: {stats.get('total_trades', 0)}\n"
        message += f"💰 **Total Profit**: ${stats.get('total_profit_usd', 0):,.2f}\n"
        message += f"📊 **Success Rate**: {stats.get('success_rate', 0):.1f}%\n"
        message += f"👥 **Unique Traders**: {stats.get('trader_count', 0)}\n\n"
        
        message += f"🚀 **Best Trade**: ${stats.get('best_trade', 0):,.2f}\n"
        message += f"😅 **Worst Trade**: ${stats.get('worst_trade', 0):,.2f}\n"
        message += f"📈 **Average Profit**: ${stats.get('avg_profit', 0):.2f}\n"
        message += f"💵 **Total Investment**: ${stats.get('total_investment', 0):,.2f}\n"
        
        return message
    
    @staticmethod
    def format_trending_tokens_message(trending: list) -> str:
        """Format trending tokens message"""
        if not trending:
            return "🔥 **Trending Tokens**\n\nNo trending data available."
        
        message = "🔥 **Trending Tokens (7 days)** 🔥\n\n"
        
        for i, token in enumerate(trending, 1):
            emoji = "🔥" if i <= 3 else "📈"
            ticker = token.get('_id', 'N/A')
            trades = token.get('trade_count', 0)
            traders = token.get('trader_count', 0)
            profit = token.get('total_profit_usd', 0)
            
            message += f"{emoji} **{ticker}**\n"
            message += f"   📊 {trades} trades | 👥 {traders} traders\n"
            message += f"   💰 ${profit:,.2f} total profit\n\n"
        
        return message
    
    @staticmethod
    def format_whale_leaderboard_message(title: str, whales: list) -> str:
        """Format whale leaderboard"""
        if not whales:
            return f"🐋 **{title}**\n\nNo whale data available."
        
        message = f"🐋 **{title}** 🐋\n\n"
        
        for i, whale in enumerate(whales, 1):
            emoji = "🐋" if i == 1 else "🐳" if i == 2 else "🦈" if i == 3 else f"{i}."
            username = whale.get('username', f"User {whale['_id']}")
            max_invest = whale.get('max_investment', 0)
            total_invest = whale.get('total_investment', 0)
            trades = whale.get('trade_count', 0)
            
            message += f"{emoji} **{username}**\n"
            message += f"   💰 Biggest: ${max_invest:,.2f}\n"
            message += f"   📊 Total: ${total_invest:,.2f} | {trades} trades\n\n"
        
        return message
    
    @staticmethod
    def format_percent_leaderboard_message(title: str, leaders: list) -> str:
        """Format percentage gain leaderboard"""
        if not leaders:
            return f"👑 **{title}**\n\nNo data available."
        
        message = f"👑 **{title}** 👑\n\n"
        
        for i, leader in enumerate(leaders, 1):
            emoji = "👑" if i == 1 else "💎" if i == 2 else "🔥" if i == 3 else f"{i}."
            username = leader.get('username', f"User {leader['_id']}")
            percent_gain = leader.get('percent_gain', 0)
            profit = leader.get('profit_usd', 0)
            investment = leader.get('initial_investment', 0)
            ticker = leader.get('ticker', 'N/A')
            
            message += f"{emoji} **{username}**\n"
            message += f"   🚀 {percent_gain:+.2f}% | {ticker}\n"
            message += f"   💰 ${profit:,.2f} profit on ${investment:,.2f}\n\n"
        
        return message
    
    @staticmethod
    def format_consistency_leaderboard_message(title: str, traders: list) -> str:
        """Format consistency leaderboard"""
        if not traders:
            return f"🎯 **{title}**\n\nNo data available."
        
        message = f"🎯 **{title}** 🎯\n\n"
        
        for i, trader in enumerate(traders, 1):
            emoji = "🎯" if i == 1 else "🔥" if i == 2 else "💪" if i == 3 else f"{i}."
            username = trader.get('username', f"User {trader['_id']}")
            win_rate = trader.get('win_rate', 0)
            trades = trader.get('total_trades', 0)
            profit = trader.get('total_profit_usd', 0)
            
            message += f"{emoji} **{username}**\n"
            message += f"   🎯 {win_rate:.1f}% win rate\n"
            message += f"   📊 {trades} trades | 💰 ${profit:,.2f}\n\n"
        
        return message
    
    @staticmethod
    def format_loss_leaderboard_message(title: str, leaders: list) -> str:
        """Format loss leaderboard (transparency board)"""
        if not leaders:
            return f"😅 **{title}**\n\nNo loss data available."
        
        message = f"😅 **{title}** 😅\n\n"
        message += "🙏 Thank you for your transparency! Learning from losses makes us all better traders.\n\n"
        
        for i, leader in enumerate(leaders, 1):
            emoji = "😭" if i == 1 else "😔" if i == 2 else "😅" if i == 3 else f"{i}."
            username = leader.get('username', f"User {leader['_id']}")
            loss = abs(leader.get('profit_usd', 0))
            ticker = leader.get('ticker', 'N/A')
            
            message += f"{emoji} **{username}**\n"
            message += f"   💸 ${loss:,.2f} loss | {ticker}\n\n"
        
        return message
    
    @staticmethod
    def format_achievements_message(achievements: dict, username: str) -> str:
        """Format user achievements"""
        message = f"🏆 **{username}'s Achievements** 🏆\n\n"
        
        total = achievements.get('total_achievements', 0)
        if total == 0:
            message += "🎯 No achievements unlocked yet!\n"
            message += f"🎪 Next: {achievements.get('next_milestone', 'First Trade')}\n"
        else:
            message += f"🏆 **Total Achievements**: {total}\n\n"
            for achievement in achievements.get('achievements', []):
                message += f"🎖️ {achievement}\n"
        
        return message
    
    @staticmethod
    def format_streaks_message(streaks: dict, username: str) -> str:
        """Format user streaks"""
        message = f"🔥 **{username}'s Streaks** 🔥\n\n"
        
        current = streaks.get('current_streak', 0)
        streak_type = streaks.get('streak_type', 'neutral')
        
        if current > 0:
            emoji = "🔥" if streak_type == 'win' else "😅"
            message += f"{emoji} **Current Streak**: {current} {streak_type}s\n"
        else:
            message += "🎯 **Current Streak**: None\n"
        
        message += f"🏆 **Best Win Streak**: {streaks.get('longest_win_streak', 0)}\n"
        message += f"😅 **Longest Loss Streak**: {streaks.get('longest_loss_streak', 0)}\n"
        
        return message
    
    @staticmethod
    def format_milestones_message(milestones: dict, username: str) -> str:
        """Format user milestones"""
        message = f"🎯 **{username}'s Milestones** 🎯\n\n"
        
        completed = milestones.get('completed_milestones', [])
        if completed:
            message += "✅ **Completed**:\n"
            for milestone in completed:
                message += f"   🎖️ {milestone}\n"
            message += "\n"
        
        next_milestone = milestones.get('next_milestone', 'N/A')
        progress = milestones.get('progress', 0)
        
        message += f"🎪 **Next Goal**: {next_milestone}\n"
        message += f"📊 **Progress**: {progress}%\n"
        
        return message
    
    @staticmethod
    def format_random_trade_message(trade: dict) -> str:
        """Format random trade for inspiration"""
        username = trade.get('username', 'Anonymous')
        ticker = trade.get('ticker', 'N/A')
        profit = trade.get('profit_usd', 0)
        investment = trade.get('initial_investment', 0)
        
        roi = (profit / investment * 100) if investment > 0 else 0
        
        message = f"✨ **Trade Inspiration** ✨\n\n"
        message += f"💡 **Trader**: {username}\n"
        message += f"🎯 **Token**: {ticker}\n"
        message += f"💰 **Profit**: ${profit:,.2f}\n"
        message += f"📊 **ROI**: {roi:+.2f}%\n\n"
        message += "🚀 You can do it too! Keep trading!"
        
        return message
    
    @staticmethod
    def format_daily_winner_message(winner: dict) -> str:
        """Format daily biggest winner"""
        username = winner.get('username', 'Anonymous')
        ticker = winner.get('ticker', 'N/A')
        profit = winner.get('profit_usd', 0)
        investment = winner.get('initial_investment', 0)
        
        roi = (profit / investment * 100) if investment > 0 else 0
        
        message = f"🏆 **Today's Biggest Winner** 🏆\n\n"
        message += f"👑 **Champion**: {username}\n"
        message += f"🎯 **Token**: {ticker}\n"
        message += f"💰 **Profit**: ${profit:,.2f}\n"
        message += f"📊 **ROI**: {roi:+.2f}%\n\n"
        message += "🎉 Congratulations on the amazing trade!"
        
        return message
    
    @staticmethod
    def format_hall_of_fame_message(legends: list) -> str:
        """Format epic hall of fame with multiple legend categories"""
        if not legends:
            return """
🏛️ **HALL OF FAME** 🏛️

*The legends are still being written...*

🌟 **BECOME A LEGEND:**
📊 `/submit` - Add your trades
💰 `/profitbattle` - Prove your worth
⚔️ `/tradewar` - Show your dedication
🎯 `/mystats` - Track your progress

*Greatness awaits those who dare to trade!*
            """.strip()
        
        # Create the epic Hall of Fame header
        message = """
🏛️ **HALL OF FAME** 🏛️
*Where Trading Legends Are Born*

═══════════════════════════

🌟 **IMMORTAL LEGENDS OF LORE** 🌟

        """.strip()
        
        # Sort legends by rank for proper display
        sorted_legends = sorted(legends, key=lambda x: x.get('rank', 999))
        
        # Create legend entries
        for legend in sorted_legends:
            category = legend.get('category', 'Unknown Legend')
            username = legend.get('username', 'Anonymous')
            achievement = legend.get('achievement', 'Unknown')
            subtitle = legend.get('subtitle', '')
            description = legend.get('description', '')
            icon = legend.get('icon', '⭐')
            
            # Clean username (remove @ if present for display)
            display_username = username.replace('@', '') if username.startswith('@') else username
            
            message += f"\n\n{icon} **{category}**\n"
            message += f"👑 **@{display_username}**\n"
            message += f"🏆 **{achievement}**"
            
            if subtitle:
                message += f" | {subtitle}"
            
            if description:
                message += f"\n*{description}*"
        
        # Add footer with statistics and motivation
        message += f"""

═══════════════════════════

🎯 **HALL OF FAME STATISTICS:**
📊 **Active Legends:** {len(legends)}
🏆 **Categories:** {len(set(l.get('category', '') for l in legends))}
⚔️ **Total Achievements:** {len(legends)}

🌟 **BECOME THE NEXT LEGEND:**
💰 **Profit Emperor** - Dominate total profits
🚀 **ROI Deity** - Master percentage returns  
🐋 **Volume Titan** - Rule capital deployment
⚔️ **Trade Gladiator** - Command trading volume
🎯 **Precision Master** - Perfect your accuracy
🏛️ **Battle Emperor** - Conquer the colosseum
💥 **Single Trade Legend** - One epic trade

**🔥 QUICK ACTIONS:**
📊 `/mystats` - Check your potential
💰 `/profitbattle` - Battle for glory
⚔️ `/tradewar` - Prove your dedication
🏆 `/leaderboard` - See current rankings

*The Hall of Fame awaits your legend!*
        """.strip()
        
        return message
    
    @staticmethod
    def format_market_sentiment_message(sentiment: dict) -> str:
        """Format market sentiment analysis"""
        message = f"📊 **Community Market Sentiment** 📊\n\n"
        
        sentiment_emoji = sentiment.get('sentiment', 'Unknown 🤷')
        total_trades = sentiment.get('total_trades', 0)
        success_rate = sentiment.get('success_rate', 0)
        total_profit = sentiment.get('total_profit', 0)
        
        message += f"🎭 **Overall Sentiment**: {sentiment_emoji}\n"
        message += f"📊 **Weekly Trades**: {total_trades}\n"
        message += f"✅ **Success Rate**: {success_rate:.1f}%\n"
        message += f"💰 **Community P&L**: ${total_profit:,.2f}\n\n"
        
        if success_rate > 60:
            message += "🚀 The community is crushing it!"
        elif success_rate > 40:
            message += "⚖️ Mixed results, keep grinding!"
        else:
            message += "🛡️ Tough market, trade carefully!"
        
        return message
    
    @staticmethod
    def format_popularity_index_message(popularity: list) -> str:
        """Format token popularity index"""
        if not popularity:
            return "📈 **Token Popularity Index**\n\nNo data available."
        
        message = "📈 **Token Popularity Index** 📈\n\n"
        
        for i, token in enumerate(popularity, 1):
            ticker = token.get('_id', 'N/A')
            frequency = token.get('trade_frequency', 0)
            traders = token.get('trader_count', 0)
            score = token.get('popularity_score', 0)
            
            emoji = "🔥" if i <= 3 else "📈"
            message += f"{emoji} **{ticker}** (Score: {score})\n"
            message += f"   📊 {frequency} trades | 👥 {traders} traders\n\n"
        
        return message
    
    @staticmethod
    def format_profitability_message(ticker: str, profitability: dict) -> str:
        """Format token profitability analysis"""
        message = f"🎯 **{ticker} Profitability Analysis** 🎯\n\n"
        
        success_rate = profitability.get('success_rate', 0)
        total_trades = profitability.get('total_trades', 0)
        total_profit = profitability.get('total_profit', 0)
        avg_profit = profitability.get('avg_profit', 0)
        best = profitability.get('best_trade', 0)
        worst = profitability.get('worst_trade', 0)
        
        message += f"✅ **Success Rate**: {success_rate:.1f}%\n"
        message += f"📊 **Total Trades**: {total_trades}\n"
        message += f"💰 **Total Profit**: ${total_profit:,.2f}\n"
        message += f"📈 **Average Profit**: ${avg_profit:.2f}\n\n"
        message += f"🚀 **Best Trade**: ${best:,.2f}\n"
        message += f"😅 **Worst Trade**: ${worst:,.2f}\n\n"
        
        if success_rate > 70:
            message += "🏆 Highly profitable token!"
        elif success_rate > 50:
            message += "💎 Solid performer"
        else:
            message += "⚠️ High risk token"
        
        return message
    
    @staticmethod
    def format_time_trends_message(trends: dict) -> str:
        """Format time trends analysis"""
        message = f"⏰ **Trading Time Trends** ⏰\n\n"
        
        best_day = trends.get('best_day', 'Monday')
        best_hour = trends.get('best_hour', '10:00 AM')
        
        message += f"📅 **Best Trading Day**: {best_day}\n"
        message += f"🕐 **Best Trading Hour**: {best_hour}\n\n"
        message += "💡 **Tip**: Timing can impact your trading success!"
        
        return message
    
    @staticmethod
    def format_search_results_message(ticker: str, trades: list) -> str:
        """Format search results for ticker"""
        if not trades:
            return f"🔍 **Search Results for {ticker}**\n\nNo trades found."
        
        message = f"🔍 **{ticker} Trade History** 🔍\n\n"
        
        for i, trade in enumerate(trades[:10], 1):
            profit = trade.get('profit_usd', 0)
            username = trade.get('username', 'Anonymous')
            emoji = "🟢" if profit > 0 else "🔴" if profit < 0 else "⚪"
            
            message += f"{i}. {emoji} **{username}**\n"
            message += f"   💰 ${profit:,.2f}\n"
            
            if 'timestamp' in trade:
                date_str = MessageFormatter.format_date_uk(trade['timestamp'])
                message += f"   📅 {date_str}\n"
            message += "\n"
        
        return message
    
    @staticmethod
    def format_user_search_results_message(username: str, trades: list) -> str:
        """Format search results for user"""
        if not trades:
            return f"🔍 **@{username}'s Trades**\n\nNo trades found."
        
        message = f"🔍 **@{username}'s Trade History** 🔍\n\n"
        
        total_profit = sum(trade.get('profit_usd', 0) for trade in trades)
        message += f"💰 **Total Shown**: ${total_profit:,.2f}\n\n"
        
        for i, trade in enumerate(trades[:10], 1):
            profit = trade.get('profit_usd', 0)
            ticker = trade.get('ticker', 'N/A')
            emoji = "🟢" if profit > 0 else "🔴" if profit < 0 else "⚪"
            
            message += f"{i}. {emoji} **{ticker}**: ${profit:,.2f}\n"
        
        return message
    
    @staticmethod
    def format_top_gainer_message(gainer: dict, period: str) -> str:
        """Format top gainer message"""
        username = gainer.get('username', 'Anonymous')
        ticker = gainer.get('ticker', 'N/A')
        percent_gain = gainer.get('percent_gain', 0)
        profit = gainer.get('profit_usd', 0)
        
        message = f"🚀 **Top Gainer ({period.title()})** 🚀\n\n"
        message += f"👑 **Champion**: {username}\n"
        message += f"🎯 **Token**: {ticker}\n"
        message += f"📊 **Gain**: {percent_gain:+.2f}%\n"
        message += f"💰 **Profit**: ${profit:,.2f}\n\n"
        message += "🔥 Incredible performance!"
        
        return message
    
    @staticmethod
    def format_portfolio_message(portfolio: dict, username: str) -> str:
        """Format user portfolio diversification"""
        message = f"📊 **{username}'s Portfolio** 📊\n\n"
        
        total_tokens = portfolio.get('total_tokens', 0)
        total_profit = portfolio.get('total_profit', 0)
        diversification = portfolio.get('diversification_score', 0)
        
        message += f"🎭 **Tokens Traded**: {total_tokens}\n"
        message += f"💰 **Total Profit**: ${total_profit:,.2f}\n"
        message += f"📊 **Diversification Score**: {diversification}/100\n\n"
        
        tokens = portfolio.get('tokens', [])[:5]  # Top 5 tokens
        if tokens:
            message += "🏆 **Top Tokens**:\n"
            for token in tokens:
                ticker = token.get('_id', 'N/A')
                profit = token.get('total_profit', 0)
                trades = token.get('trade_count', 0)
                message += f"   🎯 {ticker}: ${profit:,.2f} ({trades} trades)\n"
        
        return message
    
    @staticmethod
    def format_monthly_report_message(report: dict, username: str) -> str:
        """Format monthly trading report"""
        message = f"📅 **{username}'s Monthly Report** 📅\n\n"
        
        trades = report.get('total_trades', 0)
        profit = report.get('total_profit', 0)
        investment = report.get('total_investment', 0)
        win_rate = report.get('win_rate', 0)
        roi = report.get('roi', 0)
        best = report.get('best_trade', 0)
        worst = report.get('worst_trade', 0)
        tokens = report.get('token_count', 0)
        
        message += f"📊 **Total Trades**: {trades}\n"
        message += f"💰 **Total Profit**: ${profit:,.2f}\n"
        message += f"💵 **Total Invested**: ${investment:,.2f}\n"
        message += f"📈 **ROI**: {roi:.2f}%\n"
        message += f"✅ **Win Rate**: {win_rate:.1f}%\n\n"
        
        message += f"🚀 **Best Trade**: ${best:,.2f}\n"
        message += f"😅 **Worst Trade**: ${worst:,.2f}\n"
        message += f"🎭 **Tokens Traded**: {tokens}\n\n"
        
        if profit > 0:
            message += "🎉 Profitable month! Keep it up!"
        else:
            message += "💪 Tough month, but every trader has them!"
        
        return message


class InputValidator:
    @staticmethod
    def validate_amount(amount_str: str) -> Optional[float]:
        """Validate and parse amount input - supports both profits (positive) and losses (negative)"""
        try:
            # Remove common currency symbols and spaces
            cleaned = re.sub(r'[$,\s]', '', amount_str.strip())
            amount = float(cleaned)
            
            # Check for reasonable bounds (allow negative for losses)
            if abs(amount) > 1000000:  # Reasonable upper limit for both profits and losses
                return None
                
            return amount
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_investment_amount(amount_str: str) -> Optional[float]:
        """Validate and parse investment amount input - must be positive"""
        try:
            # Remove common currency symbols and spaces
            cleaned = re.sub(r'[$,\s]', '', amount_str.strip())
            amount = float(cleaned)
            
            # Investments must be positive
            if amount <= 0:
                return None
            if amount > 1000000:  # Reasonable upper limit
                return None
                
            return amount
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_ticker(ticker_str: str) -> Optional[str]:
        """Validate ticker symbol input"""
        if not ticker_str or not isinstance(ticker_str, str):
            return None
        
        # Clean and validate ticker
        ticker = ticker_str.strip().upper()
        
        # Basic validation - alphanumeric and common symbols
        if not re.match(r'^[A-Z0-9/\-\.]{1,20}$', ticker):
            return None
            
        return ticker


# Global instances
currency_converter = CurrencyConverter()
date_helper = DateHelper()
message_formatter = MessageFormatter()
input_validator = InputValidator() 