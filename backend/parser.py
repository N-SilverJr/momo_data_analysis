import xml.etree.ElementTree as ET
import re
import logging
from datetime import datetime
import os

# Configure logging to save unprocessed messages
logging.basicConfig(
    filename='backend/logs/errors.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def parse_sms_data(xml_file):
    """
    Parse SMS data from XML file, clean, and categorize it.
    Returns a list of dictionaries with cleaned data.
    """
    if not os.path.exists(xml_file):
        logging.error(f"XML file not found: {xml_file}")
        print(f"Error: XML file not found: {xml_file}")
        return []

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        print(f"Root tag: {root.tag}, Number of SMS elements: {len(root.findall('sms'))}")
        transactions = []

        for sms in root.findall('sms'):
            try:
                message_id = sms.get('id', sms.get('date'))
                sender = sms.get('address', '').strip()
                timestamp_ms = sms.get('date', '')
                body = sms.get('body', '').strip()
                print(f"SMS {message_id}: address={sender}, date={timestamp_ms}, body={body[:50]}...")

                if not (message_id and sender and timestamp_ms and body):
                    logging.warning(f"Skipping SMS {message_id}: Missing critical fields")
                    continue

                try:
                    timestamp = datetime.fromtimestamp(int(timestamp_ms) / 1000.0)
                except ValueError:
                    logging.warning(f"Skipping SMS {message_id}: Invalid timestamp: {timestamp_ms}")
                    continue

                transaction = process_message_body(body, message_id)
                if transaction:
                    transaction['message_id'] = message_id
                    transaction['timestamp'] = timestamp
                    transaction['sender'] = sender
                    transactions.append(transaction)
                else:
                    logging.warning(f"Skipping SMS {message_id}: Could not categorize message: {body}")

            except Exception as e:
                logging.warning(f"Error processing SMS {message_id}: {str(e)}")
                continue

        return transactions

    except Exception as e:
        logging.error(f"Failed to parse XML file: {str(e)}")
        print(f"Error parsing XML: {str(e)}")
        return []

def process_message_body(body, message_id):
    """
    Clean and categorize the SMS message body.
    Returns a dictionary with transaction details or None if unprocessable.
    """
    print(f"Processing body: {body[:100]}...")
    transaction_types = {
        'incoming': r'(?:You have received|received)\s+\d+(?:,\d+)?\s*RWF.*from',
        'payment': r'(?:Your payment|paid)\s+\d+(?:,\d+)?\s*RWF.*to',
        'transfer': r'\d+(?:,\d+)?\s*RWF\s+transferred\s+to',
        'bank_deposit': r'bank deposit.*\d+(?:,\d+)?\s*RWF',
        'airtime': r'payment.*to\s+Airtime',
        'bill_payment': r'payment.*(cash power|bill)',
        'withdrawal': r'withdrawn.*from.*agent',
        'bank_transfer': r'transfer.*to.*bank',
        'bundle_purchase': r'(internet|voice).*bundle.*purchase',
        'third_party': r'transaction of\s+\d+(?:,\d+)?\s*RWF\s+by.*completed'
    }

    transaction = {
        'transaction_type': None,
        'amount': None,
        'recipient': None,
        'reference': None,
        'balance': None,
        'status': 'success'
    }

    for t_type, pattern in transaction_types.items():
        if re.search(pattern, body, re.IGNORECASE):
            print(f"Matched type: {t_type}")
            transaction['transaction_type'] = t_type
            break

    if not transaction['transaction_type']:
        print(f"No transaction type matched for SMS {message_id}")
        return None

    amount_match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)\s*RWF', body, re.IGNORECASE)
    if amount_match:
        try:
            amount_str = amount_match.group(1).replace(',', '')
            transaction['amount'] = int(amount_str)
        except ValueError:
            logging.warning(f"Invalid amount in SMS {message_id}: {amount_match.group(1)}")
            return None

    recipient_match = re.search(r'(?:to|from)\s+(\+?\d{10,12}|\w+\s+\w+)', body, re.IGNORECASE)
    if recipient_match:
        transaction['recipient'] = recipient_match.group(1)

    reference_match = re.search(r'(?:TxId|Financial Transaction Id):\s*(\w+)', body, re.IGNORECASE)
    if reference_match:
        transaction['reference'] = reference_match.group(1)

    balance_match = re.search(r'(?:Your new balance|NEW BALANCE|New balance):\s*(\d{1,3}(?:,\d{3})*|\d+)\s*RWF', body, re.IGNORECASE)
    if balance_match:
        try:
            balance_str = balance_match.group(1).replace(',', '')
            transaction['balance'] = int(balance_str)
        except ValueError:
            logging.warning(f"Invalid balance in SMS {message_id}: {balance_match.group(1)}")

    if 'failed' in body.lower():
        transaction['status'] = 'failed'

    return transaction

def main():
    """
    Main function to parse SMS data and save cleaned data.
    """
    xml_file = 'C:/Users/hp/OneDrive/Desktop/momo_data_analysis/data/modified_sms_v2.xml'
    print(f"Attempting to open file: {xml_file}")
    transactions = parse_sms_data(xml_file)
    print(f"Parsed {len(transactions)} transactions")
    for t in transactions:
        print(t)
    return transactions

if __name__ == "__main__":
    main()