"""
Main Telegram Bot for PNL Management
"""

import os
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
import pandas as pd
from io import BytesIO
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters
)
from telegram.constants import ParseMode

from database import db_manager
from utils import currency_converter, date_helper, message_formatter, input_validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
SCREENSHOT_UPLOAD, CURRENCY_SELECTION, TICKER_INPUT, INVESTMENT_INPUT, PROFIT_INPUT = range(5)
BATTLE_PLAYER_COUNT, BATTLE_DURATION, BATTLE_PARTICIPANTS, BATTLE_CONFIRMATION = range(4, 8)

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')  # Keep for backward compatibility
CHANNEL_IDS = [id.strip() for id in os.getenv('CHANNEL_IDS', '').split(',') if id.strip()]  # New multi-channel support
MODERATOR_IDS = [int(id.strip()) for id in os.getenv('MODERATOR_IDS', '').split(',') if id.strip()]

# Parse channel configurations (can include topic IDs)
def parse_channel_config(channel_config):
    """Parse channel configuration that may include topic IDs"""
    channels = []
    
    for config in (CHANNEL_IDS if CHANNEL_IDS else ([CHANNEL_ID] if CHANNEL_ID else [])):
        if not config:
            continue
            
        # Check if it includes a topic ID (format: channel_id:topic_id)
        if ':' in config:
            channel_id, topic_id = config.split(':', 1)
            channels.append({
                'id': channel_id.strip(),
                'topic_id': int(topic_id.strip()) if topic_id.strip().isdigit() else None
            })
        else:
            channels.append({
                'id': config.strip(),
                'topic_id': None
            })
    
    return channels

CHANNELS_TO_POST = parse_channel_config(CHANNEL_IDS if CHANNEL_IDS else ([CHANNEL_ID] if CHANNEL_ID else []))

