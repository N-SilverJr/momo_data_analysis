from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(
    filename='backend/logs/errors.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_db_connection():
    """Create a connection to the SQLite database."""
    try:
        conn = sqlite3.connect('backend/db.sqlite')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {str(e)}")
        raise

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Fetch transactions with optional filters."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build SQL query with filters
        query = "SELECT message_id, timestamp, sender, recipient, amount, transaction_type, reference, balance, status FROM transactions WHERE 1=1"
        params = []

        # Filter by transaction type
        transaction_type = request.args.get('type')
        if transaction_type:
            query += " AND transaction_type = ?"
            params.append(transaction_type)

        # Filter by date range
        date_start = request.args.get('date_start')
        if date_start:
            query += " AND date(timestamp) >= ?"
            params.append(date_start)

        date_end = request.args.get('date_end')
        if date_end:
            query += " AND date(timestamp) <= ?"
            params.append(date_end)

        # Filter by amount range with validation
        amount_min = request.args.get('amount_min')
        if amount_min and amount_min.strip() and amount_min.isdigit():
            query += " AND amount >= ?"
            params.append(int(amount_min))

        amount_max = request.args.get('amount_max')
        if amount_max and amount_max.strip() and amount_max.isdigit():
            query += " AND amount <= ?"
            params.append(int(amount_max))

        # Execute query
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Convert rows to list of dictionaries
        transactions = [
            {
                'message_id': row['message_id'],
                'timestamp': row['timestamp'],
                'sender': row['sender'],
                'recipient': row['recipient'],
                'amount': row['amount'],
                'transaction_type': row['transaction_type'],
                'reference': row['reference'],
                'balance': row['balance'],
                'status': row['status']
            }
            for row in rows
        ]

        conn.close()
        return jsonify(transactions)
    except Exception as e:
        logging.error(f"API error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)