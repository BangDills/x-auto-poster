import os
import sys
import time
import random
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from database import get_pending_tweets, update_tweet_status

# Load variabel lingkungan dari file .env
load_dotenv()

SESSION_PATH = os.path.join(os.path.dirname(__file__), "session.json")

def rewrite_tweet_with_gemini(original_text, language='en'):
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("GEMINI_API_KEY tidak ditemukan di .env. Menggunakan teks asli.")
        return original_text
        
    print("Menulis ulang tweet menggunakan Gemini API...")
    try:
        from google import genai
        # Inisialisasi Google GenAI client
        client = genai.Client(api_key=gemini_api_key)
        
        # Bedakan prompt berdasarkan bahasa tweet asli
        if language == 'id':
            prompt = (
                "Tulis ulang tweet berikut agar unik, menarik, dan siap diposting ulang di X (Twitter). "
                "Pertahankan pesan inti atau esensi humor/meme/politiknya, tetapi gunakan kata-kata berbeda. "
                "Boleh menggunakan gaya santai (slang internet Indonesia jika relevan). "
                "Jangan tambahkan tanda kutip di awal dan akhir output. Tampilkan HANYA teks hasil penulisan ulang saja:\n\n"
                f"{original_text}"
            )
        else:
            prompt = (
                "Rewrite the following tweet to make it unique, engaging, and ready for posting on X. "
                "Keep the core message but use different wording. Do not add hashtags unless they are highly relevant. "
                "Do not add quotes around the output. Output ONLY the rewritten tweet text:\n\n"
                f"{original_text}"
            )
        
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        
        rewritten = response.text.strip()
        if rewritten.startswith('"') and rewritten.endswith('"'):
            rewritten = rewritten[1:-1].strip()
        elif rewritten.startswith("'") and rewritten.endswith("'"):
            rewritten = rewritten[1:-1].strip()
            
        print(f"Hasil Rewrite:\n---\n{rewritten}\n---")
        return rewritten
    except Exception as e:
        print(f"Gagal melakukan rewrite dengan Gemini: {e}. Menggunakan teks asli.")
        return original_text

def post_to_x(tweet_id, text, local_media_path=None, dry_run=False):
    if not os.path.exists(SESSION_PATH):
        print(f"Error: Berkas sesi '{SESSION_PATH}' tidak ditemukan. Jalankan login terlebih dahulu.")
        return False
        
    print(f"\nMenyiapkan postingan untuk tweet ID: {tweet_id}")
    print(f"Konten yang akan diposting:\n---\n{text}\n---")
    if local_media_path:
        print(f"Jalur media lokal yang akan diunggah: {local_media_path}")
        
    success = False
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        context = browser.new_context(
            storage_state=SESSION_PATH,
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        context.add_init_script("delete navigator.__proto__.webdriver")
        
        page = context.new_page()
        
        print("Membuka halaman compose post X...")
        page.goto("https://x.com/compose/post")
        
        time.sleep(random.uniform(3, 5))
        
        try:
            print("Mencari kolom input tweet...")
            page.wait_for_selector('div[role="textbox"]', timeout=15000)
            
            # 1. Unggah media terlebih dahulu jika ada
            if local_media_path and os.path.exists(local_media_path):
                print("Mengunggah berkas media...")
                # X menggunakan input file tersembunyi dengan data-testid="fileInput"
                page.set_input_files('input[data-testid="fileInput"]', local_media_path)
                # Jika media adalah video (.mp4), tunggu lebih lama agar proses upload/processing selesai
                if local_media_path.lower().endswith('.mp4'):
                    print("Mendeteksi file video. Menunggu proses unggah & pemrosesan video (25 detik)...")
                    time.sleep(25)
                else:
                    time.sleep(random.uniform(4, 6))
            
            # 2. Klik dan isi teks postingan
            page.click('div[role="textbox"]')
            time.sleep(random.uniform(0.5, 1.2))
            
            print("Mengisi teks postingan...")
            page.fill('div[role="textbox"]', text)
            time.sleep(random.uniform(1.5, 3.0))
            
            if dry_run:
                print("\n[DRY RUN]: Postingan terisi tetapi TIDAK dikirim ke publik.")
                # Ambil screenshot preview postingan
                page.screenshot(path="post_preview.png")
                print("Screenshot preview disimpan di post_preview.png")
                success = True
            else:
                # Cari tombol Post
                post_btn_selector = 'button[data-testid="tweetButton"], button[data-testid="tweetButtonInline"]'
                page.wait_for_selector(post_btn_selector, timeout=5000)
                
                print("Mengeklik tombol 'Post'...")
                page.click(post_btn_selector)
                
                # Tunggu proses posting selesai
                print("Menunggu konfirmasi postingan terkirim...")
                time.sleep(5)
                
                success = True
                print("Postingan berhasil dikirim!")
                
        except Exception as e:
            print(f"Error saat melakukan posting: {e}")
            page.screenshot(path="post_error.png")
            print("Screenshot error disimpan di post_error.png")
            
        browser.close()
        
    return success

def run_auto_post(dry_run=False, category=None, language=None):
    # Ambil tweet pending teratas dari database
    pending_tweets = get_pending_tweets(limit=1, category=category, language=language)
    if not pending_tweets:
        print("Tidak ada tweet pending di database.")
        return
        
    target_tweet = pending_tweets[0]
    print(f"Menemukan tweet viral dari @{target_tweet['author']} ({target_tweet['likes']} likes) di kategori {target_tweet['category']} ({target_tweet['language']}).")
    
    # Lakukan rewrite berdasarkan bahasa tweet asli
    rewritten_text = rewrite_tweet_with_gemini(target_tweet['text'], language=target_tweet['language'])
    
    # Batasi panjang teks sesuai batas X (280 karakter)
    if len(rewritten_text) > 280:
        print(f"Peringatan: Teks rewrite ({len(rewritten_text)} karakter) melebihi batas 280 karakter.")
        print("Memotong teks agar muat...")
        rewritten_text = rewritten_text[:277] + "..."
        
    local_media = target_tweet.get('local_media_path')
    
    # Kirim ke X
    posted = post_to_x(
        tweet_id=target_tweet['id'],
        text=rewritten_text,
        local_media_path=local_media,
        dry_run=dry_run
    )
    
    if posted and not dry_run:
        # Update status di database menjadi 'posted'
        update_tweet_status(
            tweet_id=target_tweet['id'],
            status='posted',
            rewritten_text=rewritten_text,
            posted_url="https://x.com/home"
        )
        print("Status tweet diperbarui di database.")
        
        # Hapus file media lokal setelah sukses diposting agar hemat ruang disk
        if local_media and os.path.exists(local_media):
            try:
                os.remove(local_media)
                print(f"Berkas media lokal berhasil dibersihkan: {local_media}")
            except Exception as e:
                print(f"Gagal membersihkan media lokal: {e}")
                
    elif posted and dry_run:
        print("Mode dry-run: Status di database tetap 'scraped' dan file media lokal dipertahankan.")

if __name__ == "__main__":
    dry_run_arg = "--dry-run" in sys.argv or "-d" in sys.argv
    
    # Izinkan pemfilteran opsional lewat argumen:
    # python post.py --category meme --lang id
    category_filter = None
    lang_filter = None
    
    for idx, arg in enumerate(sys.argv):
        if arg == "--category" and idx + 1 < len(sys.argv):
            category_filter = sys.argv[idx + 1]
        if arg == "--lang" and idx + 1 < len(sys.argv):
            lang_filter = sys.argv[idx + 1]
            
    run_auto_post(dry_run=dry_run_arg, category=category_filter, language=lang_filter)
