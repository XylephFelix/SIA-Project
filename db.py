import sqlite3
import hashlib
import os

def get_connection():
    return sqlite3.connect('app_data.db')

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, salt BLOB, password_hash TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS fake_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, address TEXT, 
                  birthdate TEXT, mobile TEXT, email TEXT, job TEXT, company TEXT, 
                  credit_card TEXT, website TEXT, username TEXT)''')
    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    if not salt:
        salt = os.urandom(32)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt, pwd_hash.hex()

def register_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    try:
        salt, pwd_hash = hash_password(password)
        c.execute("INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)",
                  (username, salt, pwd_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT salt, password_hash FROM users WHERE username = ?", (username,))
    record = c.fetchone()
    conn.close()
    
    if record:
        stored_salt, stored_hash = record
        _, input_hash = hash_password(password, stored_salt)
        return input_hash == stored_hash
    return False

def save_fake_data_to_db(records):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM fake_data")
    for data in records:
        c.execute('''INSERT INTO fake_data 
                     (name, address, birthdate, mobile, email, job, company, credit_card, website, username)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()
    conn.close()

def get_fake_data_from_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM fake_data")
    records = c.fetchall()
    conn.close()
    return records

# --- SEARCH FUNCTION (Checks ALL columns) ---
def search_fake_data(query):
    conn = get_connection()
    c = conn.cursor()
    search_term = f"%{query}%"
    c.execute('''SELECT * FROM fake_data 
                 WHERE name LIKE ? OR address LIKE ? OR birthdate LIKE ? OR mobile LIKE ? 
                 OR email LIKE ? OR job LIKE ? OR company LIKE ? OR credit_card LIKE ? 
                 OR website LIKE ? OR username LIKE ?''', 
              (search_term, search_term, search_term, search_term, search_term, 
               search_term, search_term, search_term, search_term, search_term))
    records = c.fetchall()
    conn.close()
    return records

def delete_fake_record(record_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM fake_data WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

def delete_all_fake_records():
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM fake_data")
    conn.commit()
    conn.close()