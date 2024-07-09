import sqlite3

def create_db():
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            group_id INTEGER PRIMARY KEY,
            admin_id INTEGER,
            ban_links BOOLEAN DEFAULT 0,
            ban_forwards BOOLEAN DEFAULT 0,
            ban_bad_words BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def add_group(group_id, admin_id):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO groups (group_id, admin_id, ban_links, ban_forwards, ban_bad_words)
        VALUES (?, ?, 0, 0, 0)
    ''', (group_id, admin_id))
    conn.commit()
    conn.close()

def update_group_setting(group_id, setting, value):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute(f'UPDATE groups SET {setting} = ? WHERE group_id = ?', (value, group_id))
    conn.commit()
    conn.close()

def get_group_settings(group_id):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM groups WHERE group_id = ?', (group_id,))
    settings = c.fetchone()
    conn.close()
    return settings


create_db()
