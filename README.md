# MoMo SMS Data Analysis Application

## Project Overview

This fullstack application processes, stores, and visualizes MTN Mobile Money (MoMo) SMS transaction data in Rwanda. It parses approximately 1600 SMS messages from an XML file, stores the extracted transaction information in a SQLite database, and provides an interactive web dashboard to analyze the data with charts and filters.

---

## 📁 Directory Structure

```
/momo_data_analysis/
├── backend/
│   ├── parser.py          # Parses SMS data from XML
│   ├── db_setup.py        # Sets up database and inserts data
│   ├── schema.sql         # Database schema definition
│   ├── db.sqlite          # SQLite database file
│   └── logs/
│       └── errors.log     # Error logs for failed parses
├── frontend/
│   ├── index.html         # Dashboard UI
│   ├── styles.css         # CSS styling
│   ├── script.js          # JavaScript for interactivity and Chart.js
├── data/
│   └── modified_sms_v2.xml       # Input XML file containing SMS messages
├── README.md              # Project documentation
└── .gitignore             # Git ignore rules
```

---

## 🚀 Features

### ✅ Core Functionality

- **Efficient Parsing**: Extracts structured transaction data from XML.
- **Database Storage**: Saves transactions in a normalized SQLite schema.
- **Interactive Dashboard**: Displays charts and allows data filtering.
- **Error Handling**: Logs unparsed messages and alerts UI users.
- **API Integration**: Flask-based API for data retrieval and filtering.

### 📊 Supported Operations

- **Parsing**: Extracts fields like amount, type, date, sender, and transaction ID.
- **Filtering**: By transaction type, date range, and amount range.
- **Visualization**: Interactive bar, line, and pie charts with Chart.js.

---

## 📥 Input Format

The XML input file `data/modified_sms_v2.xml` contains multiple `<sms>` tags like:

```xml
<sms date="timestamp" body="You have received Rwf 2000 from M-Money on 10-05-24 16:30:58. Transaction ID: 76662021700. New balance: Rwf 2000." />
```

- Each SMS has `date` and `body` attributes.
- Transaction data is extracted using regex.
- Invalid messages are logged in `backend/logs/errors.log`.

---

## 🛠️ Backend (Python)

### `parser.py`

- **`process_xml(xml_file)`**: Parses all SMS records into transaction dictionaries.
- **`parse_sms(body, sms_date)`**: Extracts transaction fields using regex.
- **`parse_date(date_str)`**: Converts date strings into standard format.

### `db_setup.py`

- **`main(xml_file)`**: Sets up the database and populates it with transactions.
- **`setup_database()`**: Initializes SQLite with `schema.sql`.
- **`insert_transaction(conn, transaction)`**: Inserts one transaction into DB.

### `api.py` (Flask)

- Endpoint: `/api/transactions`
- Supports filtering via query parameters.
- Dependencies: `flask`, `flask-cors`, `sqlite3`.

---

## 🌐 Frontend (HTML + JS)

### `index.html` + `script.js`

- **`fetchData()`**: Calls the backend API and fetches transaction data.
- **`renderCharts(data)`**: Creates bar, pie, and line charts using Chart.js.
- **`updateCharts(data)`**: Updates charts when filters are applied.

### `styles.css`

- Styles the dashboard, filters, and layout.

---

## ⚠️ Error Handling

- **Parsing Errors**: Logged in `errors.log`.
- **Database Errors**: Handled for duplicates or schema mismatches.
- **API Errors**: Returns standard HTTP status codes.
- **Frontend Errors**: Alerts for invalid filter input or API failures.

---

## 📦 Usage Instructions

### 1. Install dependencies:

```bash
C:/Users/hp/AppData/Local/Programs/Python/Python313/python.exe -m pip install flask flask-cors
```

### 2. Process and insert SMS data:

```bash
C:/Users/hp/AppData/Local/Programs/Python/Python313/python.exe backend/db_setup.py data/sms_data.xml
```

### 3. Start the Flask API:

```bash
C:/Users/hp/AppData/Local/Programs/Python/Python313/python.exe backend/api.py
```

### 4. Launch frontend:

```bash
cd ~/OneDrive/Desktop/momo_data_analysis
C:/Users/hp/AppData/Local/Programs/Python/Python313/python.exe -m http.server 8080
```

Then open your browser at:

```
http://localhost:8080/frontend/index.html
```

---

## 🧪 Interaction Flow

1. Choose filter options (e.g., "Incoming", May 2024, 1000–5000 RWF).
2. Click **Apply Filters** to update the dashboard.
3. Click **Reset Filters** to display all data.

---

## 👤 Student Information

**Student Name:** Nshuti Shalom Silver Jr

## ✅ Future Improvements

- Parse way more data from the xml file.
- Add authentication for secure API access.
- Migrate to PostgreSQL for larger datasets.
- Export filtered results to CSV or Excel.


Link to the report (https://docs.google.com/document/d/1tD7OmcxQrV7_DMSqvjEki6QW271mmkeKFL_ti4biL3E/edit?usp=drive_link)

Link to the video (https://youtu.be/AVEpAPWDC7c)
