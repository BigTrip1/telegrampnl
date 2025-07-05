"""
Database configuration and operations for the Telegram PNL Bot
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import re

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, host: str = "localhost", port: int = 27017, database: str = "telegram"):
        """Initialize database connection"""
        self.host = host
        self.port = port
        self.database_name = database
        self.client = None
        self.db = None
        self.pnls_collection = None
        self.battles_collection = None
        self.battle_points_collection = None
        
    def connect(self) -> bool:
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.host, self.port, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.pnls_collection = self.db['pnls']
            self.battles_collection = self.db['battles']
            self.battle_points_collection = self.db['battle_points']
            logger.info(f"Successfully connected to MongoDB at {self.host}:{self.port}")
            return True
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            return False
    
    def create_username_match_conditions(self, user_id=None, username=None):
        """Create comprehensive username matching conditions for database queries"""
        conditions = []
        
        # Add user_id matches if provided
        if user_id:
            conditions.extend([
                {'user_id': str(user_id)},
                {'user_id': user_id}  # Handle both string and int user_id
            ])
        
        # Add username matches if provided
        if username:
            # Clean username (remove @ if present)
            clean_username = username.replace('@', '') if username.startswith('@') else username
            
            # Add all possible username variations
            conditions.extend([
                {'username': username},                    # Exact match
                {'username': f'@{clean_username}'},        # With @ prefix
                {'username': clean_username},              # Without @ prefix
                {'username': {'$regex': f'^@?{re.escape(clean_username)}$', '$options': 'i'}}  # Case insensitive regex
            ])
        
        return conditions
    
    def create_username_match_query(self, user_id=None, username=None):
        """Create a MongoDB query for username matching"""
        conditions = self.create_username_match_conditions(user_id, username)
        
        if not conditions:
            return {}
        
        if len(conditions) == 1:
            return conditions[0]
        
        return {'$or': conditions}
    
    def insert_pnl_record(self, record: Dict[str, Any]) -> bool:
        """Insert a PNL record into the database"""
        try:
            # Add timestamp if not present
            if 'timestamp' not in record:
                record['timestamp'] = datetime.now(timezone.utc)
            
            result = self.pnls_collection.insert_one(record)
            logger.info(f"Inserted PNL record with ID: {result.inserted_id}")
            return True
        except Exception as e:
            logger.error(f"Error inserting PNL record: {e}")
            return False
    
    def get_all_time_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all-time leaderboard with enhanced username matching to prevent fragmentation"""
        try:
            pipeline = [
                {
                    '$addFields': {
                        'normalized_username': {
                            '$toLower': {
                                '$cond': [
                                    {'$eq': [{'$substr': ['$username', 0, 1]}, '@']},
                                    {'$substr': ['$username', 1, -1]},  # Remove @ symbol
                                    '$username'  # Keep as is
                                ]
                            }
                        }
                    }
                },
                {
                    '$group': {
                        '_id': '$normalized_username',
                        'username': {'$first': '$username'},  # Keep original username for display
                        'total_profit_usd': {'$sum': '$profit_usd'},
                        'total_profit_sol': {'$sum': '$profit_sol'},
                        'trade_count': {'$sum': 1},
                        'winning_trades': {
                            '$sum': {
                                '$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]
                            }
                        },
                        'total_investment': {'$sum': '$initial_investment'}
                    }
                },
                {
                    '$addFields': {
                        'win_rate': {
                            '$multiply': [
                                {'$divide': ['$winning_trades', '$trade_count']},
                                100
                            ]
                        },
                        'roi': {
                            '$cond': [
                                {'$gt': ['$total_investment', 0]},
                                {
                                    '$multiply': [
                                        {'$divide': ['$total_profit_usd', '$total_investment']},
                                        100
                                    ]
                                },
                                0
                            ]
                        }
                    }
                },
                {'$sort': {'total_profit_usd': -1}},
                {'$limit': limit}
            ]
            return list(self.pnls_collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error getting all-time leaderboard: {e}")
            return []
    
    def get_monthly_leaderboard(self, year: int, month: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get monthly leaderboard for specified year and month with enhanced username matching"""
        try:
            # Create date range for the month
            start_date = datetime(year, month, 1, tzinfo=timezone.utc)
            if month == 12:
                end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)
            
            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': start_date, '$lt': end_date}
                    }
                },
                {
                    '$addFields': {
                        'normalized_username': {
                            '$toLower': {
                                '$cond': [
                                    {'$eq': [{'$substr': ['$username', 0, 1]}, '@']},
                                    {'$substr': ['$username', 1, -1]},  # Remove @ symbol
                                    '$username'  # Keep as is
                                ]
                            }
                        }
                    }
                },
                {
                    '$group': {
                        '_id': '$normalized_username',
                        'username': {'$first': '$username'},  # Keep original username for display
                        'total_profit_usd': {'$sum': '$profit_usd'},
                        'total_profit_sol': {'$sum': '$profit_sol'},
                        'trade_count': {'$sum': 1},
                        'winning_trades': {
                            '$sum': {
                                '$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]
                            }
                        },
                        'total_investment': {'$sum': '$initial_investment'}
                    }
                },
                {
                    '$addFields': {
                        'win_rate': {
                            '$multiply': [
                                {'$divide': ['$winning_trades', '$trade_count']},
                                100
                            ]
                        },
                        'roi': {
                            '$cond': [
                                {'$gt': ['$total_investment', 0]},
                                {
                                    '$multiply': [
                                        {'$divide': ['$total_profit_usd', '$total_investment']},
                                        100
                                    ]
                                },
                                0
                            ]
                        }
                    }
                },
                {'$sort': {'total_profit_usd': -1}},
                {'$limit': limit}
            ]
            return list(self.pnls_collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error getting monthly leaderboard: {e}")
            return []
    
    def get_weekly_leaderboard(self, start_date: datetime, end_date: datetime, limit: int = 10) -> List[Dict[str, Any]]:
        """Get weekly leaderboard for specified date range with enhanced username matching"""
        try:
            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': start_date, '$lt': end_date}
                    }
                },
                {
                    '$addFields': {
                        'normalized_username': {
                            '$toLower': {
                                '$cond': [
                                    {'$eq': [{'$substr': ['$username', 0, 1]}, '@']},
                                    {'$substr': ['$username', 1, -1]},  # Remove @ symbol
                                    '$username'  # Keep as is
                                ]
                            }
                        }
                    }
                },
                {
                    '$group': {
                        '_id': '$normalized_username',
                        'username': {'$first': '$username'},  # Keep original username for display
                        'total_profit_usd': {'$sum': '$profit_usd'},
                        'total_profit_sol': {'$sum': '$profit_sol'},
                        'trade_count': {'$sum': 1},
                        'winning_trades': {
                            '$sum': {
                                '$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]
                            }
                        },
                        'total_investment': {'$sum': '$initial_investment'}
                    }
                },
                {
                    '$addFields': {
                        'win_rate': {
                            '$multiply': [
                                {'$divide': ['$winning_trades', '$trade_count']},
                                100
                            ]
                        },
                        'roi': {
                            '$cond': [
                                {'$gt': ['$total_investment', 0]},
                                {
                                    '$multiply': [
                                        {'$divide': ['$total_profit_usd', '$total_investment']},
                                        100
                                    ]
                                },
                                0
                            ]
                        }
                    }
                },
                {'$sort': {'total_profit_usd': -1}},
                {'$limit': limit}
            ]
            return list(self.pnls_collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error getting weekly leaderboard: {e}")
            return []
    
    def get_daily_leaderboard(self, date: datetime, limit: int = 10) -> List[Dict[str, Any]]:
        """Get daily leaderboard for specified date with enhanced username matching"""
        try:
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': start_date, '$lte': end_date}
                    }
                },
                {
                    '$addFields': {
                        'normalized_username': {
                            '$toLower': {
                                '$cond': [
                                    {'$eq': [{'$substr': ['$username', 0, 1]}, '@']},
                                    {'$substr': ['$username', 1, -1]},  # Remove @ symbol
                                    '$username'  # Keep as is
                                ]
                            }
                        }
                    }
                },
                {
                    '$group': {
                        '_id': '$normalized_username',
                        'username': {'$first': '$username'},  # Keep original username for display
                        'total_profit_usd': {'$sum': '$profit_usd'},
                        'total_profit_sol': {'$sum': '$profit_sol'},
                        'trade_count': {'$sum': 1},
                        'winning_trades': {
                            '$sum': {
                                '$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]
                            }
                        },
                        'total_investment': {'$sum': '$initial_investment'}
                    }
                },
                {
                    '$addFields': {
                        'win_rate': {
                            '$multiply': [
                                {'$divide': ['$winning_trades', '$trade_count']},
                                100
                            ]
                        },
                        'roi': {
                            '$cond': [
                                {'$gt': ['$total_investment', 0]},
                                {
                                    '$multiply': [
                                        {'$divide': ['$total_profit_usd', '$total_investment']},
                                        100
                                    ]
                                },
                                0
                            ]
                        }
                    }
                },
                {'$sort': {'total_profit_usd': -1}},
                {'$limit': limit}
            ]
            return list(self.pnls_collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error getting daily leaderboard: {e}")
            return []
    
    def get_trade_count_leaderboard(self, start_date: datetime, end_date: datetime, limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard by trade count for specified date range with enhanced username matching"""
        try:
            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': start_date, '$lt': end_date}
                    }
                },
                {
                    '$addFields': {
                        'normalized_username': {
                            '$toLower': {
                                '$cond': [
                                    {'$eq': [{'$substr': ['$username', 0, 1]}, '@']},
                                    {'$substr': ['$username', 1, -1]},  # Remove @ symbol
                                    '$username'  # Keep as is
                                ]
                            }
                        }
                    }
                },
                {
                    '$group': {
                        '_id': '$normalized_username',
                        'username': {'$first': '$username'},  # Keep original username for display
                        'trade_count': {'$sum': 1},
                        'total_profit_usd': {'$sum': '$profit_usd'},
                        'total_profit_sol': {'$sum': '$profit_sol'},
                        'winning_trades': {
                            '$sum': {
                                '$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]
                            }
                        },
                        'total_investment': {'$sum': '$initial_investment'},
                        'avg_profit_per_trade': {'$avg': '$profit_usd'}
                    }
                },
                {
                    '$addFields': {
                        'win_rate': {
                            '$multiply': [
                                {'$divide': ['$winning_trades', '$trade_count']},
                                100
                            ]
                        },
                        'roi': {
                            '$cond': [
                                {'$gt': ['$total_investment', 0]},
                                {
                                    '$multiply': [
                                        {'$divide': ['$total_profit_usd', '$total_investment']},
                                        100
                                    ]
                                },
                                0
                            ]
                        }
                    }
                },
                {'$sort': {'trade_count': -1}},
                {'$limit': limit}
            ]
            return list(self.pnls_collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error getting trade count leaderboard: {e}")
            return []
    
    def get_profit_goat(self) -> Optional[Dict[str, Any]]:
        """Get the user with highest all-time profit"""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': '$username',  # Group by username instead of user_id
                        'username': {'$first': '$username'},
                        'total_profit_usd': {'$sum': '$profit_usd'},
                        'total_profit_sol': {'$sum': '$profit_sol'},
                        'trade_count': {'$sum': 1}
                    }
                },
                {'$sort': {'total_profit_usd': -1}},
                {'$limit': 1}
            ]
            result = list(self.pnls_collection.aggregate(pipeline))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting profit goat: {e}")
            return None
    
    def get_all_pnl_data(self) -> List[Dict[str, Any]]:
        """Get all PNL data for reporting"""
        try:
            return list(self.pnls_collection.find({}, {'_id': 0}))
        except Exception as e:
            logger.error(f"Error getting all PNL data: {e}")
            return []
    
    def get_total_profit_combined(self) -> Optional[Dict[str, Any]]:
        """Get the total combined profit across all trades"""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': None,
                        'total_profit_usd': {'$sum': '$profit_usd'},
                        'total_profit_sol': {'$sum': '$profit_sol'},
                        'total_trades': {'$sum': 1},
                        'total_investment': {'$sum': '$initial_investment'},
                        'unique_traders': {'$addToSet': '$username'},
                        'unique_tokens': {'$addToSet': '$ticker'},
                        'winning_trades': {
                            '$sum': {
                                '$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]
                            }
                        },
                        'losing_trades': {
                            '$sum': {
                                '$cond': [{'$lt': ['$profit_usd', 0]}, 1, 0]
                            }
                        }
                    }
                },
                {
                    '$addFields': {
                        'trader_count': {'$size': '$unique_traders'},
                        'token_count': {'$size': '$unique_tokens'},
                        'overall_roi': {
                            '$multiply': [
                                {'$divide': ['$total_profit_usd', '$total_investment']},
                                100
                            ]
                        },
                        'win_rate': {
                            '$multiply': [
                                {'$divide': ['$winning_trades', '$total_trades']},
                                100
                            ]
                        }
                    }
                }
            ]
            result = list(self.pnls_collection.aggregate(pipeline))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting total combined profit: {e}")
            return None

    # ===== NEW METHODS FOR ENHANCED FEATURES =====
    
    def get_user_stats(self, user_id: str, username: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive user statistics with improved user matching"""
        try:
            # Enhanced user matching - handle different username formats and ensure proper matching
            user_match_conditions = self.create_username_match_conditions(user_id, username)
            
            if not user_match_conditions:
                return None
                
            pipeline = [
                {
                    '$match': {
                        '$or': user_match_conditions
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'total_trades': {'$sum': 1},
                        'total_profit_usd': {'$sum': '$profit_usd'},
                        'total_profit_sol': {'$sum': '$profit_sol'},
                        'total_investment_usd': {'$sum': '$investment_usd'},
                        'winning_trades': {
                            '$sum': {
                                '$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]
                            }
                        },
                        'losing_trades': {
                            '$sum': {
                                '$cond': [{'$lt': ['$profit_usd', 0]}, 1, 0]
                            }
                        },
                        'best_trade': {'$max': '$profit_usd'},
                        'worst_trade': {'$min': '$profit_usd'},
                        'avg_profit': {'$avg': '$profit_usd'},
                        'unique_tokens': {'$addToSet': '$ticker'}
                    }
                }
            ]
            result = list(self.pnls_collection.aggregate(pipeline))
            if result:
                stats = result[0]
                # Calculate win rate
                stats['win_rate'] = (stats['winning_trades'] / stats['total_trades']) * 100 if stats['total_trades'] > 0 else 0
                # Calculate ROI with better validation using USD investment amounts
                if stats['total_investment_usd'] > 0:
                    stats['roi'] = (stats['total_profit_usd'] / stats['total_investment_usd']) * 100
                else:
                    stats['roi'] = 0
                stats['token_count'] = len(stats['unique_tokens'])
                
                # Debug logging to help identify issues
                logger.info(f"User stats for {username} (ID: {user_id}): {stats['total_trades']} trades, ${stats['total_profit_usd']:.2f} profit, {stats['roi']:.2f}% ROI")
                
                return stats
            return None
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return None
    
    def get_user_stats_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user stats by username only"""
        try:
            match_query = self.create_username_match_query(username=username)
            pipeline = [
                {
                    '$match': match_query
                },
                {
                    '$group': {
                        '_id': None,
                        'total_trades': {'$sum': 1},
                        'total_profit_usd': {'$sum': '$profit_usd'},
                        'total_profit_sol': {'$sum': '$profit_sol'},
                        'total_investment_usd': {'$sum': '$investment_usd'},
                        'winning_trades': {
                            '$sum': {
                                '$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]
                            }
                        },
                        'losing_trades': {
                            '$sum': {
                                '$cond': [{'$lt': ['$profit_usd', 0]}, 1, 0]
                            }
                        },
                        'best_trade': {'$max': '$profit_usd'},
                        'worst_trade': {'$min': '$profit_usd'},
                        'avg_profit': {'$avg': '$profit_usd'},
                        'unique_tokens': {'$addToSet': '$ticker'}
                    }
                }
            ]
            result = list(self.pnls_collection.aggregate(pipeline))
            if result:
                stats = result[0]
                stats['win_rate'] = (stats['winning_trades'] / stats['total_trades']) * 100 if stats['total_trades'] > 0 else 0
                stats['roi'] = (stats['total_profit_usd'] / stats['total_investment_usd']) * 100 if stats['total_investment_usd'] > 0 else 0
                stats['token_count'] = len(stats['unique_tokens'])
                return stats
            return None
        except Exception as e:
            logger.error(f"Error getting user stats by username: {e}")
            return None
    
    def get_user_history(self, user_id: str, username: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's trading history"""
        try:
            match_query = self.create_username_match_query(user_id, username)
            return list(self.pnls_collection.find(
                match_query,
                {'_id': 0}
            ).sort('timestamp', -1).limit(limit))
        except Exception as e:
            logger.error(f"Error getting user history: {e}")
            return []
    
    def get_roi_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get ROI-based leaderboard with enhanced username matching"""
        try:
            pipeline = [
                {
                    '$addFields': {
                        'normalized_username': {
                            '$toLower': {
                                '$cond': [
                                    {'$eq': [{'$substr': ['$username', 0, 1]}, '@']},
                                    {'$substr': ['$username', 1, -1]},  # Remove @ symbol
                                    '$username'  # Keep as is
                                ]
                            }
                        }
                    }
                },
                {
                    '$group': {
                        '_id': '$normalized_username',
                        'username': {'$first': '$username'},  # Keep original username for display
                        'total_profit_usd': {'$sum': '$profit_usd'},
                        'total_investment': {'$sum': '$initial_investment'},
                        'trade_count': {'$sum': 1}
                    }
                },
                {
                    '$match': {
                        'total_investment': {'$gt': 0}
                    }
                },
                {
                    '$addFields': {
                        'roi_percentage': {
                            '$multiply': [
                                {'$divide': ['$total_profit_usd', '$total_investment']},
                                100
                            ]
                        }
                    }
                },
                {'$sort': {'roi_percentage': -1}},
                {'$limit': limit}
            ]
            return list(self.pnls_collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error getting ROI leaderboard: {e}")
            return []
    
    def get_token_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most profitable tokens"""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': '$ticker',
                        'total_profit_usd': {'$sum': '$profit_usd'},
                        'total_trades': {'$sum': 1},
                        'avg_profit': {'$avg': '$profit_usd'},
                        'unique_traders': {'$addToSet': '$username'}
                    }
                },
                {
                    '$addFields': {
                        'trader_count': {'$size': '$unique_traders'}
                    }
                },
                {'$sort': {'total_profit_usd': -1}},
                {'$limit': limit}
            ]
            return list(self.pnls_collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error getting token leaderboard: {e}")
            return []
    
    def get_token_stats(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get detailed stats for a specific token"""
        try:
            pipeline = [
                {
                    '$match': {
                        'ticker': ticker.upper()
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'total_trades': {'$sum': 1},
                        'total_profit_usd': {'$sum': '$profit_usd'},
                        'avg_profit': {'$avg': '$profit_usd'},
                        'best_trade': {'$max': '$profit_usd'},
                        'worst_trade': {'$min': '$profit_usd'},
                        'total_investment': {'$sum': '$initial_investment'},
                        'successful_trades': {
                            '$sum': {
                                '$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]
                            }
                        },
                        'unique_traders': {'$addToSet': '$username'}
                    }
                },
                {
                    '$addFields': {
                        'success_rate': {
                            '$multiply': [
                                {'$divide': ['$successful_trades', '$total_trades']},
                                100
                            ]
                        },
                        'trader_count': {'$size': '$unique_traders'}
                    }
                }
            ]
            result = list(self.pnls_collection.aggregate(pipeline))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting token stats: {e}")
            return None
    
    def get_trending_tokens(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most traded tokens in recent days"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': cutoff_date}
                    }
                },
                {
                    '$group': {
                        '_id': '$ticker',
                        'trade_count': {'$sum': 1},
                        'total_profit_usd': {'$sum': '$profit_usd'},
                        'unique_traders': {'$addToSet': '$username'}
                    }
                },
                {
                    '$addFields': {
                        'trader_count': {'$size': '$unique_traders'}
                    }
                },
                {'$sort': {'trade_count': -1}},
                {'$limit': limit}
            ]
            return list(self.pnls_collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error getting trending tokens: {e}")
            return []
    
    def get_whale_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get highest investment amounts leaderboard with enhanced username matching"""
        try:
            pipeline = [
                {
                    '$addFields': {
                        'normalized_username': {
                            '$toLower': {
                                '$cond': [
                                    {'$eq': [{'$substr': ['$username', 0, 1]}, '@']},
                                    {'$substr': ['$username', 1, -1]},  # Remove @ symbol
                                    '$username'  # Keep as is
                                ]
                            }
                        }
                    }
                },
                {
                    '$group': {
                        '_id': '$normalized_username',
                        'username': {'$first': '$username'},  # Keep original username for display
                        'max_investment': {'$max': '$initial_investment'},
                        'total_investment': {'$sum': '$initial_investment'},
                        'total_profit_usd': {'$sum': '$profit_usd'},
                        'trade_count': {'$sum': 1}
                    }
                },
                {'$sort': {'max_investment': -1}},
                {'$limit': limit}
            ]
            return list(self.pnls_collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error getting whale leaderboard: {e}")
            return []
    
    def get_percent_gain_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get best percentage gains leaderboard with enhanced username matching"""
        try:
            pipeline = [
                {
                    '$addFields': {
                        'normalized_username': {
                            '$toLower': {
                                '$cond': [
                                    {'$eq': [{'$substr': ['$username', 0, 1]}, '@']},
                                    {'$substr': ['$username', 1, -1]},  # Remove @ symbol
                                    '$username'  # Keep as is
                                ]
                            }
                        },
                        'percent_gain': {
                            '$cond': [
                                {'$gt': ['$initial_investment', 0]},
                                {
                                    '$multiply': [
                                        {'$divide': ['$profit_usd', '$initial_investment']},
                                        100
                                    ]
                                },
                                0
                            ]
                        }
                    }
                },
                {
                    '$match': {
                        'initial_investment': {'$gt': 0},
                        'profit_usd': {'$gt': 0}
                    }
                },
                {
                    '$group': {
                        '_id': '$normalized_username',
                        'username': {'$first': '$username'},  # Keep original username for display
                        'best_percent_gain': {'$max': '$percent_gain'},
                        'total_profit_usd': {'$sum': '$profit_usd'},
                        'trade_count': {'$sum': 1}
                    }
                },
                {'$sort': {'best_percent_gain': -1}},
                {'$limit': limit}
            ]
            return list(self.pnls_collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error getting percent gain leaderboard: {e}")
            return []
    
    def get_investment_filtered_leaderboard(self, min_investment: float = 0, max_investment: float = float('inf'), limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard filtered by investment range"""
        try:
            match_filter = {
                'initial_investment': {'$gte': min_investment}
            }
            if max_investment != float('inf'):
                match_filter['initial_investment']['$lte'] = max_investment
            
            pipeline = [
                {'$match': match_filter},
                {
                    '$group': {
                        '_id': '$username',  # Group by username instead of user_id
                        'username': {'$first': '$username'},
                        'total_profit_usd': {'$sum': '$profit_usd'},
                        'total_profit_sol': {'$sum': '$profit_sol'},
                        'trade_count': {'$sum': 1},
                        'avg_investment': {'$avg': '$initial_investment'}
                    }
                },
                {'$sort': {'total_profit_usd': -1}},
                {'$limit': limit}
            ]
            return list(self.pnls_collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error getting investment filtered leaderboard: {e}")
            return []
    
    def get_random_successful_trade(self) -> Optional[Dict[str, Any]]:
        """Get a random successful trade for inspiration"""
        try:
            pipeline = [
                {
                    '$match': {
                        'profit_usd': {'$gt': 0}
                    }
                },
                {'$sample': {'size': 1}}
            ]
            result = list(self.pnls_collection.aggregate(pipeline))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting random successful trade: {e}")
            return None
    
    def get_daily_biggest_winner(self, date: datetime) -> Optional[Dict[str, Any]]:
        """Get biggest winner for a specific day"""
        try:
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            result = self.pnls_collection.find(
                {
                    'timestamp': {'$gte': start_date, '$lte': end_date}
                }
            ).sort('profit_usd', -1).limit(1)
            
            return list(result)[0] if result else None
        except Exception as e:
            logger.error(f"Error getting daily biggest winner: {e}")
            return None
    
    def search_trades_by_ticker(self, ticker: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search trades by ticker symbol"""
        try:
            return list(self.pnls_collection.find(
                {'ticker': ticker.upper()},
                {'_id': 0}
            ).sort('timestamp', -1).limit(limit))
        except Exception as e:
            logger.error(f"Error searching trades by ticker: {e}")
            return []
    
    def search_trades_by_username(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search trades by username"""
        try:
            match_query = self.create_username_match_query(username=username)
            return list(self.pnls_collection.find(
                match_query,
                {'_id': 0}
            ).sort('timestamp', -1).limit(limit))
        except Exception as e:
            logger.error(f"Error searching trades by username: {e}")
            return []
    
    def get_top_gainer(self, period: str) -> Optional[Dict[str, Any]]:
        """Get top gainer for specified period"""
        try:
            now = datetime.now(timezone.utc)
            
            if period == 'today':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == 'week':
                start_date = now - timedelta(days=7)
            elif period == 'month':
                start_date = now - timedelta(days=30)
            else:
                return None
            
            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': start_date},
                        'initial_investment': {'$gt': 0}
                    }
                },
                {
                    '$addFields': {
                        'percent_gain': {
                            '$multiply': [
                                {'$divide': ['$profit_usd', '$initial_investment']},
                                100
                            ]
                        }
                    }
                },
                {'$sort': {'percent_gain': -1}},
                {'$limit': 1}
            ]
            result = list(self.pnls_collection.aggregate(pipeline))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting top gainer: {e}")
            return None

    # Placeholder methods for advanced features (to be implemented based on requirements)
    def get_consistency_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most consistent traders (placeholder - needs more complex logic)"""
        # For now, return traders with best win rate and multiple trades
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': '$username',  # Group by username instead of user_id
                        'username': {'$first': '$username'},
                        'total_trades': {'$sum': 1},
                        'winning_trades': {
                            '$sum': {
                                '$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]
                            }
                        },
                        'total_profit_usd': {'$sum': '$profit_usd'}
                    }
                },
                {
                    '$match': {
                        'total_trades': {'$gte': 3}  # At least 3 trades
                    }
                },
                {
                    '$addFields': {
                        'win_rate': {
                            '$multiply': [
                                {'$divide': ['$winning_trades', '$total_trades']},
                                100
                            ]
                        }
                    }
                },
                {'$sort': {'win_rate': -1, 'total_profit_usd': -1}},
                {'$limit': limit}
            ]
            return list(self.pnls_collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error getting consistency leaderboard: {e}")
            return []
    
    def get_loss_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get transparency leaderboard (biggest losses)"""
        try:
            return list(self.pnls_collection.find(
                {'profit_usd': {'$lt': 0}},
                {'_id': 0}
            ).sort('profit_usd', 1).limit(limit))
        except Exception as e:
            logger.error(f"Error getting loss leaderboard: {e}")
            return []
    
    def get_user_achievements(self, user_id: str, username: str) -> Dict[str, Any]:
        """Get user achievements based on trading patterns"""
        try:
            stats = self.get_user_stats(user_id, username)
            if not stats:
                return {'total_achievements': 0, 'achievements': [], 'next_milestone': 'First Trade'}
            
            achievements = []
            
            # Trading volume achievements
            if stats['trade_count'] >= 1:
                achievements.append("🎯 First Trade")
            if stats['trade_count'] >= 10:
                achievements.append("🔟 Ten Trades")
            if stats['trade_count'] >= 50:
                achievements.append("📊 Active Trader")
            if stats['trade_count'] >= 100:
                achievements.append("💎 Trading Veteran")
            
            # Profit achievements
            if stats['total_profit_usd'] >= 100:
                achievements.append("💰 First $100")
            if stats['total_profit_usd'] >= 1000:
                achievements.append("🚀 Thousand Club")
            if stats['total_profit_usd'] >= 10000:
                achievements.append("🏆 Ten K Club")
            
            # Win rate achievements
            if stats['win_rate'] >= 50:
                achievements.append("⚖️ Balanced Trader")
            if stats['win_rate'] >= 70:
                achievements.append("🎯 Sharp Shooter")
            if stats['win_rate'] >= 90:
                achievements.append("👑 Almost Perfect")
            
            # ROI achievements
            if stats.get('roi', 0) >= 50:
                achievements.append("📈 Growth Hacker")
            if stats.get('roi', 0) >= 100:
                achievements.append("🔥 Double Down")
            
            return {
                'total_achievements': len(achievements),
                'achievements': achievements,
                'next_milestone': self._get_next_milestone(stats)
            }
        except Exception as e:
            logger.error(f"Error getting achievements: {e}")
            return {'total_achievements': 0, 'achievements': [], 'next_milestone': 'First Trade'}
    
    def _get_next_milestone(self, stats: dict) -> str:
        """Get next milestone for user"""
        if stats['trade_count'] < 1:
            return "First Trade"
        elif stats['trade_count'] < 10:
            return f"Reach 10 trades ({10 - stats['trade_count']} to go)"
        elif stats['total_profit_usd'] < 100:
            return f"Reach $100 profit (${100 - stats['total_profit_usd']:.2f} to go)"
        elif stats['total_profit_usd'] < 1000:
            return f"Reach $1000 profit (${1000 - stats['total_profit_usd']:.2f} to go)"
        elif stats['win_rate'] < 70:
            return f"Reach 70% win rate ({70 - stats['win_rate']:.1f}% to go)"
        else:
            return "Master Trader Status!"
    
    def get_user_streaks(self, user_id: str, username: str) -> Dict[str, Any]:
        """Get user winning/losing streaks"""
        try:
            # Get user's trades in chronological order
            match_query = self.create_username_match_query(user_id, username)
            trades = list(self.pnls_collection.find(match_query).sort('timestamp', 1))
            
            if not trades:
                return {
                    'current_streak': 0,
                    'longest_win_streak': 0,
                    'longest_loss_streak': 0,
                    'streak_type': 'neutral'
                }
            
            current_streak = 0
            longest_win_streak = 0
            longest_loss_streak = 0
            current_win_streak = 0
            current_loss_streak = 0
            
            for trade in trades:
                profit = trade.get('profit_usd', 0)
                
                if profit > 0:  # Win
                    current_win_streak += 1
                    current_loss_streak = 0
                    longest_win_streak = max(longest_win_streak, current_win_streak)
                else:  # Loss
                    current_loss_streak += 1
                    current_win_streak = 0
                    longest_loss_streak = max(longest_loss_streak, current_loss_streak)
            
            # Determine current streak
            if current_win_streak > 0:
                current_streak = current_win_streak
                streak_type = 'winning'
            elif current_loss_streak > 0:
                current_streak = current_loss_streak
                streak_type = 'losing'
            else:
                current_streak = 0
                streak_type = 'neutral'
            
            return {
                'current_streak': current_streak,
                'longest_win_streak': longest_win_streak,
                'longest_loss_streak': longest_loss_streak,
                'streak_type': streak_type
            }
        except Exception as e:
            logger.error(f"Error getting user streaks: {e}")
            return {
                'current_streak': 0,
                'longest_win_streak': 0,
                'longest_loss_streak': 0,
                'streak_type': 'neutral'
            }
    
    def get_user_milestones(self, user_id: str, username: str) -> Dict[str, Any]:
        """Get user milestones and progress"""
        try:
            stats = self.get_user_stats(user_id, username)
            if not stats:
                return {
                    'completed_milestones': [],
                    'next_milestone': 'Complete first trade',
                    'progress': 0
                }
            
            completed_milestones = []
            milestones = [
                {'name': 'First Trade', 'target': 1, 'type': 'trades', 'reward': '🎯'},
                {'name': 'Five Trades', 'target': 5, 'type': 'trades', 'reward': '🏃'},
                {'name': 'Ten Trades', 'target': 10, 'type': 'trades', 'reward': '🔟'},
                {'name': 'First Profit', 'target': 1, 'type': 'profit', 'reward': '💰'},
                {'name': '$100 Club', 'target': 100, 'type': 'profit', 'reward': '💯'},
                {'name': '$500 Club', 'target': 500, 'type': 'profit', 'reward': '🚀'},
                {'name': '$1000 Club', 'target': 1000, 'type': 'profit', 'reward': '💎'},
                {'name': '50% Win Rate', 'target': 50, 'type': 'winrate', 'reward': '⚖️'},
                {'name': '70% Win Rate', 'target': 70, 'type': 'winrate', 'reward': '🎯'},
            ]
            
            next_milestone = None
            progress = 0
            
            for milestone in milestones:
                current_value = 0
                if milestone['type'] == 'trades':
                    current_value = stats['trade_count']
                elif milestone['type'] == 'profit':
                    current_value = max(0, stats['total_profit_usd'])
                elif milestone['type'] == 'winrate':
                    current_value = stats['win_rate']
                
                if current_value >= milestone['target']:
                    completed_milestones.append(f"{milestone['reward']} {milestone['name']}")
                elif not next_milestone:
                    next_milestone = milestone['name']
                    progress = min(100, (current_value / milestone['target']) * 100)
            
            return {
                'completed_milestones': completed_milestones,
                'next_milestone': next_milestone or 'All milestones completed!',
                'progress': progress
            }
        except Exception as e:
            logger.error(f"Error getting user milestones: {e}")
            return {
                'completed_milestones': [],
                'next_milestone': 'Complete first trade',
                'progress': 0
            }
    
    def get_hall_of_fame(self) -> List[Dict[str, Any]]:
        """Get hall of fame legends - top performers across multiple categories"""
        try:
            legends = []
            
            # 1. PROFIT EMPEROR - Highest total profit
            profit_emperor = self.get_profit_goat()
            if profit_emperor:
                legends.append({
                    'category': '👑 PROFIT EMPEROR',
                    'username': profit_emperor['username'],
                    'achievement': f"${profit_emperor['total_profit_usd']:,.0f}",
                    'subtitle': f"{profit_emperor.get('trade_count', 0)} trades",
                    'description': "Ruler of the profit realm",
                    'icon': '💰',
                    'rank': 1
                })
            
            # 2. ROI DEITY - Best percentage returns
            roi_leaders = self.get_roi_leaderboard(1)
            if roi_leaders:
                roi_deity = roi_leaders[0]
                legends.append({
                    'category': '🚀 ROI DEITY',
                    'username': roi_deity['username'],
                    'achievement': f"{roi_deity.get('roi_percentage', 0):.1f}%",
                    'subtitle': f"${roi_deity.get('total_profit_usd', 0):,.0f} profit",
                    'description': "Master of percentage perfection",
                    'icon': '📈',
                    'rank': 2
                })
            
            # 3. VOLUME TITAN - Highest total investment
            volume_leaders = self.get_whale_leaderboard(1)
            if volume_leaders:
                volume_titan = volume_leaders[0]
                legends.append({
                    'category': '🐋 VOLUME TITAN',
                    'username': volume_titan['username'],
                    'achievement': f"${volume_titan.get('total_investment', 0):,.0f}",
                    'subtitle': f"{volume_titan.get('trade_count', 0)} trades",
                    'description': "Commander of capital deployment",
                    'icon': '💎',
                    'rank': 3
                })
            
            # 4. TRADE GLADIATOR - Most total trades
            try:
                trade_pipeline = [
                    {'$group': {
                        '_id': '$normalized_username',
                        'username': {'$first': '$username'},
                        'total_trades': {'$sum': 1},
                        'total_profit_usd': {'$sum': '$profit_usd'},
                        'win_rate': {
                            '$avg': {
                                '$cond': [{'$gt': ['$profit_usd', 0]}, 100, 0]
                            }
                        }
                    }},
                    {'$sort': {'total_trades': -1}},
                    {'$limit': 1}
                ]
                trade_result = list(self.pnls_collection.aggregate(trade_pipeline))
                if trade_result:
                    trade_gladiator = trade_result[0]
                    legends.append({
                        'category': '⚔️ TRADE GLADIATOR',
                        'username': trade_gladiator['username'],
                        'achievement': f"{trade_gladiator['total_trades']:,} trades",
                        'subtitle': f"${trade_gladiator.get('total_profit_usd', 0):,.0f} profit",
                        'description': "Warrior of trading volume",
                        'icon': '⚡',
                        'rank': 4
                    })
            except Exception as e:
                logger.warning(f"Could not get trade gladiator: {e}")
            
            # 5. PRECISION MASTER - Highest win rate (min 10 trades)
            try:
                precision_pipeline = [
                    {'$addFields': {
                        'normalized_username': {
                            '$toLower': {
                                '$cond': [
                                    {'$eq': [{'$substr': ['$username', 0, 1]}, '@']},
                                    {'$substr': ['$username', 1, -1]},
                                    '$username'
                                ]
                            }
                        }
                    }},
                    {'$group': {
                        '_id': '$normalized_username',
                        'username': {'$first': '$username'},
                        'total_trades': {'$sum': 1},
                        'winning_trades': {
                            '$sum': {'$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]}
                        },
                        'total_profit_usd': {'$sum': '$profit_usd'}
                    }},
                    {'$match': {'total_trades': {'$gte': 10}}},
                    {'$addFields': {
                        'win_rate': {
                            '$multiply': [
                                {'$divide': ['$winning_trades', '$total_trades']},
                                100
                            ]
                        }
                    }},
                    {'$sort': {'win_rate': -1}},
                    {'$limit': 1}
                ]
                precision_result = list(self.pnls_collection.aggregate(precision_pipeline))
                if precision_result:
                    precision_master = precision_result[0]
                    legends.append({
                        'category': '🎯 PRECISION MASTER',
                        'username': precision_master['username'],
                        'achievement': f"{precision_master['win_rate']:.1f}%",
                        'subtitle': f"{precision_master['total_trades']} trades",
                        'description': "Archer of accuracy",
                        'icon': '🏹',
                        'rank': 5
                    })
            except Exception as e:
                logger.warning(f"Could not get precision master: {e}")
            
            # 6. BATTLE EMPEROR - Most battle points
            try:
                battle_leaders = self.get_battle_leaderboard(1)
                if battle_leaders:
                    battle_emperor = battle_leaders[0]
                    total_points = battle_emperor.get('profit_battle_points', 0) + battle_emperor.get('trade_war_points', 0)
                    battles_won = battle_emperor.get('battles_won', 0)
                    legends.append({
                        'category': '🏛️ BATTLE EMPEROR',
                        'username': battle_emperor['username'],
                        'achievement': f"{total_points} pts",
                        'subtitle': f"{battles_won} victories",
                        'description': "Conqueror of the colosseum",
                        'icon': '⚔️',
                        'rank': 6
                    })
            except Exception as e:
                logger.warning(f"Could not get battle emperor: {e}")
            
            # 7. SINGLE TRADE LEGEND - Biggest single trade profit
            try:
                single_trade_pipeline = [
                    {'$sort': {'profit_usd': -1}},
                    {'$limit': 1}
                ]
                single_trade_result = list(self.pnls_collection.aggregate(single_trade_pipeline))
                if single_trade_result:
                    single_legend = single_trade_result[0]
                    legends.append({
                        'category': '💥 SINGLE TRADE LEGEND',
                        'username': single_legend['username'],
                        'achievement': f"${single_legend['profit_usd']:,.0f}",
                        'subtitle': f"{single_legend.get('ticker', 'Unknown')} trade",
                        'description': "One trade to rule them all",
                        'icon': '🌟',
                        'rank': 7
                    })
            except Exception as e:
                logger.warning(f"Could not get single trade legend: {e}")
            
            return legends
            
        except Exception as e:
            logger.error(f"Error getting hall of fame: {e}")
            return []
    
    def get_market_sentiment(self) -> Dict[str, Any]:
        """Get market sentiment analysis"""
        try:
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            
            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': week_ago}
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'total_trades': {'$sum': 1},
                        'profitable_trades': {
                            '$sum': {
                                '$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]
                            }
                        },
                        'total_profit': {'$sum': '$profit_usd'},
                        'avg_profit': {'$avg': '$profit_usd'}
                    }
                },
                {
                    '$addFields': {
                        'success_rate': {
                            '$multiply': [
                                {'$divide': ['$profitable_trades', '$total_trades']},
                                100
                            ]
                        }
                    }
                }
            ]
            result = list(self.pnls_collection.aggregate(pipeline))
            if result:
                sentiment = result[0]
                if sentiment['success_rate'] > 60:
                    sentiment['sentiment'] = 'Bullish 🐂'
                elif sentiment['success_rate'] > 40:
                    sentiment['sentiment'] = 'Neutral 🦆'
                else:
                    sentiment['sentiment'] = 'Bearish 🐻'
                return sentiment
            return {'sentiment': 'Unknown', 'total_trades': 0}
        except Exception as e:
            logger.error(f"Error getting market sentiment: {e}")
            return {'sentiment': 'Unknown', 'total_trades': 0}
    
    def get_token_popularity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get token popularity index"""
        try:
            month_ago = datetime.now(timezone.utc) - timedelta(days=30)
            
            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': month_ago}
                    }
                },
                {
                    '$group': {
                        '_id': '$ticker',
                        'trade_frequency': {'$sum': 1},
                        'unique_traders': {'$addToSet': '$username'},
                        'total_volume': {'$sum': '$initial_investment'}
                    }
                },
                {
                    '$addFields': {
                        'trader_count': {'$size': '$unique_traders'},
                        'popularity_score': {
                            '$add': [
                                '$trade_frequency',
                                {'$multiply': ['$trader_count', 2]}
                            ]
                        }
                    }
                },
                {'$sort': {'popularity_score': -1}},
                {'$limit': limit}
            ]
            return list(self.pnls_collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error getting token popularity: {e}")
            return []
    
    def get_token_profitability(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get token profitability analysis"""
        try:
            pipeline = [
                {
                    '$match': {
                        'ticker': ticker.upper()
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'total_trades': {'$sum': 1},
                        'successful_trades': {
                            '$sum': {
                                '$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]
                            }
                        },
                        'total_profit': {'$sum': '$profit_usd'},
                        'avg_profit': {'$avg': '$profit_usd'},
                        'best_trade': {'$max': '$profit_usd'},
                        'worst_trade': {'$min': '$profit_usd'}
                    }
                },
                {
                    '$addFields': {
                        'success_rate': {
                            '$multiply': [
                                {'$divide': ['$successful_trades', '$total_trades']},
                                100
                            ]
                        }
                    }
                }
            ]
            result = list(self.pnls_collection.aggregate(pipeline))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting token profitability: {e}")
            return None
    
    def get_time_trends(self) -> Dict[str, Any]:
        """Get time-based trading trends"""
        try:
            # Aggregate by day of week
            day_pipeline = [
                {
                    '$addFields': {
                        'day_of_week': {'$dayOfWeek': '$timestamp'},
                        'hour': {'$hour': '$timestamp'}
                    }
                },
                {
                    '$group': {
                        '_id': '$day_of_week',
                        'total_trades': {'$sum': 1},
                        'profitable_trades': {
                            '$sum': {'$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]}
                        },
                        'avg_profit': {'$avg': '$profit_usd'}
                    }
                },
                {
                    '$addFields': {
                        'success_rate': {
                            '$multiply': [
                                {'$divide': ['$profitable_trades', '$total_trades']},
                                100
                            ]
                        }
                    }
                },
                {'$sort': {'success_rate': -1}}
            ]
            
            day_results = list(self.pnls_collection.aggregate(day_pipeline))
            
            # Map day numbers to names
            day_names = {1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 
                        5: 'Thursday', 6: 'Friday', 7: 'Saturday'}
            
            best_day = 'Monday'
            if day_results:
                best_day = day_names.get(day_results[0]['_id'], 'Monday')
            
            # Aggregate by hour
            hour_pipeline = [
                {
                    '$addFields': {
                        'hour': {'$hour': '$timestamp'}
                    }
                },
                {
                    '$group': {
                        '_id': '$hour',
                        'total_trades': {'$sum': 1},
                        'profitable_trades': {
                            '$sum': {'$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]}
                        },
                        'avg_profit': {'$avg': '$profit_usd'}
                    }
                },
                {
                    '$addFields': {
                        'success_rate': {
                            '$multiply': [
                                {'$divide': ['$profitable_trades', '$total_trades']},
                                100
                            ]
                        }
                    }
                },
                {'$sort': {'success_rate': -1}}
            ]
            
            hour_results = list(self.pnls_collection.aggregate(hour_pipeline))
            
            best_hour = '10:00 AM'
            if hour_results:
                best_hour_num = hour_results[0]['_id']
                if best_hour_num == 0:
                    best_hour = '12:00 AM'
                elif best_hour_num < 12:
                    best_hour = f'{best_hour_num}:00 AM'
                elif best_hour_num == 12:
                    best_hour = '12:00 PM'
                else:
                    best_hour = f'{best_hour_num - 12}:00 PM'
            
            # Build day volume data
            day_volume = {}
            for result in day_results:
                day_name = day_names.get(result['_id'], 'Unknown')
                day_volume[day_name] = {
                    'trades': result['total_trades'],
                    'success_rate': result['success_rate'],
                    'avg_profit': result['avg_profit']
                }
            
            # Build hour success rate data
            hour_success = {}
            for result in hour_results:
                hour_key = f"{result['_id']}:00"
                hour_success[hour_key] = {
                    'success_rate': result['success_rate'],
                    'trades': result['total_trades']
                }
            
            return {
                'best_day': best_day,
                'best_hour': best_hour,
                'trading_volume_by_day': day_volume,
                'success_rate_by_hour': hour_success
            }
        except Exception as e:
            logger.error(f"Error getting time trends: {e}")
            return {
                'best_day': 'Monday',
                'best_hour': '10:00 AM',
                'trading_volume_by_day': {},
                'success_rate_by_hour': {}
            }
    
    def get_user_export_data(self, user_id: str, username: str) -> List[Dict[str, Any]]:
        """Get user's personal data for export"""
        try:
            match_query = self.create_username_match_query(user_id, username)
            return list(self.pnls_collection.find(
                match_query,
                {'_id': 0}
            ).sort('timestamp', -1))
        except Exception as e:
            logger.error(f"Error getting user export data: {e}")
            return []
    
    def get_user_portfolio(self, user_id: str, username: str) -> Optional[Dict[str, Any]]:
        """Get user's token diversification"""
        try:
            match_query = self.create_username_match_query(user_id, username)
            pipeline = [
                {
                    '$match': match_query
                },
                {
                    '$group': {
                        '_id': '$ticker',
                        'trade_count': {'$sum': 1},
                        'total_profit': {'$sum': '$profit_usd'},
                        'total_investment': {'$sum': '$initial_investment'}
                    }
                },
                {
                    '$sort': {'total_profit': -1}
                }
            ]
            tokens = list(self.pnls_collection.aggregate(pipeline))
            
            if not tokens:
                return None
            
            total_profit = sum(token['total_profit'] for token in tokens)
            total_investment = sum(token['total_investment'] for token in tokens)
            
            return {
                'tokens': tokens,
                'total_tokens': len(tokens),
                'total_profit': total_profit,
                'total_investment': total_investment,
                'diversification_score': min(len(tokens) * 10, 100)  # Simple score
            }
        except Exception as e:
            logger.error(f"Error getting user portfolio: {e}")
            return None
    
    def get_user_monthly_report(self, user_id: str, username: str, start_date: datetime) -> Optional[Dict[str, Any]]:
        """Get user's monthly trading report"""
        try:
            end_date = start_date + timedelta(days=32)
            end_date = end_date.replace(day=1) - timedelta(days=1)  # Last day of month
            
            user_match_query = self.create_username_match_query(user_id, username)
            pipeline = [
                {
                    '$match': {
                        '$and': [
                            user_match_query,
                            {
                                'timestamp': {
                                    '$gte': start_date,
                                    '$lte': end_date
                                }
                            }
                        ]
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'total_trades': {'$sum': 1},
                        'total_profit': {'$sum': '$profit_usd'},
                        'total_investment': {'$sum': '$initial_investment'},
                        'winning_trades': {
                            '$sum': {
                                '$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]
                            }
                        },
                        'best_trade': {'$max': '$profit_usd'},
                        'worst_trade': {'$min': '$profit_usd'},
                        'unique_tokens': {'$addToSet': '$ticker'}
                    }
                },
                {
                    '$addFields': {
                        'win_rate': {
                            '$multiply': [
                                {'$divide': ['$winning_trades', '$total_trades']},
                                100
                            ]
                        },
                        'roi': {
                            '$multiply': [
                                {'$divide': ['$total_profit', '$total_investment']},
                                100
                            ]
                        },
                        'token_count': {'$size': '$unique_tokens'}
                    }
                }
            ]
            result = list(self.pnls_collection.aggregate(pipeline))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting user monthly report: {e}")
            return None
    
    # ===== PVP BATTLE SYSTEM METHODS =====
    
    def create_battle(self, battle_data: Dict[str, Any]) -> str:
        """Create a new PVP battle"""
        try:
            # Ensure battles collection exists
            if not hasattr(self, 'battles_collection'):
                self.battles_collection = self.db['battles']
            
            # Add timestamp
            battle_data['created_at'] = datetime.now(timezone.utc)
            battle_data['status'] = 'active'
            
            result = self.battles_collection.insert_one(battle_data)
            battle_id = str(result.inserted_id)
            
            logger.info(f"Created new battle with ID: {battle_id}")
            return battle_id
        except Exception as e:
            logger.error(f"Error creating battle: {e}")
            return None
    
    def get_active_battles(self) -> List[Dict[str, Any]]:
        """Get all active battles"""
        try:
            if not hasattr(self, 'battles_collection'):
                self.battles_collection = self.db['battles']
            
            return list(self.battles_collection.find({'status': 'active'}))
        except Exception as e:
            logger.error(f"Error getting active battles: {e}")
            return []
    
    def get_battle_by_id(self, battle_id: str) -> Optional[Dict[str, Any]]:
        """Get battle by ID"""
        try:
            if not hasattr(self, 'battles_collection'):
                self.battles_collection = self.db['battles']
            
            return self.battles_collection.find_one({'_id': ObjectId(battle_id)})
        except Exception as e:
            logger.error(f"Error getting battle by ID: {e}")
            return None
    
    def update_battle_status(self, battle_id: str, status: str) -> bool:
        """Update battle status"""
        try:
            if not hasattr(self, 'battles_collection'):
                self.battles_collection = self.db['battles']
            
            result = self.battles_collection.update_one(
                {'_id': ObjectId(battle_id)},
                {'$set': {'status': status, 'updated_at': datetime.now(timezone.utc)}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating battle status: {e}")
            return False
    
    def get_battle_stats(self, battle_id: str) -> Dict[str, Any]:
        """Get current battle statistics"""
        try:
            battle = self.get_battle_by_id(battle_id)
            if not battle:
                return {}
            
            participants = battle.get('participants', [])
            battle_type = battle.get('type', 'profit')
            start_date = battle.get('start_date')
            end_date = battle.get('end_date')
            
            # Get current stats for each participant
            stats = {}
            for participant in participants:
                username = participant.replace('@', '')
                
                # Get trades within battle timeframe using enhanced username matching
                user_match_query = self.create_username_match_query(username=username)
                battle_match = {
                    '$and': [
                        user_match_query,
                        {'timestamp': {'$gte': start_date, '$lte': end_date}}
                    ]
                }
                
                pipeline = [
                    {
                        '$match': battle_match
                    },
                    {
                        '$group': {
                            '_id': None,
                            'total_trades': {'$sum': 1},
                            'total_profit_usd': {'$sum': '$profit_usd'},
                            'total_profit_sol': {'$sum': '$profit_sol'},
                            'total_investment': {'$sum': '$initial_investment'},
                            'winning_trades': {
                                '$sum': {
                                    '$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]
                                }
                            }
                        }
                    }
                ]
                
                result = list(self.pnls_collection.aggregate(pipeline))
                if result:
                    user_stats = result[0]
                    user_stats['username'] = username
                    user_stats['win_rate'] = (user_stats['winning_trades'] / user_stats['total_trades']) * 100 if user_stats['total_trades'] > 0 else 0
                    
                    if battle_type == 'profit':
                        user_stats['score'] = user_stats['total_profit_usd']
                    else:  # trade war
                        user_stats['score'] = user_stats['total_trades']
                    
                    stats[username] = user_stats
                else:
                    stats[username] = {
                        'username': username,
                        'total_trades': 0,
                        'total_profit_usd': 0,
                        'total_profit_sol': 0,
                        'total_investment': 0,
                        'winning_trades': 0,
                        'win_rate': 0,
                        'score': 0
                    }
            
            return stats
        except Exception as e:
            logger.error(f"Error getting battle stats: {e}")
            return {}
    
    def get_user_battle_points(self, username: str) -> Dict[str, Any]:
        """Get user's battle points and achievements"""
        try:
            if not hasattr(self, 'battle_points_collection'):
                self.battle_points_collection = self.db['battle_points']
            
            # Try different username formats
            clean_username = username.replace('@', '') if username.startswith('@') else username
            
            # Try to find user with various username formats
            user_points = None
            for search_username in [username, f'@{clean_username}', clean_username]:
                user_points = self.battle_points_collection.find_one({'username': search_username})
                if user_points:
                    break
            
            if not user_points:
                return {
                    'username': username,
                    'profit_battle_points': 0,
                    'trade_war_points': 0,
                    'total_battles': 0,
                    'battles_won': 0,
                    'win_rate': 0
                }
            
            return user_points
        except Exception as e:
            logger.error(f"Error getting user battle points: {e}")
            return {}
    
    def update_user_battle_points(self, username: str, battle_type: str, points: int, won: bool = False) -> bool:
        """Update user's battle points"""
        try:
            if not hasattr(self, 'battle_points_collection'):
                self.battle_points_collection = self.db['battle_points']
            
            update_data = {
                '$inc': {
                    'total_battles': 1
                },
                '$set': {
                    'updated_at': datetime.now(timezone.utc)
                }
            }
            
            if battle_type == 'profit':
                update_data['$inc']['profit_battle_points'] = points
            else:  # trade war
                update_data['$inc']['trade_war_points'] = points
            
            if won:
                update_data['$inc']['battles_won'] = 1
            
            result = self.battle_points_collection.update_one(
                {'username': username},
                update_data,
                upsert=True
            )
            
            # Calculate new win rate
            user_data = self.battle_points_collection.find_one({'username': username})
            if user_data:
                win_rate = (user_data['battles_won'] / user_data['total_battles']) * 100
                self.battle_points_collection.update_one(
                    {'username': username},
                    {'$set': {'win_rate': win_rate}}
                )
            
            return True
        except Exception as e:
            logger.error(f"Error updating user battle points: {e}")
            return False
    
    def get_battle_leaderboard(self, battle_type: str = 'all', limit: int = 10) -> List[Dict[str, Any]]:
        """Get battle points leaderboard"""
        try:
            if not hasattr(self, 'battle_points_collection'):
                self.battle_points_collection = self.db['battle_points']
            
            if battle_type == 'profit':
                sort_field = 'profit_battle_points'
            elif battle_type == 'trade':
                sort_field = 'trade_war_points'
            else:  # all - combined points
                pipeline = [
                    {
                        '$addFields': {
                            'total_points': {
                                '$add': ['$profit_battle_points', '$trade_war_points']
                            }
                        }
                    },
                    {'$sort': {'total_points': -1}},
                    {'$limit': limit}
                ]
                return list(self.battle_points_collection.aggregate(pipeline))
            
            return list(self.battle_points_collection.find({}).sort(sort_field, -1).limit(limit))
        except Exception as e:
            logger.error(f"Error getting battle leaderboard: {e}")
            return []
    
    def get_user_battle_history(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's battle history"""
        try:
            if not hasattr(self, 'battles_collection'):
                self.battles_collection = self.db['battles']
            
            # Try different username formats for battle participation
            clean_username = username.replace('@', '') if username.startswith('@') else username
            
            # Find battles where user participated (check multiple username formats)
            battles = list(self.battles_collection.find(
                {
                    'participants': {
                        '$in': [username, f'@{clean_username}', clean_username]
                    }
                },
                {'_id': 0}
            ).sort('created_at', -1).limit(limit))
            
            return battles
        except Exception as e:
            logger.error(f"Error getting user battle history: {e}")
            return []
    
    def complete_battle(self, battle_id: str) -> Dict[str, Any]:
        """Complete a battle and calculate results"""
        try:
            battle = self.get_battle_by_id(battle_id)
            if not battle:
                return {}
            
            # Get final stats
            final_stats = self.get_battle_stats(battle_id)
            
            # Determine winner and calculate points
            if not final_stats:
                return {}
            
            # Sort participants by score
            ranked_participants = sorted(
                final_stats.items(),
                key=lambda x: x[1]['score'],
                reverse=True
            )
            
            # Award points based on ranking
            results = {
                'battle_id': battle_id,
                'battle_type': battle['type'],
                'participants': len(ranked_participants),
                'rankings': []
            }
            
            for rank, (username, stats) in enumerate(ranked_participants, 1):
                # Calculate points based on rank
                if rank == 1:
                    points = 100  # Winner gets 100 points
                    won = True
                elif rank == 2:
                    points = 75   # Second place gets 75 points
                    won = False
                elif rank == 3:
                    points = 50   # Third place gets 50 points
                    won = False
                else:
                    points = 25   # Participation points
                    won = False
                
                # Update user's battle points
                self.update_user_battle_points(username, battle['type'], points, won)
                
                results['rankings'].append({
                    'rank': rank,
                    'username': username,
                    'score': stats['score'],
                    'points_earned': points,
                    'stats': stats
                })
            
            # Update battle status
            self.update_battle_status(battle_id, 'completed')
            
            return results
        except Exception as e:
            logger.error(f"Error completing battle: {e}")
            return {}
    
    def get_expired_battles(self) -> List[Dict[str, Any]]:
        """Get battles that have expired and need to be completed"""
        try:
            if not hasattr(self, 'battles_collection'):
                self.battles_collection = self.db['battles']
            
            now = datetime.now(timezone.utc)
            return list(self.battles_collection.find({
                'status': 'active',
                'end_date': {'$lt': now}
            }))
        except Exception as e:
            logger.error(f"Error getting expired battles: {e}")
            return []
    
    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global database instance
db_manager = DatabaseManager() 