class TelegramPNLBot:
    def __init__(self):
        self.application = None
        self.user_sessions = {}  # Store user session data
        self.battle_sessions = {}  # Store battle session data
    
    async def start_command(self, update: Update, context) -> None:
        """Handle /start command"""
        welcome_message = """
🚀 **Welcome to the Ultimate Trading Analytics Bot!** 🚀

Transform your trading experience with professional-grade community intelligence. This isn't just a PNL tracker - it's your complete trading analytics platform.

🎯 **GET STARTED (MOBILE OPTIMIZED):**
📱 **SUPER EASY:** Just upload any screenshot! I'll ask if you want to submit it as PNL
📊 `/submit` - Traditional submission process  
❓ `/help` - Complete command guide & tutorial
🚫 `/cancel` - Cancel any ongoing process

🏆 **LEADERBOARDS & COMPETITION:**
📈 `/leaderboard` - All-time profit champions
📅 `/monthlyleaderboard` - This month's top performers
📆 `/weeklyleaderboard` - This week's winners
📋 `/dailyleaderboard` - Today's leaders
🔢 `/tradeleader` - Most active traders
🐐 `/profitgoat` - Highest single profit holder

💡 **YOUR PERSONAL ANALYTICS:**
📊 `/mystats` - Complete trading dashboard
📚 `/myhistory` - Your trading journey
⚖️ `/compare @username` - Head-to-head analysis
🎯 `/portfolio` - Token diversification insights

🧠 **TOKEN INTELLIGENCE:**
🏅 `/tokenleader` - Most profitable tokens
🔍 `/tokenstats TICKER` - Deep token analysis
📈 `/trendingcoins` - What's hot right now

🎮 **ACHIEVEMENTS & GAMIFICATION:**
🏆 `/achievements` - Unlock trading badges
🔥 `/streaks` - Track your winning runs
🎯 `/milestones` - Progress tracking
🎪 `/randomtrade` - Get inspired by epic wins

💰 **ADVANCED LEADERBOARDS:**
💎 `/roi` - Best percentage returns
🐋 `/bigballer` - Whale tracker
👑 `/percentking` - Biggest gains
🎯 `/consistenttrader` - Most reliable traders

🔍 **SEARCH & DISCOVERY:**
🔎 `/search TICKER` - Find trades by token
👤 `/finduser @username` - User's trading history
📊 `/topgainer` - Best performers by period

🌐 **COMMUNITY OVERVIEW:**
🌌 `/loretotalprofit` - View total community profit & stats
🚀 `/lore` - Open Lore.trade platform within Telegram

Ready to join the elite? Start with `/submit` for your first clean PNL post!
Type `/help` to master all 40+ commands and unlock your trading potential.
        """
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
        await self.clean_command_message(update, context)
    
    async def help_command(self, update: Update, context) -> None:
        """Show comprehensive help guide"""
        help_message = f"""
🏆 **LORE PNL TRADING BOT - COMPLETE COMMAND LIST** 🏆

**🎯 QUICK START:**
• `/submit` - Submit your trade (screenshot required)
• `/mystats` - View your trading statistics
• `/leaderboard` - See community rankings

**📊 CORE COMMANDS:**
• `/submit` - Submit trade with screenshot
• `/mystats` - Your personal trading stats
• `/leaderboard` - Community leaderboard (Top 10)
• `/fullboard` - Complete leaderboard (All traders)
• `/achievements` - View your trading achievements
• `/loretotalprofit` - Community total profit stats

**🔥 BATTLE SYSTEM:**
⚔️ `/profitbattle` - Start profit battles
⚡ `/tradewar` - Start trade count wars
🏆 `/battlerules` - Complete battle guide
📊 `/battlpoints` - Your battle points & record
🎖️ `/battleleaderboard` - Hall of battle champions

**📈 ANALYSIS & INSIGHTS:**
• `/analysis` - Advanced trading analysis
• `/insights` - Market insights and trends
• `/sentiment` - Weekly sentiment analysis
• `/profitability` - Profitability analysis
• `/tokenanalysis` - Token performance analysis
• `/compare` - Compare trader performance

**🎯 SPECIALIZED COMMANDS:**
• `/topprofits` - Highest profit trades
• `/topperformers` - Top performing traders
• `/weeklyreport` - Weekly trading report
• `/monthlyreport` - Monthly trading report
• `/filters` - Set custom leaderboard filters
• `/recenttrades` - View recent community trades

**🏆 LEADERBOARD VARIATIONS:**
• `/leaderboard` - Standard top 10
• `/fullboard` - Complete rankings
• `/weeklyboard` - Weekly leaderboard
• `/monthlyboard` - Monthly leaderboard
• `/battleleaderboard` - Battle champions

**🎮 BATTLE COMMANDS:**
• `/profitbattle` - Profit competition battles
• `/tradewar` - Trade count competition wars
• `/battlerules` - Battle system guide
• `/battlpoints` - Your battle statistics
• `/battleleaderboard` - Battle hall of fame

**💡 TIPS:**
• Screenshots are required for all trades
• Use `/mystats` to track your progress
• Join battles to earn battle points
• Check `/achievements` for milestones
• Use analysis commands for insights

**🚀 PREMIUM FEATURES:**
Hold LORE tokens for exclusive benefits!
• Advanced analytics
• Priority support
• Premium insights
• VIP community access

**Token:** G2AbNxcyXV6QiXptMm6MuQPBDJYp9AVQHTdWAV1Wpump
**Access:** https://lore.trade/access

Ready to dominate the markets? Start with `/submit` to log your first trade! 📈
        """
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
        await self.clean_command_message(update, context)
    
    async def submit_command(self, update: Update, context) -> int:
        """Start PNL submission process"""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name or f"User{user_id}"
        
        # Initialize user session
        self.user_sessions[user_id] = {
            'user_id': user_id,
            'username': username,
            'timestamp': datetime.now(timezone.utc),
            'messages_to_delete': []  # Track messages to delete later
        }
        
        # Store the command message for deletion
        self.user_sessions[user_id]['messages_to_delete'].append(update.message.message_id)
        
        # Ask for screenshot first
        message = await update.message.reply_text(
            "📸 **PNL Submission** 📸\n\n"
            "First, upload a screenshot of your trade as proof:",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Store this message for deletion
        self.user_sessions[user_id]['messages_to_delete'].append(message.message_id)
        
        return SCREENSHOT_UPLOAD
    
    async def currency_selection_callback(self, update: Update, context) -> int:
        """Handle currency selection"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        currency = query.data.split("_")[1]  # Extract USD or SOL
        
        # Store currency selection
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['currency'] = currency
        
        currency_symbol = "💵" if currency == "USD" else "◎"
        await query.edit_message_text(
            f"✅ **Currency:** {currency_symbol} {currency}\n\n"
            f"🎯 **Step 2:** Enter TICKER\n"
            f"_(e.g. BONK, WIF, PEPE)_",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # The message is already tracked from previous step since it's an edit
        
        return TICKER_INPUT
    
    async def ticker_input(self, update: Update, context) -> int:
        """Handle ticker input"""
        user_id = update.effective_user.id
        ticker_text = update.message.text.strip()
        
        # Store this message for deletion
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['messages_to_delete'].append(update.message.message_id)
        
        # Validate ticker
        ticker = input_validator.validate_ticker(ticker_text)
        if not ticker:
            message = await update.message.reply_text(
                "❌ **Invalid ticker**\n\nTry: BTC, ETH, DOGE, etc."
            )
            # Store message for deletion
            if user_id in self.user_sessions:
                self.user_sessions[user_id]['messages_to_delete'].append(message.message_id)
            return TICKER_INPUT
        
        # Store ticker
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['ticker'] = ticker
        
        currency = self.user_sessions[user_id].get('currency', 'USD')
        currency_symbol = "💵" if currency == "USD" else "◎"
        
        message = await update.message.reply_text(
            f"✅ **Ticker:** {ticker}\n\n"
            f"💵 **Step 3:** Investment amount in {currency_symbol} {currency}",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Store this message for deletion
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['messages_to_delete'].append(message.message_id)
        
        return INVESTMENT_INPUT
    
    async def investment_input(self, update: Update, context) -> int:
        """Handle initial investment input"""
        user_id = update.effective_user.id
        investment_text = update.message.text.strip()
        
        # Store this message for deletion
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['messages_to_delete'].append(update.message.message_id)
        
        # Validate investment amount (must be positive)
        investment = input_validator.validate_investment_amount(investment_text)
        if investment is None:
            message = await update.message.reply_text(
                "❌ **Invalid investment amount**\n\nInvestments must be positive numbers.\nTry: 100, 250.50, etc."
            )
            # Store message for deletion
            if user_id in self.user_sessions:
                self.user_sessions[user_id]['messages_to_delete'].append(message.message_id)
            return INVESTMENT_INPUT
        
        # Store investment
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['initial_investment'] = investment
        
        currency = self.user_sessions[user_id].get('currency', 'USD')
        currency_symbol = "💵" if currency == "USD" else "◎"
        
        # Format investment amount based on currency
        if currency == 'USD':
            investment_str = f"{investment:,.2f}"
        else:  # SOL
            investment_str = f"{investment:.3f}"
        
        message = await update.message.reply_text(
            f"✅ **Investment:** {currency_symbol} {investment_str}\n\n"
            f"💰 **Step 4:** Profit in {currency_symbol} {currency}\n"
            f"_(use negative for losses)_",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Store this message for deletion
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['messages_to_delete'].append(message.message_id)
        
        return PROFIT_INPUT
    
    async def profit_input(self, update: Update, context) -> int:
        """Handle profit input and complete submission"""
        user_id = update.effective_user.id
        profit_text = update.message.text.strip()
        
        # Store this message for deletion
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['messages_to_delete'].append(update.message.message_id)
        
        # Validate profit amount
        profit = input_validator.validate_amount(profit_text)
        if profit is None:
            message = await update.message.reply_text(
                "❌ **Invalid amount**\n\nTry: 50, -25.5, etc."
            )
            # Store message for deletion
            if user_id in self.user_sessions:
                self.user_sessions[user_id]['messages_to_delete'].append(message.message_id)
            return PROFIT_INPUT
        
        # Store profit and calculate conversions for both profit and investment
        currency = self.user_sessions[user_id].get('currency', 'USD')
        initial_investment = self.user_sessions[user_id].get('initial_investment', 0)
        
        if currency == 'USD':
            profit_usd = profit
            profit_sol = currency_converter.usd_to_sol(profit)
            investment_usd = initial_investment
            investment_sol = currency_converter.usd_to_sol(initial_investment)
        else:  # SOL
            profit_sol = profit
            profit_usd = currency_converter.sol_to_usd(profit)
            investment_sol = initial_investment
            investment_usd = currency_converter.sol_to_usd(initial_investment)
        
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['profit_usd'] = profit_usd
            self.user_sessions[user_id]['profit_sol'] = profit_sol
            self.user_sessions[user_id]['investment_usd'] = investment_usd
            self.user_sessions[user_id]['investment_sol'] = investment_sol
        
        # Complete the submission
        await self.complete_submission(update, context)
        
        return ConversationHandler.END
    
    async def screenshot_upload(self, update: Update, context) -> int:
        """Handle screenshot upload at the beginning"""
        user_id = update.effective_user.id
        
        if not update.message.photo:
            message = await update.message.reply_text(
                "❌ Please upload a screenshot image:"
            )
            # Store message for deletion
            if user_id in self.user_sessions:
                self.user_sessions[user_id]['messages_to_delete'].append(message.message_id)
            return SCREENSHOT_UPLOAD
        
        # Store the screenshot message for deletion
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['messages_to_delete'].append(update.message.message_id)
        
        # Get the highest resolution photo
        photo = update.message.photo[-1]
        
        # Store screenshot in session
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['screenshot'] = photo.file_id
        
        # Create currency selection keyboard
        keyboard = [
            [InlineKeyboardButton("💵 USD", callback_data="currency_USD")],
            [InlineKeyboardButton("◎ SOL", callback_data="currency_SOL")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = await update.message.reply_text(
            "✅ Screenshot received!\n\n💰 Now select the currency for your profit:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Store this message for deletion
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['messages_to_delete'].append(message.message_id)
        
        return CURRENCY_SELECTION
    
    async def photo_auto_detect(self, update: Update, context) -> None:
        """Auto-detect photo/image uploads and ask if user wants to submit as PNL - Mobile Optimized"""
        user_id = update.effective_user.id
        chat_type = update.effective_chat.type
        chat_id = update.effective_chat.id
        message_thread_id = getattr(update.message, 'message_thread_id', None)
        
        # Debug logging to help troubleshoot group issues
        logger.info(f"🔍 PHOTO DETECTED: User {user_id} in chat {chat_id} (type: {chat_type}) topic: {message_thread_id}")
        
        # RESTRICTION: Only work in PnLs topic (11248) - ignore photos in other channels/topics
        PNLS_TOPIC_ID = 11248
        PNLS_CHANNEL_ID = -1002529018762
        
        # Check if we're in the correct channel and topic
        if chat_id == PNLS_CHANNEL_ID:
            if message_thread_id != PNLS_TOPIC_ID:
                logger.info(f"🚫 Photo in wrong topic ({message_thread_id}), PnL detection only works in topic {PNLS_TOPIC_ID}")
                return  # Ignore photos not in PnLs topic
        else:
            # Not in the PnLs channel at all - could be private chat or different channel
            if chat_type in ['group', 'supergroup']:
                logger.info(f"🚫 Photo in different channel ({chat_id}), PnL detection only works in channel {PNLS_CHANNEL_ID} topic {PNLS_TOPIC_ID}")
                return  # Ignore photos in other channels
            else:
                logger.info(f"💬 Processing private photo upload - allowing PnL detection")
                # Allow private chats for testing/direct submissions
        
        # Add group-specific handling for better UX
        if chat_type in ['group', 'supergroup']:
            logger.info(f"📱 Processing PnLs topic photo upload in {chat_type}: {chat_id}")
        else:
            logger.info(f"💬 Processing private photo upload")
        
        # Skip if user is already in a submission process
        if user_id in self.user_sessions:
            session = self.user_sessions[user_id]
            if not session.get('auto_detect_mode', False):
                return  # User is in active submission, don't interfere
        
        # Get file_id from photo or document (mobile compatibility)
        file_id = None
        image_type = "unknown"
        
        if update.message.photo:
            # Regular photo (most common)
            file_id = update.message.photo[-1].file_id
            image_type = "photo"
            logger.info(f"📸 Regular photo detected: {file_id}")
        elif update.message.document and update.message.document.mime_type and update.message.document.mime_type.startswith('image/'):
            # Image sent as document (common on mobile when "compressed" is disabled)
            file_id = update.message.document.file_id
            image_type = "document"
            logger.info(f"📄 Image document detected: {file_id} (mime: {update.message.document.mime_type})")
        
        if not file_id:
            logger.warning(f"⚠️ No valid image file_id found in message from user {user_id}")
            return  # Not a valid image
        
        logger.info(f"✅ Valid image found: {image_type} with file_id: {file_id}")
        
        # Create mobile-friendly buttons (larger text, clearer icons)
        keyboard = [
            [InlineKeyboardButton("✅ YES - Submit as PNL Entry", callback_data="auto_submit_yes")],
            [InlineKeyboardButton("❌ NO - Just sharing a photo", callback_data="auto_submit_no")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Mobile-optimized message with enhanced visibility
        group_indicator = f" (in {chat_type})" if chat_type in ['group', 'supergroup'] else ""
        
        # Log what we're about to send for debugging
        logger.info(f"📤 Sending auto-detection prompt to user {user_id} in chat {chat_id}")
        
        # Small delay to ensure message visibility
        await asyncio.sleep(0.5)
        
        try:
            prompt_message = await update.message.reply_text(
                f"🚨🚨 **SCREENSHOT DETECTED!**{group_indicator} 🚨🚨\n\n"
                "💰 **Want to submit this as a PNL trade?**\n\n"
                "👇 **CLICK ONE:**",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info(f"✅ Auto-detection prompt sent successfully: message_id {prompt_message.message_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send auto-detection prompt: {e}")
            return
        
        # Store the image temporarily
        self.user_sessions[user_id] = {
            'temp_photo': file_id,
            'temp_message_id': update.message.message_id,
            'prompt_message_id': prompt_message.message_id,
            'auto_detect_mode': True,
            'is_document': update.message.document is not None  # Track if it was sent as document
        }
    
    async def auto_submit_callback(self, update: Update, context) -> int:
        """Handle auto-submit yes/no callback"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # Handle test button callbacks
        if query.data.startswith("test_"):
            choice = query.data.split("_")[-1]
            if choice == "working":
                await query.edit_message_text("✅ **Great!** The bot is working perfectly in your group!")
            elif choice == "issues":
                await query.edit_message_text("❌ **Issues detected.** Please check the logs or contact support.")
            return ConversationHandler.END
        
        choice = query.data.split("_")[-1]  # Extract "yes" or "no"
        
        if choice == "no":
            # User doesn't want to submit - mobile-friendly message
            await query.edit_message_text(
                "👍 **Got it!**\n\n📸 Just sharing - carry on!"
            )
            
            # Clean up temp session after a delay to let user see the message
            if user_id in self.user_sessions:
                # Delete the prompt message after 3 seconds
                try:
                    await asyncio.sleep(3)
                    await context.bot.delete_message(
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id
                    )
                except Exception:
                    pass  # Message might already be deleted
                
                del self.user_sessions[user_id]
            return ConversationHandler.END
        
        elif choice == "yes":
            # User wants to submit - start the process
            username = query.from_user.username or query.from_user.first_name or f"User{user_id}"
            
            # Get the stored photo
            temp_data = self.user_sessions.get(user_id, {})
            screenshot_file_id = temp_data.get('temp_photo')
            
            # Initialize full submission session
            messages_to_delete = []
            if temp_data.get('temp_message_id'):
                messages_to_delete.append(temp_data.get('temp_message_id'))
            # Also track the current prompt message that will be edited
            messages_to_delete.append(query.message.message_id)
            
            self.user_sessions[user_id] = {
                'user_id': user_id,
                'username': username,
                'timestamp': datetime.now(timezone.utc),
                'screenshot': screenshot_file_id,
                'messages_to_delete': messages_to_delete
            }
            
            # Create currency selection keyboard
            keyboard = [
                [InlineKeyboardButton("💵 USD", callback_data="currency_USD")],
                [InlineKeyboardButton("◎ SOL", callback_data="currency_SOL")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🚀 **Let's go!**\n\n"
                "💰 **Step 1:** Select your currency",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
            
            return CURRENCY_SELECTION
        
        return ConversationHandler.END

    async def complete_submission(self, update: Update, context) -> None:
        """Complete the PNL submission with clean final post"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions:
            return
        
        session_data = self.user_sessions[user_id]
        
        try:
            # Prepare complete database record
            db_record = {
                'user_id': str(session_data['user_id']),
                'username': session_data['username'],
                'ticker': session_data.get('ticker', ''),
                'initial_investment': session_data.get('initial_investment', 0),
                'investment_usd': session_data.get('investment_usd', session_data.get('initial_investment', 0)),
                'investment_sol': session_data.get('investment_sol', 0),
                'profit_usd': session_data.get('profit_usd', 0),
                'profit_sol': session_data.get('profit_sol', 0),
                'timestamp': session_data['timestamp'],
                'currency': session_data.get('currency', 'USD'),
                'screenshot_file_id': session_data.get('screenshot', '')
            }
            
            # Save to database
            success = db_manager.insert_pnl_record(db_record)
            
            if success:
                # Create clean final post with image and data FIRST
                photo_file_id = session_data.get('screenshot')
                channel_message = message_formatter.format_submission_message(
                    session_data, currency_converter
                )
                
                # Send clean final post to user
                final_message = await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo_file_id,
                    caption=f"{channel_message}\n\n✅ **Success!**\n\n"
                            f"🏆 PNL recorded! Check `/leaderboard` to see your ranking!",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Now delete all form messages to keep chat clean (after final post is sent)
                messages_to_delete = session_data.get('messages_to_delete', [])
                for message_id in messages_to_delete:
                    try:
                        await context.bot.delete_message(
                            chat_id=update.effective_chat.id,
                            message_id=message_id
                        )
                        # Small delay between deletions to avoid rate limits
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.warning(f"Could not delete message {message_id}: {e}")
                
                # Post to all configured channels
                if CHANNELS_TO_POST:
                    logger.info(f"📢 Posting PNL to {len(CHANNELS_TO_POST)} channels")
                    
                    for channel_config in CHANNELS_TO_POST:
                        channel_id = channel_config['id']
                        topic_id = channel_config.get('topic_id')
                        
                        if not channel_id:  # Skip empty channel IDs
                            continue
                            
                        try:
                            # Prepare send_photo parameters
                            send_params = {
                                'chat_id': channel_id,
                                'photo': photo_file_id,
                                'caption': channel_message,
                                'parse_mode': ParseMode.MARKDOWN
                            }
                            
                            # Add topic ID if specified (for posting to specific topics/threads)
                            if topic_id:
                                send_params['message_thread_id'] = topic_id
                                logger.info(f"📍 Posting to channel {channel_id} topic {topic_id}")
                            else:
                                logger.info(f"📍 Posting to channel {channel_id}")
                            
                            await context.bot.send_photo(**send_params)
                            
                            display_name = f"{channel_id}" + (f" (topic {topic_id})" if topic_id else "")
                            logger.info(f"✅ Successfully posted to: {display_name}")
                            
                            # Small delay between posts to avoid rate limits
                            await asyncio.sleep(0.5)
                            
                        except Exception as e:
                            display_name = f"{channel_id}" + (f" topic {topic_id}" if topic_id else "")
                            logger.error(f"❌ Error posting to {display_name}: {e}")
                else:
                    logger.warning("⚠️ No channels configured for posting")
                
            else:
                # Clean up messages even if submission failed
                messages_to_delete = session_data.get('messages_to_delete', [])
                for message_id in messages_to_delete:
                    try:
                        await context.bot.delete_message(
                            chat_id=update.effective_chat.id,
                            message_id=message_id
                        )
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.warning(f"Could not delete message {message_id}: {e}")
                
                await update.message.reply_text(
                    "❌ **Submission failed!** Please try again later."
                )
            
        except Exception as e:
            logger.error(f"Error in complete_submission: {e}")
            # Clean up messages even if there's an error
            messages_to_delete = session_data.get('messages_to_delete', [])
            for message_id in messages_to_delete:
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=message_id
                    )
                    await asyncio.sleep(0.1)
                except Exception as e:
                    logger.warning(f"Could not delete message {message_id}: {e}")
            
            await update.message.reply_text(
                "❌ **Submission failed!** Please try again later."
            )
        
        # Clean up session
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
    
    async def clean_command_message(self, update: Update, context) -> None:
        """Clean up command message after sending response"""
        try:
            await asyncio.sleep(1)  # Small delay to ensure response is sent first
            await update.message.delete()
        except Exception as e:
            logger.debug(f"Could not delete command message: {e}")
    
    async def safe_reply(self, update: Update, message: str, **kwargs):
        """Safely reply to messages, handle deleted message errors"""
        try:
            return await update.message.reply_text(message, **kwargs)
        except Exception as e:
            logger.warning(f"Failed to reply to message: {e}")
            # Try sending without reply
            try:
                return await update.effective_chat.send_message(message, **kwargs)
            except Exception as e2:
                logger.error(f"Failed to send message entirely: {e2}")
                return None

    async def cancel_command(self, update: Update, context) -> int:
        """Cancel the submission process"""
        user_id = update.effective_user.id
        
        # Clean up any tracked messages
        if user_id in self.user_sessions:
            messages_to_delete = self.user_sessions[user_id].get('messages_to_delete', [])
            for message_id in messages_to_delete:
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=message_id
                    )
                except Exception as e:
                    logger.warning(f"Could not delete message {message_id}: {e}")
            
            del self.user_sessions[user_id]
        
        await update.message.reply_text(
            "❌ Submission cancelled. Use /submit to start over."
        )
        return ConversationHandler.END
    
    async def leaderboard_command(self, update: Update, context) -> None:
        """Show all-time leaderboard"""
        leaders = db_manager.get_all_time_leaderboard()
        message = message_formatter.format_leaderboard_message(
            "All-Time Leaderboard", leaders, currency_converter
        )
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        await self.clean_command_message(update, context)
    
    async def monthly_leaderboard_command(self, update: Update, context) -> None:
        """Show monthly leaderboard"""
        year, month = date_helper.get_current_month_year()
        leaders = db_manager.get_monthly_leaderboard(year, month)
        
        month_names = ["", "January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]
        title = f"{month_names[month]} {year} Leaderboard"
        
        message = message_formatter.format_leaderboard_message(
            title, leaders, currency_converter
        )
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def weekly_leaderboard_command(self, update: Update, context) -> None:
        """Show weekly leaderboard"""
        start_date, end_date = date_helper.get_current_week_range()
        leaders = db_manager.get_weekly_leaderboard(start_date, end_date)
        
        title = f"This Week's Leaderboard ({start_date.strftime('%d/%m')} - {end_date.strftime('%d/%m')})"
        message = message_formatter.format_leaderboard_message(
            title, leaders, currency_converter
        )
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def daily_leaderboard_command(self, update: Update, context) -> None:
        """Show daily leaderboard"""
        today = datetime.now(timezone.utc)
        leaders = db_manager.get_daily_leaderboard(today)
        
        title = f"Today's Leaderboard ({today.strftime('%d/%m/%Y')})"
        message = message_formatter.format_leaderboard_message(
            title, leaders, currency_converter
        )
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def trade_leader_command(self, update: Update, context) -> None:
        """Show trade count leaderboard for this week"""
        start_date, end_date = date_helper.get_current_week_range()
        leaders = db_manager.get_trade_count_leaderboard(start_date, end_date)
        
        title = f"This Week's Trade Leaders ({start_date.strftime('%d/%m')} - {end_date.strftime('%d/%m')})"
        message = message_formatter.format_trade_leaderboard_message(title, leaders)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def profit_goat_command(self, update: Update, context) -> None:
        """Show the profit GOAT"""
        goat_data = db_manager.get_profit_goat()
        message = message_formatter.format_profit_goat_message(goat_data)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def pnl_report_command(self, update: Update, context) -> None:
        """Generate PNL report (moderators only)"""
        user_id = update.effective_user.id
        
        if user_id not in MODERATOR_IDS:
            await update.message.reply_text("❌ Access denied. This command is for moderators only.")
            return
        
        try:
            # Get all PNL data
            data = db_manager.get_all_pnl_data()
            
            if not data:
                await update.message.reply_text("📄 No PNL data available for export.")
                return
            
            # Create DataFrame and CSV
            df = pd.DataFrame(data)
            
            # Reorder columns for better readability
            column_order = ['username', 'ticker', 'initial_investment', 'profit_usd', 'profit_sol', 
                          'currency', 'timestamp', 'is_historical']
            
            # Only include columns that exist
            available_columns = [col for col in column_order if col in df.columns]
            df = df[available_columns]
            
            # Create CSV in memory
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pnl_report_{timestamp}.csv"
            
            await update.message.reply_document(
                document=csv_buffer,
                filename=filename,
                caption=f"📄 **PNL Report Generated**\n\n"
                       f"📊 Total records: {len(df)}\n"
                       f"📅 Generated: {datetime.now().strftime('%d/%m/%Y %H:%M UTC')}",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error generating PNL report: {e}")
            await update.message.reply_text("❌ Error generating report. Please try again later.")
    
    # ===== PERSONAL ANALYTICS COMMANDS =====
    
    async def mystats_command(self, update: Update, context) -> None:
        """Show personal trading statistics"""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name or f"User{user_id}"
        
        # Get user's trading stats
        stats = db_manager.get_user_stats(user_id, username)
        
        if not stats:
            await update.message.reply_text("📊 No trading data found for your account. Use `/submit` to add your first trade!")
            await self.clean_command_message(update, context)
            return
        
        message = message_formatter.format_user_stats_message(stats, username)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        await self.clean_command_message(update, context)
    
    async def myhistory_command(self, update: Update, context) -> None:
        """Show personal trading history"""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name or f"User{user_id}"
        
        # Get user's trading history
        history = db_manager.get_user_history(user_id, username)
        
        if not history:
            await self.safe_reply(update, "📈 No trading history found for your account.")
            return
        
        message = message_formatter.format_user_history_message(history, username)
        await self.safe_reply(update, message, parse_mode=ParseMode.MARKDOWN)
    
    async def compare_command(self, update: Update, context) -> None:
        """Compare two traders"""
        if not context.args:
            await update.message.reply_text("❓ Usage: `/compare @username`\nExample: `/compare @TradingGuru`")
            return
        
        user1_id = update.effective_user.id
        user1_name = update.effective_user.username or update.effective_user.first_name or f"User{user1_id}"
        user2_name = context.args[0].replace('@', '')
        
        # Get stats for both users
        user1_stats = db_manager.get_user_stats(user1_id, user1_name)
        user2_stats = db_manager.get_user_stats_by_username(user2_name)
        
        if not user1_stats:
            await update.message.reply_text("📊 You don't have any trading data yet. Use `/submit` to add trades!")
            return
        
        if not user2_stats:
            await update.message.reply_text(f"📊 No trading data found for @{user2_name}")
            return
        
        message = message_formatter.format_comparison_message(user1_stats, user2_stats, user1_name, user2_name)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def roi_command(self, update: Update, context) -> None:
        """Show ROI-based leaderboard"""
        leaders = db_manager.get_roi_leaderboard()
        
        title = "🚀 ROI Leaderboard (Best Returns)"
        message = message_formatter.format_roi_leaderboard_message(title, leaders)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    # ===== TOKEN INTELLIGENCE COMMANDS =====
    
    async def tokenleader_command(self, update: Update, context) -> None:
        """Show most profitable tokens"""
        token_stats = db_manager.get_token_leaderboard()
        
        if not token_stats:
            await update.message.reply_text("📊 No token data available yet.")
            return
        
        message = message_formatter.format_token_leaderboard_message(token_stats)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def tokenstats_command(self, update: Update, context) -> None:
        """Show detailed stats for a specific token"""
        if not context.args:
            await update.message.reply_text("❓ Usage: `/tokenstats TICKER`\nExample: `/tokenstats BTC`")
            return
        
        ticker = context.args[0].upper()
        stats = db_manager.get_token_stats(ticker)
        
        if not stats:
            await update.message.reply_text(f"📊 No trading data found for {ticker}")
            return
        
        message = message_formatter.format_token_stats_message(ticker, stats)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def trendingcoins_command(self, update: Update, context) -> None:
        """Show most traded tokens this week/month"""
        trending = db_manager.get_trending_tokens()
        
        if not trending:
            await update.message.reply_text("📊 No trending token data available.")
            return
        
        message = message_formatter.format_trending_tokens_message(trending)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    # ===== ADVANCED LEADERBOARDS =====
    
    async def bigballer_command(self, update: Update, context) -> None:
        """Show highest investment amounts (whale tracker)"""
        whales = db_manager.get_whale_leaderboard()
        
        title = "🐋 Big Baller Leaderboard (Highest Investments)"
        message = message_formatter.format_whale_leaderboard_message(title, whales)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def percentking_command(self, update: Update, context) -> None:
        """Show best percentage gains"""
        leaders = db_manager.get_percent_gain_leaderboard()
        
        title = "👑 Percent King Leaderboard (Best % Gains)"
        message = message_formatter.format_percent_leaderboard_message(title, leaders)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def consistenttrader_command(self, update: Update, context) -> None:
        """Show most consistent profitable traders"""
        traders = db_manager.get_consistency_leaderboard()
        
        title = "🎯 Consistent Trader Leaderboard"
        message = message_formatter.format_consistency_leaderboard_message(title, traders)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def lossleader_command(self, update: Update, context) -> None:
        """Show transparency leaderboard (biggest losses)"""
        leaders = db_manager.get_loss_leaderboard()
        
        title = "😅 Transparency Leaderboard (Lessons Learned)"
        message = message_formatter.format_loss_leaderboard_message(title, leaders)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def smallcap_command(self, update: Update, context) -> None:
        """Show leaderboard for investments under $100"""
        leaders = db_manager.get_investment_filtered_leaderboard(max_investment=100)
        
        title = "💰 Small Cap Leaderboard (Under $100)"
        message = message_formatter.format_leaderboard_message(title, leaders, currency_converter)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def midcap_command(self, update: Update, context) -> None:
        """Show leaderboard for investments $100-$1000"""
        leaders = db_manager.get_investment_filtered_leaderboard(min_investment=100, max_investment=1000)
        
        title = "💎 Mid Cap Leaderboard ($100-$1000)"
        message = message_formatter.format_leaderboard_message(title, leaders, currency_converter)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def largecap_command(self, update: Update, context) -> None:
        """Show leaderboard for investments over $1000"""
        leaders = db_manager.get_investment_filtered_leaderboard(min_investment=1000)
        
        title = "🐋 Large Cap Leaderboard (Over $1000)"
        message = message_formatter.format_leaderboard_message(title, leaders, currency_converter)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    # ===== GAMIFICATION & SOCIAL =====
    
    async def achievements_command(self, update: Update, context) -> None:
        """Show earned badges and achievements"""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name or f"User{user_id}"
        
        achievements = db_manager.get_user_achievements(user_id, username)
        message = message_formatter.format_achievements_message(achievements, username)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def streaks_command(self, update: Update, context) -> None:
        """Show current winning/losing streaks"""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name or f"User{user_id}"
        
        streaks = db_manager.get_user_streaks(user_id, username)
        message = message_formatter.format_streaks_message(streaks, username)
        await self.safe_reply(update, message, parse_mode=ParseMode.MARKDOWN)
        await self.clean_command_message(update, context)
    
    async def milestones_command(self, update: Update, context) -> None:
        """Show progress toward goals"""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name or f"User{user_id}"
        
        milestones = db_manager.get_user_milestones(user_id, username)
        message = message_formatter.format_milestones_message(milestones, username)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def randomtrade_command(self, update: Update, context) -> None:
        """Show random successful trade for inspiration"""
        trade = db_manager.get_random_successful_trade()
        
        if not trade:
            await update.message.reply_text("📊 No successful trades found for inspiration.")
            return
        
        message = message_formatter.format_random_trade_message(trade)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def todaysbiggest_command(self, update: Update, context) -> None:
        """Show biggest winner today"""
        today = datetime.now(timezone.utc)
        winner = db_manager.get_daily_biggest_winner(today)
        
        if not winner:
            await update.message.reply_text("📊 No trades recorded for today yet.")
            return
        
        message = message_formatter.format_daily_winner_message(winner)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def hall_of_fame_command(self, update: Update, context) -> None:
        """Show all-time legends with special recognition"""
        legends = db_manager.get_hall_of_fame()
        
        if not legends:
            await update.message.reply_text("🏛️ Hall of Fame is still being built...")
            return
        
        message = message_formatter.format_hall_of_fame_message(legends)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    # ===== MARKET INTELLIGENCE =====
    
    async def marketsentiment_command(self, update: Update, context) -> None:
        """Show community sentiment analysis"""
        sentiment = db_manager.get_market_sentiment()
        
        message = message_formatter.format_market_sentiment_message(sentiment)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def popularityindex_command(self, update: Update, context) -> None:
        """Show most frequently traded tokens"""
        popularity = db_manager.get_token_popularity()
        
        message = message_formatter.format_popularity_index_message(popularity)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def profitability_command(self, update: Update, context) -> None:
        """Show success rate and average profit for specific tokens"""
        if not context.args:
            await update.message.reply_text("❓ Usage: `/profitability TICKER`\nExample: `/profitability BTC`")
            return
        
        ticker = context.args[0].upper()
        profitability = db_manager.get_token_profitability(ticker)
        
        if not profitability:
            await update.message.reply_text(f"📊 No profitability data found for {ticker}")
            return
        
        message = message_formatter.format_profitability_message(ticker, profitability)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def timetrendz_command(self, update: Update, context) -> None:
        """Show best performing times/days for trades"""
        trends = db_manager.get_time_trends()
        
        message = message_formatter.format_time_trends_message(trends)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    # ===== WEBSITE & LINKS =====
    
    async def lore_command(self, update: Update, context) -> None:
        """Open Lore.trade website within Telegram"""
        # Create inline keyboard with website button
        keyboard = [
            [InlineKeyboardButton("🚀 Launch Lore.Trade", url="https://Lore.Trade")],
            [InlineKeyboardButton("🎯 Get Access Now", url="https://Lore.Trade/Access")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = """
🌟 **LORE.TRADE - Premium Trading Platform** 🌟

🚀 **Experience Next-Level Trading:**
• Advanced analytics & insights
• Real-time market intelligence  
• Professional trading tools
• Community-driven strategies

💎 **Why Lore.trade?**
• Used by our top community traders
• Proven results & performance tracking
• Seamless integration with our PNL bot
• Exclusive features for serious traders

👆 **Choose your path:**
        """
        
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        await self.clean_command_message(update, context)
    
    # ===== UTILITY & SEARCH =====
    
    async def search_command(self, update: Update, context) -> None:
        """Find all trades for a specific token"""
        if not context.args:
            await update.message.reply_text("❓ Usage: `/search TICKER`\nExample: `/search BTC`")
            return
        
        ticker = context.args[0].upper()
        trades = db_manager.search_trades_by_ticker(ticker)
        
        if not trades:
            await update.message.reply_text(f"🔍 No trades found for {ticker}")
            return
        
        message = message_formatter.format_search_results_message(ticker, trades)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def finduser_command(self, update: Update, context) -> None:
        """Search specific user's trades"""
        if not context.args:
            await update.message.reply_text("❓ Usage: `/finduser @username`\nExample: `/finduser @TradingGuru`")
            return
        
        username = context.args[0].replace('@', '')
        trades = db_manager.search_trades_by_username(username)
        
        if not trades:
            await update.message.reply_text(f"🔍 No trades found for @{username}")
            return
        
        message = message_formatter.format_user_search_results_message(username, trades)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def topgainer_command(self, update: Update, context) -> None:
        """Show best percentage gain today/week/month"""
        period = context.args[0] if context.args else 'today'
        
        if period not in ['today', 'week', 'month']:
            await update.message.reply_text("❓ Usage: `/topgainer [today|week|month]`\nExample: `/topgainer week`")
            return
        
        gainer = db_manager.get_top_gainer(period)
        
        if not gainer:
            await update.message.reply_text(f"📊 No data available for {period}")
            return
        
        message = message_formatter.format_top_gainer_message(gainer, period)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def export_command(self, update: Update, context) -> None:
        """Export personal trading data (for mods and admins only)"""
        user_id = update.effective_user.id
        
        if user_id not in MODERATOR_IDS:
            await update.message.reply_text("❌ Access denied. This command is for moderators only.")
            return
        
        # This is the same as pnl_report but for personal data
        username = update.effective_user.username or update.effective_user.first_name or f"User{user_id}"
        data = db_manager.get_user_export_data(user_id, username)
        
        if not data:
            await update.message.reply_text("📄 No personal trading data available for export.")
            return
        
        # Create DataFrame and CSV
        df = pd.DataFrame(data)
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"personal_trades_{timestamp}.csv"
        
        await update.message.reply_document(
            document=csv_buffer,
            filename=filename,
            caption=f"📄 **Personal Trading Data Export**\n\n"
                   f"📊 Total records: {len(df)}\n"
                   f"📅 Generated: {datetime.now().strftime('%d/%m/%Y %H:%M UTC')}",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def portfolio_command(self, update: Update, context) -> None:
        """Show diversification across tokens"""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name or f"User{user_id}"
        
        portfolio = db_manager.get_user_portfolio(user_id, username)
        
        if not portfolio:
            await update.message.reply_text("📊 No portfolio data available. Use `/submit` to add trades!")
            return
        
        message = message_formatter.format_portfolio_message(portfolio, username)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def monthlyreport_command(self, update: Update, context) -> None:
        """Show personal monthly summary"""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name or f"User{user_id}"
        
        # Get current month data
        now = datetime.now(timezone.utc)
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        report = db_manager.get_user_monthly_report(user_id, username, start_date)
        
        if not report:
            await update.message.reply_text("📊 No trading data for this month yet.")
            return
        
        message = message_formatter.format_monthly_report_message(report, username)
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    # ===== FILTERS COMMAND =====
    
    async def filters_command(self, update: Update, context) -> None:
        """Show all available commands organized by category"""
        filters_message = """
🔧 **ALL COMMANDS - ORGANIZED BY CATEGORY** 🔧

**🚀 GETTING STARTED**
• `/start` - Bot welcome & overview
• `/help` - Complete command guide
• `/pnlguide` - How to submit PNL entries
• `/submit` - Submit PNL with screenshot
• `/cancel` - Cancel submission

**🏆 LEADERBOARDS**
• `/leaderboard` - All-time top 10
• `/monthlyleaderboard` - Top 10 this month
• `/weeklyleaderboard` - Top 10 this week
• `/dailyleaderboard` - Top 10 today
• `/tradeleader` - Top 10 by trade count
• `/profitgoat` - Highest profit holder

**📈 PERSONAL ANALYTICS**
• `/mystats` - Your trading dashboard
• `/myhistory` - Your trading history
• `/compare @username` - Compare traders
• `/portfolio` - Your token diversification
• `/monthlyreport` - Your monthly summary

**🚀 ROI & PERFORMANCE**
• `/roi` - ROI-based leaderboard
• `/percentking` - Best % gains
• `/consistenttrader` - Most consistent
• `/topgainer [period]` - Best gainer

**💰 INVESTMENT CATEGORIES**
• `/smallcap` - Under $100 leaderboard
• `/midcap` - $100-$1000 leaderboard
• `/largecap` - Over $1000 leaderboard
• `/bigballer` - Highest investments

**🎯 TOKEN INTELLIGENCE**
• `/tokenleader` - Most profitable tokens
• `/tokenstats TICKER` - Token details
• `/trendingcoins` - Most traded tokens
• `/profitability TICKER` - Token success rate

**🔍 SEARCH & DISCOVERY**
• `/search TICKER` - Find token trades
• `/finduser @username` - Find user trades
• `/randomtrade` - Random inspiration
• `/todaysbiggest` - Today's biggest win

**🎮 GAMIFICATION**
• `/achievements` - Your badges
• `/streaks` - Win/loss streaks
• `/milestones` - Progress tracking
• `/hall_of_fame` - All-time legends

**📊 MARKET INTELLIGENCE**
• `/marketsentiment` - Community sentiment
• `/popularityindex` - Token popularity
• `/timetrendz` - Best trading times
• `/lossleader` - Transparency board

**🌐 WEBSITE & LINKS**
• `/lore` - Open Lore.trade platform

**🔧 MODERATOR ONLY**
• `/pnlreport` - Generate CSV report
• `/export` - Export personal data

Use `/filters` to see this list anytime! 🚀
        """
        await update.message.reply_text(filters_message, parse_mode=ParseMode.MARKDOWN)
    
    async def pnlguide_command(self, update: Update, context) -> None:
        """Show comprehensive PNL submission guide"""
        guide_message = """
📊 **COMPLETE PNL SUBMISSION GUIDE** 📊
*How to Submit Profits & Losses*

🎯 **TWO WAYS TO SUBMIT:**

**🚀 METHOD 1: AUTO-DETECTION (EASIEST)**

**Step 1:** Go to **PnLs topic** in the group
**Step 2:** Upload ANY screenshot 📱
**Step 3:** Bot detects it: "📸 Screenshot detected!"
**Step 4:** Click **✅ YES - Submit as PNL Entry**
**Step 5:** Follow the 4-step guided form
**Step 6:** Your clean post appears automatically! ✨

*All form messages get deleted - only final post remains*

**📝 METHOD 2: MANUAL SUBMISSION**

Type `/submit` and follow the prompts:
1. **Upload screenshot** 📸 (required)
2. **Select currency** (💵 USD or ◎ SOL)
3. **Enter ticker** ($TROLL, $KING, $gork, etc.)
4. **Enter investment** (how much you put in)
5. **Enter profit/loss** (your result)

💡 **PROFIT/LOSS EXAMPLES:**

**🟢 FOR PROFITS (positive numbers):**
• Made $150 profit → Type: `150`
• Made $75.25 profit → Type: `75.25`
• Made $500 profit → Type: `500`

**🔴 FOR LOSSES (negative numbers):**
• Lost $50 → Type: `-50`
• Lost $125.75 → Type: `-125.75`
• Lost $200 → Type: `-200`

**📊 SAMPLE PROFIT SUBMISSION:**
```
Investment: $500 in $TROLL
Result: Sold for $750 (made $250 profit)
Enter: 500 (investment), then 250 (profit)
```

**📊 SAMPLE LOSS SUBMISSION:**
```
Investment: $1000 in $KING
Result: Sold for $850 (lost $150)
Enter: 1000 (investment), then -150 (loss)
```

**✅ IMPORTANT TIPS:**
• **Always use minus (-) for losses**
• **Upload real screenshots only**
• **Be honest - transparency builds trust**
• **Auto-detection only works in PnLs topic**
• **Decimals are supported** (25.50, 150.75)

**🎮 WHAT HAPPENS AFTER SUBMISSION:**
✨ Clean post with your trade details
🏆 Achievement tracking & badges
📊 Community ranking updates
🔥 Streak tracking (wins/losses)
📈 Personal stats calculation

**🆘 NEED HELP?**
• Type `/help` for all commands
• Type `/cancel` to stop any process
• Type `/mystats` to see your progress

Ready to track your trading journey? Start with a screenshot! 📸
        """
        await update.message.reply_text(guide_message, parse_mode=ParseMode.MARKDOWN)

    async def loretotalprofit_command(self, update: Update, context) -> None:
        """Show total combined profit across all trades"""
        try:
            # Get total profit data
            total_data = db_manager.get_total_profit_combined()
            
            if not total_data:
                await self.safe_reply(update, "📊 No trading data available yet.")
        await self.clean_command_message(update, context)
                return
            
            # Extract data
            total_profit_usd = total_data.get('total_profit_usd', 0)
            total_profit_sol = total_data.get('total_profit_sol', 0)
            total_trades = total_data.get('total_trades', 0)
            total_investment = total_data.get('total_investment', 0)
            trader_count = total_data.get('trader_count', 0)
            token_count = total_data.get('token_count', 0)
            winning_trades = total_data.get('winning_trades', 0)
            losing_trades = total_data.get('losing_trades', 0)
            overall_roi = total_data.get('overall_roi', 0)
            win_rate = total_data.get('win_rate', 0)
            
            # Get current SOL rate for reference and comparison
            sol_usd_rate = currency_converter.get_sol_usd_rate()
            current_sol_rate = f"${sol_usd_rate:.2f}" if sol_usd_rate else "N/A"
            current_sol_value = total_profit_sol * sol_usd_rate if sol_usd_rate else 0
            
            # Format the comprehensive message
            message = f"""
🌌 **LORE TOTAL PROFIT - COMMUNITY OVERVIEW** 🌌

💰 **TOTAL COMBINED PROFIT:**
💵 **${total_profit_usd:,.2f} USD** *(Actual profit at historical SOL rates)*
◎ **{total_profit_sol:.3f} SOL** *(Total SOL earned)*

📊 **PROFIT BREAKDOWN:**
🔸 **Historical Value:** ${total_profit_usd:,.2f} *(Real profit when trades were made)*
🔸 **Current SOL Rate:** {current_sol_rate} per SOL
🔸 **Current Value:** ${current_sol_value:,.2f} *(If all SOL converted at today's rate)*
🔸 **Rate Impact:** {'+' if current_sol_value > total_profit_usd else ''}${current_sol_value - total_profit_usd:,.2f} *(Difference due to SOL price changes)*

📊 **TRADING STATISTICS:**
🔢 **Total Trades:** {total_trades:,}
👥 **Active Traders:** {trader_count:,}
🪙 **Tokens Traded:** {token_count:,}
💸 **Total Investment:** ${total_investment:,.2f}

📈 **PERFORMANCE METRICS:**
🎯 **Overall ROI:** {overall_roi:+.2f}%
✅ **Win Rate:** {win_rate:.1f}%
🟢 **Winning Trades:** {winning_trades:,}
🔴 **Losing Trades:** {losing_trades:,}

📅 **Updated:** {message_formatter.format_date_uk_with_time(datetime.now(timezone.utc))}

💡 **Note:** The "Historical Value" shows your actual profit based on SOL prices when each trade was made. The "Current Value" shows what those same SOL amounts would be worth at today's rate. The difference reflects SOL price movement over time.

*This represents the combined profit/loss of every individual trade entry in our community database.*
            """
            
            await self.safe_reply(update, message.strip(), parse_mode=ParseMode.MARKDOWN)
            await self.clean_command_message(update, context)
            
        except Exception as e:
            logger.error(f"Error in loretotalprofit command: {e}")
            await self.safe_reply(update, "❌ Error retrieving total profit data. Please try again.")
            await self.clean_command_message(update, context)

    async def battlerules_command(self, update: Update, context) -> None:
        """Show comprehensive battle rules and instructions"""
        rules_message = """
⚔️ **BATTLE SYSTEM - COMPLETE RULES & GUIDE** ⚔️

🎯 **AVAILABLE BATTLE TYPES:**

**💰 PROFIT BATTLE** (`/profitbattle`)
• **Objective:** Earn the most USD profit during battle period
• **Winner:** Highest total profit across all trades
• **Rewards:** 🏆 Profit Battle Points + Champion status

**🔥 TRADE WAR** (`/tradewar`)
• **Objective:** Execute the most trades during battle period
• **Winner:** Highest trade count (regardless of profit/loss)
• **Rewards:** ⚡ Trade War Points + Trade Count Champion status

---

🚀 **HOW TO START A BATTLE:**

**Step 1:** Choose your battle type
• Type `/profitbattle` or `/tradewar`

**Step 2:** Set player count (2-8 players)
• Select number of participants

**Step 3:** Set battle duration (15 minutes to 4 weeks)
• Choose from presets or set custom time
• Examples: 30m, 2h, 1d, 3d, 1w, 2w

**Step 4:** Add participants
• Type usernames: `@dave @bob @bill`
• Must use @ symbol before each username

**Step 5:** Confirm & commence
• Review battle settings
• Click "⚔️ COMMENCE BATTLE" to start!

---

⏰ **BATTLE MECHANICS:**

**🎬 BATTLE START:**
• Countdown begins immediately
• All participants get notifications
• Battle tracking activates

**📊 BATTLE MONITORING:**
• Real-time score tracking
• Live leaderboard calculations
• Updates when leadership changes
• Automatic battle completion

**🏁 BATTLE END:**
• Automatic completion when time expires
• Epic victory announcement
• Points awarded to all participants

---

🏆 **BATTLE POINTS SYSTEM:**

**🥇 1st Place:** 100 Points + 🏆 Champion Badge
**🥈 2nd Place:** 75 Points + 🏅 Silver Medal
**🥉 3rd Place:** 50 Points + 🥉 Bronze Medal
**🎖️ Participation:** 25 Points + 🎖️ Warrior Badge

---

📊 **PROFIT BATTLE SCORING:**
• **Profit Trades:** +$150 = 150 points toward score
• **Loss Trades:** -$50 = -50 points toward score
• **Net Profit:** Your total USD profit during battle
• **Strategy:** Focus on profitable trades, minimize losses

📈 **TRADE WAR SCORING:**
• **Every Trade:** +1 point toward score
• **Profit/Loss:** Doesn't matter - trade count is king!
• **Total Trades:** Your trade count during battle
• **Strategy:** High frequency trading, stay active

---

🎯 **BATTLE STRATEGY TIPS:**

**💰 For Profit Battles:**
• Focus on high-confidence trades
• Take profits when available
• Manage risk carefully
• Quality over quantity

**🔥 For Trade Wars:**
• Stay active throughout battle
• Multiple small trades can win
• Monitor market opportunities
• Quantity over quality

---

🛡️ **BATTLE RULES & REQUIREMENTS:**

**✅ REQUIREMENTS:**
• Anyone can start a battle - no previous trades needed!
• All participants must be active community members
• Screenshots required for all trades during battle
• Trades must be submitted within 24 hours

**⛔ RESTRICTIONS:**
• No fake trades or manipulation allowed
• Battle creator cannot cancel once started
• All trades must be legitimate and verifiable
• Screenshot evidence required for all trades
• Respect other participants and fair play

**🎮 FAIR PLAY:**
• All trades verified through screenshots
• Timestamps strictly enforced
• Community voting on disputes
• Moderator intervention when needed

---

🏅 **BATTLE ACHIEVEMENTS:**

**🏆 Champion Badges:**
• Profit Battle Champion
• Trade War Champion
• Battle Legend (10+ wins)
• Warrior Elite (50+ battles)

**🎖️ Special Titles:**
• Battle Master (5 consecutive wins)
• Trade Count King (1000+ trades in battle)
• Profit Titan ($10K+ profit in battle)
• Battle Veteran (100+ battles)

---

⚡ **BATTLE COMMANDS:**

**🚀 Start Battles:**
• `/profitbattle` - Start profit competition
• `/tradewar` - Start trade count war

**📊 Check Status:**
• `/battlerules` - View this complete guide
• `/battlpoints` - See your battle points and stats
• `/battleleaderboard` - Hall of champions
• `/mystats` - See your overall trading record
• `/achievements` - View trading achievements

**🏆 Leaderboards:**
• `/leaderboard` - Overall community rankings
• `/battleleaderboard` - Battle champions ranking
• Live battle stats tracked automatically

---

🎉 **VICTORY CELEBRATIONS:**

**🏆 CHAMPION ANNOUNCEMENT:**
• Posted in all community channels
• Detailed victory statistics
• Battle highlights and records
• Public recognition and praise

**📈 BATTLE SUMMARY:**
• Complete participant rankings
• Individual performance metrics
• Battle highlights and records
• Statistical analysis and insights

---

💡 **PRO TIPS:**

• **Time Zones:** All battles use UTC timing - plan accordingly!
• **Start Small:** Try shorter battles (15-30 minutes) first
• **Learn Together:** Support and learn from your opponents
• **Screenshot Ready:** Keep your trading app ready for captures
• **Custom Durations:** Use formats like `2h`, `3d`, `1w` for custom times
• **Community:** Remember it's about learning and having fun!

Ready to prove your trading prowess? Choose your battle and may the best trader win! ⚔️💰

Type `/profitbattle` or `/tradewar` to get started!
        """
        await update.message.reply_text(rules_message, parse_mode=ParseMode.MARKDOWN)
        await self.clean_command_message(update, context)

    async def battlpoints_command(self, update: Update, context) -> None:
        """Show user's battle points and battle record"""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name or f"User{user_id}"
        
        # Get user's battle stats
        battle_stats = db_manager.get_user_battle_stats(user_id, username)
        
        if not battle_stats:
            await update.message.reply_text(
                "🏆 **Battle Stats**\n\n"
                "You haven't participated in any battles yet!\n"
                "Use `/profitbattle` or `/tradewar` to start competing! ⚔️",
                parse_mode=ParseMode.MARKDOWN
            )
            await self.clean_command_message(update, context)
            return
        
        # Format battle stats
        total_points = battle_stats.get('total_points', 0)
        battles_won = battle_stats.get('battles_won', 0)
        battles_participated = battle_stats.get('battles_participated', 0)
        profit_battles_won = battle_stats.get('profit_battles_won', 0)
        trade_wars_won = battle_stats.get('trade_wars_won', 0)
        
        win_rate = (battles_won / battles_participated * 100) if battles_participated > 0 else 0
        
        # Determine rank based on points
        rank_info = db_manager.get_user_battle_rank(user_id, username)
        rank = rank_info.get('rank', 'Unranked')
        
        # Get recent battles
        recent_battles = battle_stats.get('recent_battles', [])
        
        stats_message = f"""
🏆 **@{username}'s Battle Record** 🏆

**⚔️ BATTLE POINTS: {total_points}**
🏅 **Global Rank:** #{rank}

**📊 BATTLE STATISTICS:**
• Total Battles: {battles_participated}
• Victories: {battles_won}
• Win Rate: {win_rate:.1f}%

**🎯 VICTORIES BY TYPE:**
• 💰 Profit Battles: {profit_battles_won}
• ⚡ Trade Wars: {trade_wars_won}

**🔥 RECENT BATTLES:**
        """
        
        if recent_battles:
            for battle in recent_battles[-3:]:  # Show last 3 battles
                battle_type = "💰" if battle['type'] == 'profit' else "⚡"
                result = "🏆 WON" if battle['won'] else "⚔️ FOUGHT"
                points = f"+{battle['points']}" if battle['points'] > 0 else "0"
                
                stats_message += f"\n• {battle_type} {result} ({points} pts)"
        else:
            stats_message += "\n• No recent battles"
        
        stats_message += "\n\n*Use `/battlerules` to learn about battles!*"
        
        await update.message.reply_text(stats_message.strip(), parse_mode=ParseMode.MARKDOWN)
        await self.clean_command_message(update, context)
    
    async def battleleaderboard_command(self, update: Update, context) -> None:
        """Show battle points leaderboard"""
        try:
            # Get battle leaderboard
            leaderboard = db_manager.get_battle_leaderboard()
            
            if not leaderboard:
                await update.message.reply_text(
                    "🏆 **Battle Leaderboard**\n\n"
                    "No battle champions yet! Be the first to compete! ⚔️\n"
                    "Use `/profitbattle` or `/tradewar` to start!",
                    parse_mode=ParseMode.MARKDOWN
                )
                await self.clean_command_message(update, context)
                return
            
            # Format leaderboard
            leaderboard_text = "🏆 **BATTLE CHAMPIONS LEADERBOARD** 🏆\n\n"
            
            for i, user in enumerate(leaderboard[:10], 1):
                username = user['username']
                points = user['total_points']
                battles_won = user['battles_won']
                battles_total = user['battles_participated']
                
                if i == 1:
                    emoji = "👑"
                elif i == 2:
                    emoji = "🥈"
                elif i == 3:
                    emoji = "🥉"
                else:
                    emoji = "🎖️"
                
                leaderboard_text += f"{emoji} **#{i} @{username}**\n"
                leaderboard_text += f"    🏆 {points} pts | ⚔️ {battles_won}/{battles_total} wins\n\n"
            
            leaderboard_text += "*Battle more to climb the ranks! Use `/battlpoints` to see your stats*"
            
            await update.message.reply_text(leaderboard_text, parse_mode=ParseMode.MARKDOWN)
            await self.clean_command_message(update, context)
            
        except Exception as e:
            logger.error(f"Error in battleleaderboard command: {e}")
            await self.safe_reply(update, "❌ Error retrieving battle leaderboard. Please try again.")
            await self.clean_command_message(update, context)

    # ===== PVP BATTLE SYSTEM COMMANDS =====
    
    def parse_duration(self, duration_str):
        """Parse duration string into minutes"""
        import re
        
        # Remove spaces and convert to lowercase
        duration_str = duration_str.replace(' ', '').lower()
        
        # Match pattern: number + unit
        match = re.match(r'^(\d+)([mhdw])$', duration_str)
        if not match:
            return None
        
        value, unit = match.groups()
        value = int(value)
        
        # Convert to minutes
        if unit == 'm':
            return value, 'minutes'
        elif unit == 'h':
            return value * 60, 'hours'
        elif unit == 'd':
            return value * 60 * 24, 'days'
        elif unit == 'w':
            return value * 60 * 24 * 7, 'weeks'
        
        return None
    
    def parse_preset_duration(self, duration_code):
        """Parse preset duration codes"""
        duration_map = {
            '30m': (30, 'minutes'),
            '2h': (120, 'hours'),
            '1d': (1440, 'days'),
            '3d': (4320, 'days'),
            '1w': (10080, 'weeks')
        }
        
        if duration_code in duration_map:
            minutes, unit = duration_map[duration_code]
            return minutes, unit
        
        return None
    
    def format_duration_display(self, minutes, unit):
        """Format duration for display"""
        if unit == 'minutes':
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        elif unit == 'hours':
            hours = minutes // 60
            return f"{hours} hour{'s' if hours != 1 else ''}"
        elif unit == 'days':
            days = minutes // (60 * 24)
            return f"{days} day{'s' if days != 1 else ''}"
        elif unit == 'weeks':
            weeks = minutes // (60 * 24 * 7)
            return f"{weeks} week{'s' if weeks != 1 else ''}"
        
        return f"{minutes} minutes"
    
    async def profitbattle_command(self, update: Update, context) -> int:
        """Start profit battle setup"""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name or f"User{user_id}"
        
        # Initialize battle session
        if not hasattr(self, 'battle_sessions'):
            self.battle_sessions = {}
        
        self.battle_sessions[user_id] = {
            'type': 'profit',
            'creator': username,
            'step': 'player_count',
            'messages_to_delete': []
        }
        
        # Store command message for cleanup
        self.battle_sessions[user_id]['messages_to_delete'].append(update.message.message_id)
        
        # Create player count selection keyboard
        keyboard = []
        for i in range(2, 9):  # 2-8 players
            keyboard.append([InlineKeyboardButton(
                f"⚔️ {i} Players Battle",
                callback_data=f"battle_players_{i}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = await update.message.reply_text(
            "💰 **PROFIT BATTLE SETUP** 💰\n\n"
            "⚔️ **Step 1/4: Choose Number of Players**\n\n"
            "Select how many traders will compete in this epic profit battle!\n"
            "More players = more competition = more glory! 🏆",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        self.battle_sessions[user_id]['messages_to_delete'].append(message.message_id)
        return BATTLE_PLAYER_COUNT
    
    async def battle_player_count_callback(self, update: Update, context) -> int:
        """Handle player count selection"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if user_id not in self.battle_sessions:
            await query.edit_message_text("❌ Battle session expired. Please start again with `/profitbattle`.")
            return ConversationHandler.END
        
        # Extract player count
        player_count = int(query.data.split('_')[2])
        self.battle_sessions[user_id]['player_count'] = player_count
        self.battle_sessions[user_id]['step'] = 'duration'
        
        # Create duration selection keyboard
        keyboard = [
            [InlineKeyboardButton("⚡ 30 Min Battle", callback_data="battle_duration_30m")],
            [InlineKeyboardButton("🔥 2 Hour Battle", callback_data="battle_duration_2h")],
            [InlineKeyboardButton("💪 1 Day Battle", callback_data="battle_duration_1d")],
            [InlineKeyboardButton("🏆 3 Days Battle", callback_data="battle_duration_3d")],
            [InlineKeyboardButton("🌟 1 Week Battle", callback_data="battle_duration_1w")],
            [InlineKeyboardButton("⚙️ Custom Time", callback_data="battle_duration_custom")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"💰 **PROFIT BATTLE SETUP** 💰\n\n"
            f"⚔️ **Step 2/4: Choose Battle Duration**\n\n"
            f"👥 **Players:** {player_count}\n\n"
            f"How long should this epic profit battle last?\n"
            f"Longer battles = more opportunities for comebacks! ⏰",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return BATTLE_DURATION
    
    async def battle_duration_callback(self, update: Update, context) -> int:
        """Handle duration selection"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if user_id not in self.battle_sessions:
            await query.edit_message_text("❌ Battle session expired. Please start again with `/profitbattle`.")
            return ConversationHandler.END
        
        # Check if custom duration is selected
        if query.data == "battle_duration_custom":
            await query.edit_message_text(
                f"💰 **PROFIT BATTLE SETUP** 💰\n\n"
                f"⚙️ **Step 2.5/4: Custom Battle Duration**\n\n"
                f"Choose your time unit and enter the duration:\n\n"
                f"**Examples:**\n"
                f"• `15m` = 15 minutes\n"
                f"• `4h` = 4 hours  \n"
                f"• `3d` = 3 days\n"
                f"• `2w` = 2 weeks\n\n"
                f"**Format:** `[number][unit]`\n"
                f"**Units:** `m`=minutes, `h`=hours, `d`=days, `w`=weeks\n\n"
                f"**Limits:** 5m minimum, 4w maximum\n\n"
                f"Enter your custom duration:",
                parse_mode=ParseMode.MARKDOWN
            )
            self.battle_sessions[user_id]['step'] = 'custom_duration'
            return BATTLE_DURATION
        
        # Extract duration code
        duration_code = query.data.split('_')[2]
        duration_result = self.parse_preset_duration(duration_code)
        
        if not duration_result:
            await query.edit_message_text("❌ Invalid duration selected. Please try again.")
            return ConversationHandler.END
        
        duration_minutes, duration_unit = duration_result
        duration_display = self.format_duration_display(duration_minutes, duration_unit)
        
        self.battle_sessions[user_id]['duration_minutes'] = duration_minutes
        self.battle_sessions[user_id]['duration_display'] = duration_display
        self.battle_sessions[user_id]['step'] = 'participants'
        
        player_count = self.battle_sessions[user_id]['player_count']
        
        await query.edit_message_text(
            f"💰 **PROFIT BATTLE SETUP** 💰\n\n"
            f"⚔️ **Step 3/4: Add Battle Participants**\n\n"
            f"👥 **Players:** {player_count}\n"
            f"⏰ **Duration:** {duration_display}\n\n"
            f"Now enter the usernames of traders you want to challenge!\n\n"
            f"**Format:** `@username1 @username2 @username3`\n"
            f"**Example:** `@dave @bob @bill @alice`\n\n"
            f"⚠️ **Important:** Include the @ symbol before each username!",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return BATTLE_PARTICIPANTS
    
    async def battle_custom_duration_input(self, update: Update, context) -> int:
        """Handle custom duration input"""
        user_id = update.effective_user.id
        if user_id not in self.battle_sessions:
            await update.message.reply_text("❌ Battle session expired. Please start again with `/profitbattle`.")
            return ConversationHandler.END
        
        # Store message for cleanup
        self.battle_sessions[user_id]['messages_to_delete'].append(update.message.message_id)
        
        # Parse custom duration
        duration_text = update.message.text.strip()
        duration_result = self.parse_duration(duration_text)
        
        if not duration_result:
            message = await update.message.reply_text(
                "❌ **Invalid Duration Format!**\n\n"
                "Please use the correct format:\n"
                "**Examples:** `15m`, `4h`, `3d`, `2w`\n\n"
                "**Units:** `m`=minutes, `h`=hours, `d`=days, `w`=weeks\n\n"
                "Try again:",
                parse_mode=ParseMode.MARKDOWN
            )
            self.battle_sessions[user_id]['messages_to_delete'].append(message.message_id)
            return BATTLE_DURATION
        
        duration_minutes, duration_unit = duration_result
        
        # Validate duration limits
        if duration_minutes < 5:  # 5 minutes minimum
            message = await update.message.reply_text(
                "❌ **Duration Too Short!**\n\n"
                "Minimum battle duration is 5 minutes.\n\n"
                "Try again:",
                parse_mode=ParseMode.MARKDOWN
            )
            self.battle_sessions[user_id]['messages_to_delete'].append(message.message_id)
            return BATTLE_DURATION
        
        if duration_minutes > 40320:  # 4 weeks maximum
            message = await update.message.reply_text(
                "❌ **Duration Too Long!**\n\n"
                "Maximum battle duration is 4 weeks.\n\n"
                "Try again:",
                parse_mode=ParseMode.MARKDOWN
            )
            self.battle_sessions[user_id]['messages_to_delete'].append(message.message_id)
            return BATTLE_DURATION
        
        # Store duration
        duration_display = self.format_duration_display(duration_minutes, duration_unit)
        self.battle_sessions[user_id]['duration_minutes'] = duration_minutes
        self.battle_sessions[user_id]['duration_display'] = duration_display
        self.battle_sessions[user_id]['step'] = 'participants'
        
        player_count = self.battle_sessions[user_id]['player_count']
        
        message = await update.message.reply_text(
            f"💰 **PROFIT BATTLE SETUP** 💰\n\n"
            f"⚔️ **Step 3/4: Add Battle Participants**\n\n"
            f"👥 **Players:** {player_count}\n"
            f"⏰ **Duration:** {duration_display}\n\n"
            f"Now enter the usernames of traders you want to challenge!\n\n"
            f"**Format:** `@username1 @username2 @username3`\n"
            f"**Example:** `@dave @bob @bill @alice`\n\n"
            f"⚠️ **Important:** Include the @ symbol before each username!",
            parse_mode=ParseMode.MARKDOWN
        )
        
        self.battle_sessions[user_id]['messages_to_delete'].append(message.message_id)
        return BATTLE_PARTICIPANTS
    
    async def battle_participants_input(self, update: Update, context) -> int:
        """Handle participants input"""
        user_id = update.effective_user.id
        if user_id not in self.battle_sessions:
            await update.message.reply_text("❌ Battle session expired. Please start again with `/profitbattle`.")
            return ConversationHandler.END
        
        # Store message for cleanup
        self.battle_sessions[user_id]['messages_to_delete'].append(update.message.message_id)
        
        # Parse participants
        participants_text = update.message.text.strip()
        participants = []
        
        # Extract usernames (with @ symbol)
        import re
        usernames = re.findall(r'@\w+', participants_text)
        
        if not usernames:
            message = await update.message.reply_text(
                "❌ **Invalid Format!**\n\n"
                "Please use the correct format with @ symbols:\n"
                "**Example:** `@dave @bob @bill`\n\n"
                "Try again:",
                parse_mode=ParseMode.MARKDOWN
            )
            self.battle_sessions[user_id]['messages_to_delete'].append(message.message_id)
            return BATTLE_PARTICIPANTS
        
        expected_count = self.battle_sessions[user_id]['player_count']
        creator = self.battle_sessions[user_id]['creator']
        
        # Add creator to participants if not already included
        creator_username = f"@{creator}" if not creator.startswith('@') else creator
        if creator_username not in usernames:
            usernames.append(creator_username)
        
        if len(usernames) != expected_count:
            message = await update.message.reply_text(
                f"❌ **Wrong Number of Participants!**\n\n"
                f"Expected: {expected_count} players\n"
                f"Found: {len(usernames)} players\n\n"
                f"Please enter exactly {expected_count} usernames including yourself:\n"
                f"**Example:** `@dave @bob @bill`",
                parse_mode=ParseMode.MARKDOWN
            )
            self.battle_sessions[user_id]['messages_to_delete'].append(message.message_id)
            return BATTLE_PARTICIPANTS
        
        # Store participants
        self.battle_sessions[user_id]['participants'] = usernames
        self.battle_sessions[user_id]['step'] = 'confirmation'
        
        # Create confirmation message
        player_count = self.battle_sessions[user_id]['player_count']
        duration_display = self.battle_sessions[user_id]['duration_display']
        
        participants_list = '\n'.join([f"⚔️ {username}" for username in usernames])
        
        keyboard = [
            [InlineKeyboardButton("⚔️ COMMENCE BATTLE!", callback_data="battle_start")],
            [InlineKeyboardButton("❌ Cancel Battle", callback_data="battle_cancel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = await update.message.reply_text(
            f"💰 **PROFIT BATTLE - FINAL CONFIRMATION** 💰\n\n"
            f"⚔️ **Battle Type:** Profit Battle\n"
            f"👥 **Players:** {player_count}\n"
            f"⏰ **Duration:** {duration_display}\n"
            f"🎯 **Objective:** Highest USD profit wins!\n\n"
            f"**⚔️ BATTLE PARTICIPANTS:**\n{participants_list}\n\n"
            f"**🏆 REWARDS:**\n"
            f"🥇 Winner: 100 Battle Points\n"
            f"🥈 2nd Place: 75 Battle Points\n"
            f"🥉 3rd Place: 50 Battle Points\n"
            f"🎖️ Participation: 25 Battle Points\n\n"
            f"Ready to begin this epic profit battle?",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        self.battle_sessions[user_id]['messages_to_delete'].append(message.message_id)
        return BATTLE_CONFIRMATION
    
    async def battle_start_callback(self, update: Update, context) -> int:
        """Handle battle start confirmation"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if user_id not in self.battle_sessions:
            await query.edit_message_text("❌ Battle session expired.")
            return ConversationHandler.END
        
        if query.data == "battle_cancel":
            await query.edit_message_text("❌ Battle cancelled.")
            await self.cleanup_battle_session(user_id, context, query.message.chat_id)
            return ConversationHandler.END
        
        # Create battle in database
        duration_minutes = self.battle_sessions[user_id]['duration_minutes']
        duration_display = self.battle_sessions[user_id]['duration_display']
        
        battle_data = {
            'type': 'profit',
            'creator': self.battle_sessions[user_id]['creator'],
            'participants': self.battle_sessions[user_id]['participants'],
            'duration_minutes': duration_minutes,
            'duration_display': duration_display,
            'start_date': datetime.now(timezone.utc),
            'end_date': datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
        }
        
        battle_id = db_manager.create_battle(battle_data)
        
        if not battle_id:
            await query.edit_message_text("❌ Failed to create battle. Please try again.")
            return ConversationHandler.END
        
        # Create epic gladiator-style battle announcement
        participants = self.battle_sessions[user_id]['participants']
        end_date = battle_data['end_date']
        
        participants_list = '\n'.join([f"⚔️ {username}" for username in participants])
        
        announcement = f"""
🏛️ **THE COLOSSEUM AWAKENS!** 🏛️
⚔️ **PROFIT GLADIATORS ENTER THE ARENA!** ⚔️

💰 **BATTLE TYPE:** Epic Profit Gladiator Combat
⏰ **DURATION:** {duration_display}
🎯 **OBJECTIVE:** Earn the highest USD profit and claim glory!

**⚔️ GLADIATORS ENTERING THE ARENA:**
{participants_list}

**🏛️ ARENA CLOSES:** {end_date.strftime('%d/%m/%Y at %H:%M UTC')}

**⚡ GLADIATOR CODE:**
• Only official PNL submissions count toward victory
• Screenshots required for all battle trades
• Combat period strictly enforced
• Updates posted only when leads change
• Victory announcements in gladiator style

**🔥 LET THE PROFIT COMBAT BEGIN!**
*"Are you not entertained? TRADE!"* 🏆💰

*Gladiator Arena ID: {battle_id}*
        """
        
        await query.edit_message_text(announcement.strip(), parse_mode=ParseMode.MARKDOWN)
        
        # Post to all configured channels
        await self.post_to_all_channels(context, announcement.strip())
        
        # Cleanup session
        await self.cleanup_battle_session(user_id, context, query.message.chat_id)
        
        return ConversationHandler.END
    
    async def cleanup_battle_session(self, user_id: int, context=None, chat_id=None):
        """Clean up battle session messages"""
        if user_id in self.battle_sessions:
            messages_to_delete = self.battle_sessions[user_id].get('messages_to_delete', [])
            for message_id in messages_to_delete:
                try:
                    if context and chat_id:
                        await context.bot.delete_message(
                            chat_id=chat_id,
                            message_id=message_id
                        )
                except Exception as e:
                    logger.warning(f"Could not delete message {message_id}: {e}")
            
            del self.battle_sessions[user_id]
    
    async def post_to_all_channels(self, context, message: str):
        """Post message to all configured channels"""
        for channel_config in CHANNELS_TO_POST:
            try:
                if channel_config['thread_id']:
                    await context.bot.send_message(
                        chat_id=channel_config['channel_id'],
                        text=message,
                        message_thread_id=channel_config['thread_id'],
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await context.bot.send_message(
                        chat_id=channel_config['channel_id'],
                        text=message,
                        parse_mode=ParseMode.MARKDOWN
                    )
            except Exception as e:
                logger.warning(f"Could not post to channel {channel_config}: {e}")

    async def tradewar_command(self, update: Update, context) -> int:
        """Start trade war setup"""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name or f"User{user_id}"
        
        # Initialize battle session
        if not hasattr(self, 'battle_sessions'):
            self.battle_sessions = {}
        
        self.battle_sessions[user_id] = {
            'type': 'trade',
            'creator': username,
            'step': 'player_count',
            'messages_to_delete': []
        }
        
        # Store command message for cleanup
        self.battle_sessions[user_id]['messages_to_delete'].append(update.message.message_id)
        
        # Create player count selection keyboard
        keyboard = []
        for i in range(2, 9):  # 2-8 players
            keyboard.append([InlineKeyboardButton(
                f"⚡ {i} Players War",
                callback_data=f"tradewar_players_{i}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = await update.message.reply_text(
            "⚡ **TRADE WAR SETUP** ⚡\n\n"
            "🔥 **Step 1/4: Choose Number of Players**\n\n"
            "Select how many traders will compete in this epic trade count war!\n"
            "More players = more chaos = more excitement! 🚀",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        self.battle_sessions[user_id]['messages_to_delete'].append(message.message_id)
        return BATTLE_PLAYER_COUNT
    
    async def tradewar_player_count_callback(self, update: Update, context) -> int:
        """Handle trade war player count selection"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if user_id not in self.battle_sessions:
            await query.edit_message_text("❌ Battle session expired. Please start again with `/tradewar`.")
            return ConversationHandler.END
        
        # Extract player count
        player_count = int(query.data.split('_')[2])
        self.battle_sessions[user_id]['player_count'] = player_count
        self.battle_sessions[user_id]['step'] = 'duration'
        
        # Create duration selection keyboard
        keyboard = [
            [InlineKeyboardButton("⚡ 30 Min War", callback_data="tradewar_duration_30m")],
            [InlineKeyboardButton("🔥 2 Hour War", callback_data="tradewar_duration_2h")],
            [InlineKeyboardButton("💪 1 Day War", callback_data="tradewar_duration_1d")],
            [InlineKeyboardButton("🚀 3 Days War", callback_data="tradewar_duration_3d")],
            [InlineKeyboardButton("🌟 1 Week War", callback_data="tradewar_duration_1w")],
            [InlineKeyboardButton("⚙️ Custom Time", callback_data="tradewar_duration_custom")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"⚡ **TRADE WAR SETUP** ⚡\n\n"
            f"🔥 **Step 2/4: Choose War Duration**\n\n"
            f"👥 **Warriors:** {player_count}\n\n"
            f"How long should this epic trade war last?\n"
            f"Longer wars = more opportunities for massive trade counts! 📈",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return BATTLE_DURATION
    
    async def tradewar_duration_callback(self, update: Update, context) -> int:
        """Handle trade war duration selection"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if user_id not in self.battle_sessions:
            await query.edit_message_text("❌ Battle session expired. Please start again with `/tradewar`.")
            return ConversationHandler.END
        
        # Check if custom duration is selected
        if query.data == "tradewar_duration_custom":
            await query.edit_message_text(
                f"⚡ **TRADE WAR SETUP** ⚡\n\n"
                f"⚙️ **Step 2.5/4: Custom War Duration**\n\n"
                f"Choose your time unit and enter the duration:\n\n"
                f"**Examples:**\n"
                f"• `15m` = 15 minutes of intense trading\n"
                f"• `4h` = 4 hours of trade warfare  \n"
                f"• `3d` = 3 days of trading combat\n"
                f"• `2w` = 2 weeks of epic war\n\n"
                f"**Format:** `[number][unit]`\n"
                f"**Units:** `m`=minutes, `h`=hours, `d`=days, `w`=weeks\n\n"
                f"**Limits:** 5m minimum, 4w maximum\n\n"
                f"Enter your custom war duration:",
                parse_mode=ParseMode.MARKDOWN
            )
            self.battle_sessions[user_id]['step'] = 'custom_duration'
            return BATTLE_DURATION
        
        # Extract duration code
        duration_code = query.data.split('_')[2]
        duration_result = self.parse_preset_duration(duration_code)
        
        if not duration_result:
            await query.edit_message_text("❌ Invalid duration selected. Please try again.")
            return ConversationHandler.END
        
        duration_minutes, duration_unit = duration_result
        duration_display = self.format_duration_display(duration_minutes, duration_unit)
        
        self.battle_sessions[user_id]['duration_minutes'] = duration_minutes
        self.battle_sessions[user_id]['duration_display'] = duration_display
        self.battle_sessions[user_id]['step'] = 'participants'
        
        player_count = self.battle_sessions[user_id]['player_count']
        
        await query.edit_message_text(
            f"⚡ **TRADE WAR SETUP** ⚡\n\n"
            f"🔥 **Step 3/4: Add War Participants**\n\n"
            f"👥 **Warriors:** {player_count}\n"
            f"⏰ **Duration:** {duration_display}\n\n"
            f"Now enter the usernames of traders you want to challenge!\n\n"
            f"**Format:** `@username1 @username2 @username3`\n"
            f"**Example:** `@dave @bob @bill @alice`\n\n"
            f"⚠️ **Important:** Include the @ symbol before each username!",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return BATTLE_PARTICIPANTS
    
    async def tradewar_custom_duration_input(self, update: Update, context) -> int:
        """Handle custom duration input for trade wars"""
        user_id = update.effective_user.id
        if user_id not in self.battle_sessions:
            await update.message.reply_text("❌ Battle session expired. Please start again with `/tradewar`.")
            return ConversationHandler.END
        
        # Store message for cleanup
        self.battle_sessions[user_id]['messages_to_delete'].append(update.message.message_id)
        
        # Parse custom duration
        duration_text = update.message.text.strip()
        duration_result = self.parse_duration(duration_text)
        
        if not duration_result:
            message = await update.message.reply_text(
                "❌ **Invalid War Duration Format!**\n\n"
                "Please use the correct format:\n"
                "**Examples:** `15m`, `4h`, `3d`, `2w`\n\n"
                "**Units:** `m`=minutes, `h`=hours, `d`=days, `w`=weeks\n\n"
                "Try again:",
                parse_mode=ParseMode.MARKDOWN
            )
            self.battle_sessions[user_id]['messages_to_delete'].append(message.message_id)
            return BATTLE_DURATION
        
        duration_minutes, duration_unit = duration_result
        
        # Validate duration limits
        if duration_minutes < 5:  # 5 minutes minimum
            message = await update.message.reply_text(
                "❌ **War Duration Too Short!**\n\n"
                "Minimum trade war duration is 5 minutes.\n"
                "Even the fastest gladiators need time to trade!\n\n"
                "Try again:",
                parse_mode=ParseMode.MARKDOWN
            )
            self.battle_sessions[user_id]['messages_to_delete'].append(message.message_id)
            return BATTLE_DURATION
        
        if duration_minutes > 40320:  # 4 weeks maximum
            message = await update.message.reply_text(
                "❌ **War Duration Too Long!**\n\n"
                "Maximum trade war duration is 4 weeks.\n"
                "Even epic wars must end eventually!\n\n"
                "Try again:",
                parse_mode=ParseMode.MARKDOWN
            )
            self.battle_sessions[user_id]['messages_to_delete'].append(message.message_id)
            return BATTLE_DURATION
        
        # Store duration
        duration_display = self.format_duration_display(duration_minutes, duration_unit)
        self.battle_sessions[user_id]['duration_minutes'] = duration_minutes
        self.battle_sessions[user_id]['duration_display'] = duration_display
        self.battle_sessions[user_id]['step'] = 'participants'
        
        player_count = self.battle_sessions[user_id]['player_count']
        
        message = await update.message.reply_text(
            f"⚡ **TRADE WAR SETUP** ⚡\n\n"
            f"🔥 **Step 3/4: Add War Participants**\n\n"
            f"👥 **Warriors:** {player_count}\n"
            f"⏰ **Duration:** {duration_display}\n\n"
            f"Now enter the usernames of traders you want to challenge!\n\n"
            f"**Format:** `@username1 @username2 @username3`\n"
            f"**Example:** `@dave @bob @bill @alice`\n\n"
            f"⚠️ **Important:** Include the @ symbol before each username!",
            parse_mode=ParseMode.MARKDOWN
        )
        
        self.battle_sessions[user_id]['messages_to_delete'].append(message.message_id)
        return BATTLE_PARTICIPANTS
    
    async def tradewar_participants_input(self, update: Update, context) -> int:
        """Handle trade war participants input"""
        user_id = update.effective_user.id
        if user_id not in self.battle_sessions:
            await update.message.reply_text("❌ Battle session expired. Please start again with `/tradewar`.")
            return ConversationHandler.END
        
        # Store message for cleanup
        self.battle_sessions[user_id]['messages_to_delete'].append(update.message.message_id)
        
        # Parse participants
        participants_text = update.message.text.strip()
        participants = []
        
        # Extract usernames (with @ symbol)
        import re
        usernames = re.findall(r'@\w+', participants_text)
        
        if not usernames:
            message = await update.message.reply_text(
                "❌ **Invalid Format!**\n\n"
                "Please use the correct format with @ symbols:\n"
                "**Example:** `@dave @bob @bill`\n\n"
                "Try again:",
                parse_mode=ParseMode.MARKDOWN
            )
            self.battle_sessions[user_id]['messages_to_delete'].append(message.message_id)
            return BATTLE_PARTICIPANTS
        
        expected_count = self.battle_sessions[user_id]['player_count']
        creator = self.battle_sessions[user_id]['creator']
        
        # Add creator to participants if not already included
        creator_username = f"@{creator}" if not creator.startswith('@') else creator
        if creator_username not in usernames:
            usernames.append(creator_username)
        
        if len(usernames) != expected_count:
            message = await update.message.reply_text(
                f"❌ **Wrong Number of Participants!**\n\n"
                f"Expected: {expected_count} players\n"
                f"Found: {len(usernames)} players\n\n"
                f"Please enter exactly {expected_count} usernames including yourself:\n"
                f"**Example:** `@dave @bob @bill`",
                parse_mode=ParseMode.MARKDOWN
            )
            self.battle_sessions[user_id]['messages_to_delete'].append(message.message_id)
            return BATTLE_PARTICIPANTS
        
        # Store participants
        self.battle_sessions[user_id]['participants'] = usernames
        self.battle_sessions[user_id]['step'] = 'confirmation'
        
        # Create confirmation message
        player_count = self.battle_sessions[user_id]['player_count']
        duration_display = self.battle_sessions[user_id]['duration_display']
        
        participants_list = '\n'.join([f"⚡ {username}" for username in usernames])
        
        keyboard = [
            [InlineKeyboardButton("⚡ COMMENCE WAR!", callback_data="tradewar_start")],
            [InlineKeyboardButton("❌ Cancel War", callback_data="tradewar_cancel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = await update.message.reply_text(
            f"⚡ **TRADE WAR - FINAL CONFIRMATION** ⚡\n\n"
            f"🔥 **Battle Type:** Trade War\n"
            f"👥 **Warriors:** {player_count}\n"
            f"⏰ **Duration:** {duration_display}\n"
            f"🎯 **Objective:** Highest trade count wins!\n\n"
            f"**⚡ WAR PARTICIPANTS:**\n{participants_list}\n\n"
            f"**🏆 REWARDS:**\n"
            f"🥇 Winner: 100 Battle Points\n"
            f"🥈 2nd Place: 75 Battle Points\n"
            f"🥉 3rd Place: 50 Battle Points\n"
            f"🎖️ Participation: 25 Battle Points\n\n"
            f"Ready to begin this epic trade war?",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        self.battle_sessions[user_id]['messages_to_delete'].append(message.message_id)
        return BATTLE_CONFIRMATION
    
    async def tradewar_start_callback(self, update: Update, context) -> int:
        """Handle trade war start confirmation"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if user_id not in self.battle_sessions:
            await query.edit_message_text("❌ Battle session expired.")
            return ConversationHandler.END
        
        if query.data == "tradewar_cancel":
            await query.edit_message_text("❌ Trade war cancelled.")
            await self.cleanup_battle_session(user_id, context, query.message.chat_id)
            return ConversationHandler.END
        
        # Create battle in database
        duration_minutes = self.battle_sessions[user_id]['duration_minutes']
        duration_display = self.battle_sessions[user_id]['duration_display']
        
        battle_data = {
            'type': 'trade',
            'creator': self.battle_sessions[user_id]['creator'],
            'participants': self.battle_sessions[user_id]['participants'],
            'duration_minutes': duration_minutes,
            'duration_display': duration_display,
            'start_date': datetime.now(timezone.utc),
            'end_date': datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
        }
        
        battle_id = db_manager.create_battle(battle_data)
        
        if not battle_id:
            await query.edit_message_text("❌ Failed to create trade war. Please try again.")
            return ConversationHandler.END
        
        # Create epic gladiator-style trade war announcement
        participants = self.battle_sessions[user_id]['participants']
        end_date = battle_data['end_date']
        
        participants_list = '\n'.join([f"⚡ {username}" for username in participants])
        
        announcement = f"""
🎺 **EPIC TRADE WAR COMMENCES!** 🎺

⚡ **BATTLE DECLARED!** ⚡

🔥 **WAR TYPE:** Epic Trade Count Gladiator War
👥 **WARRIORS:** {len(participants)}
⏰ **DURATION:** {duration_display}
🎯 **OBJECTIVE:** Most trades executed wins!

**⚡ BRAVE WARRIORS ENTERING THE ARENA:**
{participants_list}

🏆 **GLORY AWAITS:**
🥇 Champion: 100 Battle Points
🥈 Second: 75 Battle Points  
🥉 Third: 50 Battle Points
🎖️ All: 25 Battle Points

**⚔️ BATTLE ENDS:** {end_date.strftime('%Y-%m-%d %H:%M UTC')}

**🔥 LET THE TRADE COUNT WAR BEGIN!**

*May the most dedicated trader claim eternal glory!*
⚡ The arena drums beat for battle! ⚡

---
🏛️ The trade count war intensifies!
*Track your progress and dominate the competition!*
        """
        
        await query.edit_message_text(announcement.strip(), parse_mode=ParseMode.MARKDOWN)
        
        # Post to all configured channels
        await self.post_to_all_channels(context, announcement.strip())
        
        # Cleanup session
        await self.cleanup_battle_session(user_id, context, query.message.chat_id)
        
        return ConversationHandler.END

    def setup_handlers(self):
        """Set up all command and message handlers"""
        # Submission conversation handler
        submit_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('submit', self.submit_command)],
            states={
                SCREENSHOT_UPLOAD: [MessageHandler(filters.PHOTO, self.screenshot_upload)],
                CURRENCY_SELECTION: [CallbackQueryHandler(self.currency_selection_callback, pattern="^currency_")],
                TICKER_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ticker_input)],
                INVESTMENT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.investment_input)],
                PROFIT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.profit_input)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel_command)],
            per_chat=True,
            per_user=True
        )
        
        # Auto-submit conversation handler (for photo detection)
        auto_submit_conv_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.auto_submit_callback, pattern="^auto_submit_")],
            states={
                CURRENCY_SELECTION: [CallbackQueryHandler(self.currency_selection_callback, pattern="^currency_")],
                TICKER_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ticker_input)],
                INVESTMENT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.investment_input)],
                PROFIT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.profit_input)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel_command)],
            per_chat=True,
            per_user=True
        )
        
        # Profit battle conversation handler
        profitbattle_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('profitbattle', self.profitbattle_command)],
            states={
                BATTLE_PLAYER_COUNT: [CallbackQueryHandler(self.battle_player_count_callback, pattern="^battle_players_")],
                BATTLE_DURATION: [
                    CallbackQueryHandler(self.battle_duration_callback, pattern="^battle_duration_"),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.battle_custom_duration_input)
                ],
                BATTLE_PARTICIPANTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.battle_participants_input)],
                BATTLE_CONFIRMATION: [CallbackQueryHandler(self.battle_start_callback, pattern="^battle_")]
            },
            fallbacks=[CommandHandler('cancel', self.cancel_command)],
            per_chat=True,
            per_user=True
        )
        
        # Trade war conversation handler
        tradewar_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('tradewar', self.tradewar_command)],
            states={
                BATTLE_PLAYER_COUNT: [CallbackQueryHandler(self.tradewar_player_count_callback, pattern="^tradewar_players_")],
                BATTLE_DURATION: [
                    CallbackQueryHandler(self.tradewar_duration_callback, pattern="^tradewar_duration_"),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.tradewar_custom_duration_input)
                ],
                BATTLE_PARTICIPANTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.tradewar_participants_input)],
                BATTLE_CONFIRMATION: [CallbackQueryHandler(self.tradewar_start_callback, pattern="^tradewar_")]
            },
            fallbacks=[CommandHandler('cancel', self.cancel_command)],
            per_chat=True,
            per_user=True
        )

        # Add handlers to application - ORDER MATTERS FOR MOBILE!
        self.application.add_handler(CommandHandler('start', self.start_command))
        self.application.add_handler(CommandHandler('help', self.help_command))
        
        # Photo auto-detection MUST be first (group=0) for mobile compatibility
        self.application.add_handler(MessageHandler(
            (filters.PHOTO | filters.Document.IMAGE) & ~filters.COMMAND, 
            self.photo_auto_detect
        ), group=0)
        
        # Conversation handlers in higher group
        self.application.add_handler(submit_conv_handler, group=1)
        self.application.add_handler(auto_submit_conv_handler, group=1)
        self.application.add_handler(profitbattle_conv_handler, group=1)
        self.application.add_handler(tradewar_conv_handler, group=1)
        self.application.add_handler(CommandHandler('leaderboard', self.leaderboard_command))
        self.application.add_handler(CommandHandler('monthlyleaderboard', self.monthly_leaderboard_command))
        self.application.add_handler(CommandHandler('weeklyleaderboard', self.weekly_leaderboard_command))
        self.application.add_handler(CommandHandler('dailyleaderboard', self.daily_leaderboard_command))
        self.application.add_handler(CommandHandler('tradeleader', self.trade_leader_command))
        self.application.add_handler(CommandHandler('profitgoat', self.profit_goat_command))
        self.application.add_handler(CommandHandler('pnlreport', self.pnl_report_command))
        self.application.add_handler(CommandHandler('mystats', self.mystats_command))
        self.application.add_handler(CommandHandler('myhistory', self.myhistory_command))
        self.application.add_handler(CommandHandler('compare', self.compare_command))
        self.application.add_handler(CommandHandler('roi', self.roi_command))
        self.application.add_handler(CommandHandler('tokenleader', self.tokenleader_command))
        self.application.add_handler(CommandHandler('tokenstats', self.tokenstats_command))
        self.application.add_handler(CommandHandler('trendingcoins', self.trendingcoins_command))
        self.application.add_handler(CommandHandler('bigballer', self.bigballer_command))
        self.application.add_handler(CommandHandler('percentking', self.percentking_command))
        self.application.add_handler(CommandHandler('consistenttrader', self.consistenttrader_command))
        self.application.add_handler(CommandHandler('lossleader', self.lossleader_command))
        self.application.add_handler(CommandHandler('smallcap', self.smallcap_command))
        self.application.add_handler(CommandHandler('midcap', self.midcap_command))
        self.application.add_handler(CommandHandler('largecap', self.largecap_command))
        self.application.add_handler(CommandHandler('achievements', self.achievements_command))
        self.application.add_handler(CommandHandler('streaks', self.streaks_command))
        self.application.add_handler(CommandHandler('milestones', self.milestones_command))
        self.application.add_handler(CommandHandler('randomtrade', self.randomtrade_command))
        self.application.add_handler(CommandHandler('todaysbiggest', self.todaysbiggest_command))
        self.application.add_handler(CommandHandler('hall_of_fame', self.hall_of_fame_command))
        self.application.add_handler(CommandHandler('marketsentiment', self.marketsentiment_command))
        self.application.add_handler(CommandHandler('popularityindex', self.popularityindex_command))
        self.application.add_handler(CommandHandler('profitability', self.profitability_command))
        self.application.add_handler(CommandHandler('timetrendz', self.timetrendz_command))
        self.application.add_handler(CommandHandler('search', self.search_command))
        self.application.add_handler(CommandHandler('finduser', self.finduser_command))
        self.application.add_handler(CommandHandler('topgainer', self.topgainer_command))
        self.application.add_handler(CommandHandler('export', self.export_command))
        self.application.add_handler(CommandHandler('portfolio', self.portfolio_command))
        self.application.add_handler(CommandHandler('monthlyreport', self.monthlyreport_command))
        self.application.add_handler(CommandHandler('filters', self.filters_command))
        self.application.add_handler(CommandHandler('lore', self.lore_command))
        self.application.add_handler(CommandHandler('pnlguide', self.pnlguide_command))
        self.application.add_handler(CommandHandler('loretotalprofit', self.loretotalprofit_command))
        self.application.add_handler(CommandHandler('battlerules', self.battlerules_command))
        self.application.add_handler(CommandHandler('battlpoints', self.battlpoints_command))
        self.application.add_handler(CommandHandler('battleleaderboard', self.battleleaderboard_command))
    
    def initialize(self):
        """Initialize the bot and database connection"""
        # Connect to database
        if not db_manager.connect():
            logger.error("Failed to connect to database. Exiting...")
            return False
        
        # Create application
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Set up handlers
        self.setup_handlers()
        
        logger.info("Bot initialized successfully")
        return True
    

    
    def run(self):
        """Run the bot"""
        if not self.initialize():
            return
        
        logger.info("Starting Telegram PNL Bot...")
        logger.info("🏛️ Gladiator Battle Monitoring System activated! ⚔️")
        
        try:
            # Start polling - this will run indefinitely
            self.application.run_polling(
                poll_interval=1.0,
                timeout=10
            )
        except KeyboardInterrupt:
            logger.info("Stopping bot...")
        finally:
            db_manager.close_connection()

    # ===== BATTLE MONITORING SYSTEM =====
    # Note: Advanced monitoring features can be added later
    # For now, battles work manually without background monitoring
    
    # Battle monitoring methods simplified for compatibility
    def check_battle_status(self):
        """Simple battle status check - can be called manually"""
        try:
            # This method can be enhanced later with proper async support
            logger.info("Battle status check - manual mode")
            return True
        except Exception as e:
            logger.error(f"Error checking battle status: {e}")
            return False
    
    def get_pnl_channel_id(self):
        """Get the PNL channel ID from configuration"""
        # This should return the specific PNL channel ID
        # For now, return the first configured channel
        if CHANNELS_TO_POST:
            return CHANNELS_TO_POST[0]['id']
        return None
    
    async def post_to_pnl_channel(self, context, message: str, channel_id: str):
        """Post message only to PNL channel"""
        if not channel_id:
            return
            
        try:
            await context.bot.send_message(
                chat_id=channel_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.warning(f"Could not post to PNL channel {channel_id}: {e}")
    
    def format_leader_change_update(self, battle, new_leader, action_details):
        """Format leader change update for PNL channel"""
        battle_type = battle.get('type', 'profit')
        duration_display = battle.get('duration_display', 'Unknown')
        
        if battle_type == 'profit':
            battle_emoji = "💰"
            battle_name = "PROFIT GLADIATOR"
            score = action_details.get('new_score', 0)
            score_text = f"${score:,.2f}"
            message_style = "profit dominance"
        else:
            battle_emoji = "⚡"
            battle_name = "TRADE WAR GLADIATOR"
            score = action_details.get('new_score', 0)
            score_text = f"{int(score)} trades"
            message_style = "volume supremacy"
        
        return f"""
🏛️ **GLADIATOR ARENA UPDATE!** 🏛️

{battle_emoji} **NEW LEADER EMERGES!** {battle_emoji}

👑 **@{new_leader}** has seized the arena throne!
📊 **Score:** {score_text}
⚔️ **Arena:** {battle_name} Battle
⏰ **Duration:** {duration_display}

*The crowd roars as a new champion takes command!*
*Will this {message_style} hold until the arena closes?*

🔥 **Keep trading, gladiators!** 🔥
        """.strip()
    
    def format_new_trade_update(self, battle, action_details):
        """Format new trade update for PNL channel"""
        trader = action_details.get('trader')
        trade_profit = action_details.get('profit_usd', 0)
        battle_type = battle.get('type', 'profit')
        
        if battle_type == 'profit':
            if trade_profit > 1000:  # Only show significant trades
                return f"""
⚔️ **MASSIVE GLADIATOR STRIKE!** ⚔️

💰 **@{trader}** just landed a ${trade_profit:,.2f} profit hit!
🏛️ The arena trembles with this powerful move!

*Will this be enough to claim the champion's throne?*
                """.strip()
        else:  # trade war
            return f"""
⚡ **GLADIATOR STRIKES AGAIN!** ⚡

🔥 **@{trader}** adds another trade to their arsenal!
🏛️ The volume war intensifies!

*Every trade counts in this epic battle!*
            """.strip()
        
        return None  # Don't post small trades
    
    async def check_battle_completions(self, context):
        """Check for expired battles and complete them"""
        try:
            expired_battles = db_manager.get_expired_battles()
            
            for battle in expired_battles:
                battle_id = str(battle['_id'])
                
                # Complete the battle
                results = db_manager.complete_battle(battle_id)
                
                if results:
                    # Create victory announcement
                    victory_message = self.format_victory_announcement(results)
                    
                    # Post to all channels
                    await self.post_to_all_channels(context, victory_message)
                    
                    logger.info(f"Completed battle {battle_id}")
                
        except Exception as e:
            logger.error(f"Error in battle completion check: {e}")
    
    def format_profit_battle_update(self, battle, stats, hours_remaining):
        """Format hourly update for profit battles"""
        battle_type = "💰 PROFIT BATTLE"
        duration = battle.get('duration_days', 0)
        
        # Sort participants by profit
        sorted_stats = sorted(
            stats.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        # Create leaderboard
        leaderboard = []
        for rank, (username, user_stats) in enumerate(sorted_stats[:5], 1):
            profit = user_stats['score']
            trades = user_stats['total_trades']
            emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🎖️"
            
            leaderboard.append(
                f"{emoji} **#{rank} @{username}**\n"
                f"    💰 ${profit:,.2f} | 📊 {trades} trades"
            )
        
        leaderboard_text = '\n'.join(leaderboard)
        
        return f"""
⚔️ **{battle_type} - HOURLY UPDATE** ⚔️

⏰ **TIME REMAINING:** {hours_remaining} hours
🎯 **OBJECTIVE:** Highest USD profit wins!

**📊 CURRENT LEADERBOARD:**
{leaderboard_text}

**⚡ BATTLE STATUS:**
• Battle duration: {duration} days
• Participants: {len(sorted_stats)}
• Total trades submitted: {sum(s[1]['total_trades'] for s in sorted_stats)}

🔥 **Keep trading! The battle continues!** 🔥
        """.strip()
    
    def format_trade_war_update(self, battle, stats, hours_remaining):
        """Format hourly update for trade wars"""
        battle_type = "⚡ TRADE WAR"
        duration = battle.get('duration_days', 0)
        
        # Sort participants by trade count
        sorted_stats = sorted(
            stats.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        # Create leaderboard
        leaderboard = []
        for rank, (username, user_stats) in enumerate(sorted_stats[:5], 1):
            trades = user_stats['score']
            profit = user_stats['total_profit_usd']
            emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🎖️"
            
            leaderboard.append(
                f"{emoji} **#{rank} @{username}**\n"
                f"    ⚡ {trades} trades | 💰 ${profit:,.2f}"
            )
        
        leaderboard_text = '\n'.join(leaderboard)
        
        return f"""
⚡ **{battle_type} - HOURLY UPDATE** ⚡

⏰ **TIME REMAINING:** {hours_remaining} hours
🎯 **OBJECTIVE:** Most trades wins!

**📊 CURRENT LEADERBOARD:**
{leaderboard_text}

**🚀 WAR STATUS:**
• War duration: {duration} days
• Warriors: {len(sorted_stats)}
• Total trades: {sum(s[1]['total_trades'] for s in sorted_stats)} trades

🔥 **Keep trading! Trade count is victory!** 🔥
        """.strip()
    
    def format_victory_announcement(self, results):
        """Format epic gladiator-style victory announcement"""
        battle_type = results.get('battle_type', 'profit')
        rankings = results.get('rankings', [])
        battle_duration = results.get('duration_display', 'Unknown')
        
        if not rankings:
            return "🏛️ The arena stands empty - no gladiators answered the call to battle."
        
        # Get winner
        winner = rankings[0]
        winner_username = winner['username']
        winner_score = winner['score']
        
        # Battle type specific formatting
        if battle_type == 'profit':
            battle_emoji = "💰"
            arena_type = "PROFIT GLADIATOR ARENA"
            score_text = f"${winner_score:,.2f} USD"
            victory_title = "PROFIT CHAMPION OF THE COLOSSEUM"
            weapon = "profit sword"
            victory_cry = "PROFIT REIGNS SUPREME!"
        else:  # trade war
            battle_emoji = "⚡"
            arena_type = "TRADE COUNT GLADIATOR ARENA"
            score_text = f"{int(winner_score)} trades"
            victory_title = "TRADE COUNT EMPEROR OF THE ARENA"
            weapon = "trade count spear"
            victory_cry = "TRADE COUNT IS ETERNAL!"
        
        # Create epic rankings display
        ranking_lines = []
        rank_titles = {
            1: "👑 EMPEROR",
            2: "🥈 GENERAL", 
            3: "🥉 CENTURION",
            4: "🎖️ LEGIONNAIRE",
            5: "🎖️ SOLDIER"
        }
        
        for rank_data in rankings[:5]:  # Top 5
            rank = rank_data['rank']
            username = rank_data['username']
            score = rank_data['score']
            points_earned = rank_data['points_earned']
            
            rank_title = rank_titles.get(rank, "🎖️ WARRIOR")
            
            if battle_type == 'profit':
                score_display = f"${score:,.2f}"
            else:
                score_display = f"{int(score)} trades"
            
            ranking_lines.append(
                f"{rank_title} **@{username}**\n"
                f"    ⚔️ {score_display} | 🏆 +{points_earned} glory points"
            )
        
        rankings_text = '\n'.join(ranking_lines)
        
        # Create detailed champion stats
        winner_stats = winner.get('stats', {})
        total_trades = winner_stats.get('total_trades', 0)
        win_rate = winner_stats.get('win_rate', 0)
        
        champion_details = f"""
**🏛️ CHAMPION'S BATTLE RECORD:**
⚔️ Trades Executed: {total_trades}
🎯 Victory Rate: {win_rate:.1f}%
🏆 Glory Points Earned: {winner['points_earned']}
⏰ Arena Duration: {battle_duration}
        """.strip()
        
        # Epic gladiator-style announcement
        return f"""
🏛️ **THE COLOSSEUM ROARS WITH VICTORY!** 🏛️
⚔️ **{arena_type} CONCLUDES IN EPIC TRIUMPH!** ⚔️

{battle_emoji} **{victory_cry}** {battle_emoji}

🎺🎺🎺 **VICTORY FANFARE** 🎺🎺🎺

👑 **HAIL THE CHAMPION: @{winner_username}!** 👑
🏆 **{victory_title}**
⚔️ **Final Battle Score: {score_text}**
🛡️ **Wielding the mighty {weapon} with unmatched skill!**

{champion_details}

🏛️ **HALL OF GLADIATOR HONORS:** 🏛️
{rankings_text}

⚡ **ARENA STATISTICS:**
🏛️ Gladiators Who Entered: {len(rankings)}
🏆 Total Glory Points Awarded: {sum(r['points_earned'] for r in rankings)}
🔥 Epic Battles Fought: LEGENDARY STATUS!

🎪 **THE CROWD CHANTS THE CHAMPION'S NAME!** 🎪
*"@{winner_username}! @{winner_username}! @{winner_username}!"*

Your courage in the arena has brought eternal glory!
The gods of trading smile upon all who fought with honor!

⚔️ *Ready for the next gladiator battle? Use `/profitbattle` or `/tradewar`!* ⚔️
🏆 *Check `/battlpoints` to see your gladiator ranking!* 🏆

*"Those who dare to trade, dare to win!"*
        """.strip()


def main():
    """Main function"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set")
        return
    
    bot = TelegramPNLBot()
    bot.run()


if __name__ == '__main__':
    main() 