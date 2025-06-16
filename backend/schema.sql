CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT UNIQUE NOT NULL,       
    timestamp DATETIME NOT NULL,            
    sender TEXT NOT NULL,                  
    recipient TEXT,                        
    amount INTEGER,                        
    transaction_type TEXT NOT NULL,        
    reference TEXT,                        
    balance INTEGER,                      
    status TEXT,                           
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP  
);

CREATE INDEX IF NOT EXISTS idx_transaction_type ON transactions (transaction_type);
CREATE INDEX IF NOT EXISTS idx_timestamp ON transactions (timestamp);