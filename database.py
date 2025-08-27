import sqlite3
import json
from datetime import datetime, timedelta
from contextlib import contextmanager

class Database:
    def __init__(self, db_path='analyses.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        with self.get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    upload_date TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                    total_packets INTEGER,
                    packet_data TEXT,
                    statistics TEXT
                )
            ''')
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def save_analysis(self, filename, packets, stats):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analyses (filename, total_packets, packet_data, statistics)
                VALUES (?, ?, ?, ?)
            ''', (filename, len(packets), json.dumps(packets), json.dumps(stats)))
            conn.commit()
            return cursor.lastrowid
    
    def get_analysis(self, analysis_id):
        with self.get_connection() as conn:
            row = conn.execute(
                'SELECT * FROM analyses WHERE id = ?', 
                (analysis_id,)
            ).fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'filename': row['filename'],
                    'upload_date': row['upload_date'],
                    'packets': json.loads(row['packet_data']),
                    'stats': json.loads(row['statistics'])
                }
            return None
    
    def get_all_analyses(self):
        with self.get_connection() as conn:
            rows = conn.execute(
                'SELECT id, filename, upload_date, total_packets FROM analyses ORDER BY id DESC'
            ).fetchall()
            return [dict(row) for row in rows]
    
    def delete_analysis(self, analysis_id):
        with self.get_connection() as conn:
            conn.execute('DELETE FROM analyses WHERE id = ?', (analysis_id,))
            conn.commit()