import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bot_data.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Buat tabel dasar jika belum ada
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tweets (
            id TEXT PRIMARY KEY,
            author TEXT NOT NULL,
            text TEXT NOT NULL,
            likes INTEGER DEFAULT 0,
            retweets INTEGER DEFAULT 0,
            media_urls TEXT, -- JSON string array
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            rewritten_text TEXT,
            status TEXT DEFAULT 'scraped', -- 'scraped', 'approved', 'posted', 'ignored'
            posted_at TIMESTAMP,
            posted_url TEXT
        )
    """)
    
    # Tambahkan kolom baru jika belum ada untuk skema baru
    new_columns = [
        ("category", "TEXT DEFAULT 'general'"),
        ("language", "TEXT DEFAULT 'en'"),
        ("local_media_path", "TEXT")
    ]
    
    for col_name, col_def in new_columns:
        try:
            cursor.execute(f"ALTER TABLE tweets ADD COLUMN {col_name} {col_def}")
        except sqlite3.OperationalError:
            # Kolom sudah ada, lompati
            pass
            
    conn.commit()
    conn.close()

def save_tweets(tweets_list, category='general', language='en'):
    """
    Saves a list of tweets dict to database.
    Each tweet dict should have: id, author, text, likes, retweets, media_urls (list), local_media_path (str)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    saved_count = 0
    for t in tweets_list:
        media_urls_json = json.dumps(t.get('media_urls', []))
        try:
            cursor.execute("""
                INSERT INTO tweets (id, author, text, likes, retweets, media_urls, category, language, local_media_path, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'scraped')
                ON CONFLICT(id) DO UPDATE SET
                    likes=excluded.likes,
                    retweets=excluded.retweets,
                    local_media_path=COALESCE(excluded.local_media_path, tweets.local_media_path)
            """, (
                t['id'], 
                t['author'], 
                t['text'], 
                t.get('likes', 0), 
                t.get('retweets', 0), 
                media_urls_json,
                category,
                language,
                t.get('local_media_path')
            ))
            saved_count += 1
        except Exception as e:
            print(f"Error saving tweet {t.get('id')}: {e}")
            
    conn.commit()
    conn.close()
    return saved_count

def get_pending_tweets(limit=10, category=None, language=None):
    """
    Gets tweets that are scraped but not yet posted or ignored.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM tweets WHERE status = 'scraped'"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    if language:
        query += " AND language = ?"
        params.append(language)
        
    query += " ORDER BY likes DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    
    tweets = []
    for r in rows:
        t = dict(r)
        t['media_urls'] = json.loads(t['media_urls']) if t['media_urls'] else []
        tweets.append(t)
    return tweets

def update_tweet_status(tweet_id, status, rewritten_text=None, posted_url=None):
    """
    Updates the status and optional fields of a tweet.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if status == 'posted':
        cursor.execute("""
            UPDATE tweets 
            SET status = ?, rewritten_text = ?, posted_url = ?, posted_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, rewritten_text, posted_url, tweet_id))
    else:
        cursor.execute("""
            UPDATE tweets 
            SET status = ?, rewritten_text = COALESCE(?, rewritten_text)
            WHERE id = ?
        """, (status, rewritten_text, tweet_id))
        
    conn.commit()
    conn.close()

def reset_pending_queue():
    """
    Deletes all tweets that have 'scraped' status (in the queue but not posted/commented/quoted)
    and removes their associated local media files from disk to prevent storage leaks.
    """
    import os
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT local_media_path FROM tweets WHERE status = 'scraped' AND local_media_path IS NOT NULL")
    rows = cursor.fetchall()
    
    for row in rows:
        media_path = row['local_media_path']
        if media_path and os.path.exists(media_path):
            try:
                os.remove(media_path)
                print(f"Hapus berkas media usang: {os.path.basename(media_path)}")
            except Exception as e:
                print(f"Gagal menghapus berkas media usang {media_path}: {e}")
                
    cursor.execute("DELETE FROM tweets WHERE status = 'scraped'")
    deleted_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"Mengosongkan antrean: Berhasil menghapus {deleted_count} tweet usang dari database.")
    return deleted_count

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
