import sqlite3
import json
import os
from datetime import datetime

DB_FILE = "insightpilot.db"

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if tables do not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Executive Reports
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS executive_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        report_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        content TEXT NOT NULL,
        metrics_summary TEXT
    );
    """)
    
    # 2. Strategy Engine Queries
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS strategy_queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query_text TEXT NOT NULL,
        response_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 3. Data Uploads Audit Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data_uploads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        row_count INTEGER NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_type TEXT NOT NULL
    );
    """)
    
    conn.commit()
    conn.close()

def save_executive_report(title, report_type, content, metrics_summary=None):
    """Saves a generated executive report to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    metrics_str = json.dumps(metrics_summary) if metrics_summary else None
    cursor.execute(
        "INSERT INTO executive_reports (title, report_type, content, metrics_summary) VALUES (?, ?, ?, ?)",
        (title, report_type, content, metrics_str)
    )
    conn.commit()
    conn.close()

def get_all_reports():
    """Fetches all saved executive reports."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, report_type, created_at, content FROM executive_reports ORDER BY created_at DESC")
    reports = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return reports

def log_strategy_query(query_text, response_text):
    """Logs user query and its AI-generated response."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO strategy_queries (query_text, response_text) VALUES (?, ?)",
        (query_text, response_text)
    )
    conn.commit()
    conn.close()

def log_data_upload(filename, row_count, data_type):
    """Logs details of uploaded data files."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO data_uploads (filename, row_count, data_type) VALUES (?, ?, ?)",
        (filename, row_count, data_type)
    )
    conn.commit()
    conn.close()

# Initialize on import
init_db()
