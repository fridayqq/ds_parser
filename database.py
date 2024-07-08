import sqlite3

def create_table():
    conn = sqlite3.connect('news_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            link TEXT PRIMARY KEY,
            title TEXT,
            images TEXT,
            parsed BOOLEAN DEFAULT 0,
            rich_text TEXT DEFAULT '',
            posted BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def fetch_unparsed_links():
    conn = sqlite3.connect('news_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT link, title FROM news WHERE parsed = 0')
    rows = cursor.fetchall()
    conn.close()
    return rows

def link_exists(link):
    conn = sqlite3.connect('news_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT link FROM news WHERE link = ?', (link,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def insert_news(link, title, images):
    conn = sqlite3.connect('news_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO news (link, title, images)
        VALUES (?, ?, ?)
    ''', (link, title, images))
    conn.commit()
    conn.close()

def update_parsed(link, rich_text=''):
    conn = sqlite3.connect('news_data.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE news SET rich_text = ?, parsed = 1 WHERE link = ?', (rich_text, link))
    conn.commit()
    conn.close()


def mark_as_parsed_and_posted(link):
    conn = sqlite3.connect('news_data.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE news SET parsed = 1, posted = 1 WHERE link = ?', (link,))
    conn.commit()
    conn.close()