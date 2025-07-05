"""
Data import script for loading historical PNL data from Excel into MongoDB
"""

import pandas as pd
import logging
from datetime import datetime, timezone
from database import db_manager
from utils import currency_converter
from typing import Dict, Any, List
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataImporter:
    def __init__(self, excel_file: str = "lorestats.xlsx"):
        self.excel_file = excel_file
        self.processed_count = 0
        self.error_count = 0
    
    def _parse_date_column(self, date_series: pd.Series) -> pd.Series:
        """Parse date column with support for multiple formats including ISO and UK format"""
        parsed_dates = pd.Series(index=date_series.index, dtype='datetime64[ns, UTC]')
        
        for idx, date_value in date_series.items():
            try:
                if pd.isna(date_value):
                    parsed_dates[idx] = datetime.now(timezone.utc)
                    continue
                    
                # Convert to string if not already
                date_str = str(date_value).strip()
                
                # Try parsing ISO format first (e.g., "2025-04-08T00:00:00.000Z")
                if 'T' in date_str and ('Z' in date_str or '+' in date_str):
                    parsed_date = pd.to_datetime(date_str, utc=True)
                    parsed_dates[idx] = parsed_date
                    continue
                
                # Try UK format (dd/mm/yyyy)
                if '/' in date_str:
                    try:
                        parsed_date = pd.to_datetime(date_str, format='%d/%m/%Y', utc=True)
                        parsed_dates[idx] = parsed_date
                        continue
                    except ValueError:
                        pass
                
                # Try standard formats
                parsed_date = pd.to_datetime(date_str, utc=True)
                parsed_dates[idx] = parsed_date
                
            except Exception as e:
                logger.warning(f"Could not parse date '{date_value}': {e}")
                parsed_dates[idx] = datetime.now(timezone.utc)
        
        return parsed_dates
    
    def format_date_uk(self, date_value: datetime) -> str:
        """Format datetime to UK format (dd/mm/yyyy)"""
        if date_value is None:
            return ""
        return date_value.strftime("%d/%m/%Y")
    
    def validate_excel_file(self) -> bool:
        """Check if Excel file exists and is readable"""
        if not os.path.exists(self.excel_file):
            logger.error(f"Excel file not found: {self.excel_file}")
            return False
        
        try:
            # Try to read the file
            df = pd.read_excel(self.excel_file, nrows=1)
            logger.info(f"Excel file validated: {self.excel_file}")
            return True
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}")
            return False
    
    def load_excel_data(self) -> pd.DataFrame:
        """Load data from Excel file"""
        try:
            df = pd.read_excel(self.excel_file)
            logger.info(f"Loaded {len(df)} rows from {self.excel_file}")
            return df
        except Exception as e:
            logger.error(f"Error loading Excel data: {e}")
            return pd.DataFrame()
    
    def clean_and_validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate the Excel data"""
        logger.info("Cleaning and validating data...")
        
        # Make a copy to avoid modifying original
        cleaned_df = df.copy()
        
        # Common column name variations to standardize
        column_mapping = {
            'user': 'username',
            'User': 'username',
            'USERNAME': 'username',
            'Username': 'username',
            'trader': 'username',
            'Trader': 'username',
            'profit': 'profit_usd',
            'Profit': 'profit_usd',
            'PROFIT': 'profit_usd',
            'profit_usd': 'profit_usd',
            'Profit_USD': 'profit_usd',
            'ticker': 'ticker',
            'Ticker': 'ticker',
            'TICKER': 'ticker',
            'symbol': 'ticker',
            'Symbol': 'ticker',
            'Token Name': 'ticker',
            'token_name': 'ticker',
            'investment': 'initial_investment',
            'Investment': 'initial_investment',
            'Invested': 'initial_investment',
            'invested': 'initial_investment',
            'initial': 'initial_investment',
            'Initial': 'initial_investment',
            'date': 'date',
            'Date': 'date',
            'DATE': 'date',
            'timestamp': 'timestamp',
            'Timestamp': 'timestamp'
        }
        
        # Rename columns based on mapping
        for old_name, new_name in column_mapping.items():
            if old_name in cleaned_df.columns:
                cleaned_df = cleaned_df.rename(columns={old_name: new_name})
        
        # Ensure required columns exist
        required_columns = ['username', 'profit_usd']
        missing_columns = [col for col in required_columns if col not in cleaned_df.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            logger.info(f"Available columns: {list(cleaned_df.columns)}")
            return pd.DataFrame()
        
        # Clean username column
        if 'username' in cleaned_df.columns:
            cleaned_df['username'] = cleaned_df['username'].astype(str).str.strip()
            cleaned_df = cleaned_df[cleaned_df['username'].notna()]
            cleaned_df = cleaned_df[cleaned_df['username'] != '']
        
        # Clean profit column
        if 'profit_usd' in cleaned_df.columns:
            # Handle various profit formats
            cleaned_df['profit_usd'] = pd.to_numeric(cleaned_df['profit_usd'], errors='coerce')
            cleaned_df = cleaned_df[cleaned_df['profit_usd'].notna()]
        
        # Clean ticker column if exists
        if 'ticker' in cleaned_df.columns:
            cleaned_df['ticker'] = cleaned_df['ticker'].astype(str).str.strip().str.upper()
        else:
            cleaned_df['ticker'] = 'N/A'
        
        # Clean initial investment if exists
        if 'initial_investment' in cleaned_df.columns:
            cleaned_df['initial_investment'] = pd.to_numeric(cleaned_df['initial_investment'], errors='coerce')
            cleaned_df['initial_investment'] = cleaned_df['initial_investment'].fillna(0)
        else:
            cleaned_df['initial_investment'] = 0
        
        # Handle date column - support multiple date formats including ISO and UK format
        if 'date' in cleaned_df.columns:
            cleaned_df['date'] = self._parse_date_column(cleaned_df['date'])
        elif 'timestamp' in cleaned_df.columns:
            cleaned_df['date'] = self._parse_date_column(cleaned_df['timestamp'])
        else:
            cleaned_df['date'] = datetime.now(timezone.utc)
        
        # Remove rows with invalid data
        initial_count = len(cleaned_df)
        cleaned_df = cleaned_df.dropna(subset=['username', 'profit_usd'])
        final_count = len(cleaned_df)
        
        if initial_count != final_count:
            logger.info(f"Removed {initial_count - final_count} rows with invalid data")
        
        logger.info(f"Data cleaning complete. {len(cleaned_df)} valid rows remaining.")
        return cleaned_df
    
    def convert_to_mongodb_records(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert DataFrame to MongoDB records with currency conversion"""
        logger.info("Converting data to MongoDB records...")
        
        records = []
        sol_rate = currency_converter.get_sol_usd_rate()
        
        for _, row in df.iterrows():
            try:
                # Convert date to datetime if it's not already
                if 'date' in row and pd.notna(row['date']):
                    timestamp = row['date']
                elif 'timestamp' in row and pd.notna(row['timestamp']):
                    timestamp = row['timestamp']
                else:
                    timestamp = datetime.now(timezone.utc)
                
                # Convert to datetime if it's a string
                if isinstance(timestamp, str):
                    timestamp = pd.to_datetime(timestamp, utc=True)
                elif isinstance(timestamp, pd.Timestamp):
                    timestamp = timestamp.to_pydatetime()
                
                # Ensure timezone aware
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                
                # Create MongoDB record
                record = {
                    'user_id': f"historical_{hash(row['username'])}",  # Generate consistent ID for historical users
                    'username': row['username'],
                    'ticker': row['ticker'],
                    'initial_investment': float(row['initial_investment']),
                    'profit_usd': float(row['profit_usd']),
                    'profit_sol': float(row['profit_usd']) / sol_rate if sol_rate else 0,
                    'currency': 'USD',  # Historical data is assumed to be in USD
                    'timestamp': timestamp,
                    'screenshot': None,  # Historical data doesn't have screenshots
                    'is_historical': True  # Flag to identify historical records
                }
                
                records.append(record)
                
            except Exception as e:
                logger.error(f"Error processing row: {e}")
                self.error_count += 1
                continue
        
        logger.info(f"Converted {len(records)} records for MongoDB insertion")
        return records
    
    def import_to_database(self, records: List[Dict[str, Any]]) -> bool:
        """Import records to MongoDB database"""
        if not records:
            logger.warning("No records to import")
            return False
        
        try:
            # Connect to database
            if not db_manager.connect():
                logger.error("Failed to connect to database")
                return False
            
            # Check if historical data already exists
            existing_count = db_manager.pnls_collection.count_documents({'is_historical': True})
            if existing_count > 0:
                logger.info(f"Found {existing_count} existing historical records")
                response = input("Historical data already exists. Do you want to replace it? (y/N): ")
                if response.lower() != 'y':
                    logger.info("Import cancelled by user")
                    return False
                
                # Delete existing historical data
                delete_result = db_manager.pnls_collection.delete_many({'is_historical': True})
                logger.info(f"Deleted {delete_result.deleted_count} existing historical records")
            
            # Insert new records
            result = db_manager.pnls_collection.insert_many(records)
            self.processed_count = len(result.inserted_ids)
            
            logger.info(f"Successfully imported {self.processed_count} historical records")
            return True
            
        except Exception as e:
            logger.error(f"Error importing to database: {e}")
            return False
    
    def run_import(self) -> bool:
        """Run the complete import process"""
        logger.info(f"Starting data import from {self.excel_file}")
        
        # Validate Excel file
        if not self.validate_excel_file():
            return False
        
        # Load data
        df = self.load_excel_data()
        if df.empty:
            logger.error("No data loaded from Excel file")
            return False
        
        # Clean and validate
        cleaned_df = self.clean_and_validate_data(df)
        if cleaned_df.empty:
            logger.error("No valid data after cleaning")
            return False
        
        # Convert to MongoDB records
        records = self.convert_to_mongodb_records(cleaned_df)
        if not records:
            logger.error("No records generated for import")
            return False
        
        # Import to database
        success = self.import_to_database(records)
        
        # Print summary
        logger.info("="*50)
        logger.info("IMPORT SUMMARY")
        logger.info("="*50)
        logger.info(f"Excel file: {self.excel_file}")
        logger.info(f"Records processed: {self.processed_count}")
        logger.info(f"Errors encountered: {self.error_count}")
        logger.info(f"Import successful: {'Yes' if success else 'No'}")
        logger.info("="*50)
        
        return success


def main():
    """Main function to run data import"""
    import sys
    
    # Get Excel file path from command line or use default
    excel_file = sys.argv[1] if len(sys.argv) > 1 else "lorestats.xlsx"
    
    print(f"📊 Starting data import from: {excel_file}")
    print("🔄 Processing data with UK date format support (dd/mm/yyyy)")
    
    # Create and run importer
    importer = DataImporter(excel_file)
    success = importer.run_import()
    
    if success:
        print("✅ Data import completed successfully!")
        print("📅 Dates have been processed with UK format support")
        print("🚀 You can now start the Telegram bot to begin using the imported data.")
    else:
        print("❌ Data import failed. Please check the logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main() 