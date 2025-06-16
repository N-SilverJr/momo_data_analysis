import sqlite3
import logging
from parser import parse_sms_data

# Configure logging for database operations
logging.basicConfig(
    filename='backend/logs/errors.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def init_database(schema_file, db_file):
    """
    Initialize the SQLite database using the schema.sql file.
    """
    try:
        with open(schema_file, 'r') as f:
            schema = f.read()
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.executescript(schema)
        conn.commit()
        logging.info("Database initialized successfully")
        return conn
    except Exception as e:
        logging.error(f"Failed to initialize database: {str(e)}")
        raise

def insert_transactions(conn, transactions):
    """
    Insert parsed transactions into the database, handling duplicates.
    """
    cursor = conn.cursor()
    insert_query = """
    INSERT OR IGNORE INTO transactions (
        message_id, timestamp, sender, recipient, amount, 
        transaction_type, reference, balance, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    for transaction in transactions:
        try:
            cursor.execute(insert_query, (
                transaction['message_id'],
                transaction['timestamp'],
                transaction['sender'],
                transaction.get('recipient'),
                transaction.get('amount'),
                transaction['transaction_type'],
                transaction.get('reference'),
                transaction.get('balance'),
                transaction['status']
            ))
        except sqlite3.IntegrityError as e:
            logging.warning(f"Duplicate message_id {transaction['message_id']}: {str(e)}")
            continue
        except Exception as e:
            logging.warning(f"Error inserting transaction {transaction['message_id']}: {str(e)}")
            continue
    
    conn.commit()
    logging.info(f"Inserted {cursor.rowcount} transactions into the database")

def main():
    """
    Main function to set up database and insert transactions.
    """
    schema_file = 'backend/schema.sql'
    db_file = 'backend/db.sqlite'
    xml_file = 'C:/Users/hp/OneDrive/Desktop/momo_data_analysis/data/modified_sms_v2.xml'
    
    try:
        # Initialize database
        conn = init_database(schema_file, db_file)
        
        # Parse transactions
        transactions = parse_sms_data(xml_file)
        if not transactions:
            logging.error("No transactions parsed from XML")
            return
        
        # Insert transactions
        insert_transactions(conn, transactions)
        
        # Verify insertion
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transactions")
        count = cursor.fetchone()[0]
        print(f"Total transactions in database: {count}")
        
    except Exception as e:
        logging.error(f"Database setup failed: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()