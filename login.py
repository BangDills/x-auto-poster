import sys
import os
from playwright.sync_api import sync_playwright

SESSION_PATH = os.path.join(os.path.dirname(__file__), "session.json")

def save_x_session():
    print("==================================================================")
    print("MEMULAI PROSES LOGIN X (TWITTER)")
    print("==================================================================")
    print("Menjalankan browser Chromium...")
    
    with sync_playwright() as p:
        # Menjalankan Chromium dalam mode GUI (headless=False)
        # Gunakan argumen user-agent standar agar tidak dicurigai sebagai bot otomatis
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )
        
        # Buat konteks baru tanpa deteksi automation kontrol
        context = browser.new_context(
            viewport=None,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Matikan webdriver flag agar tidak terdeteksi
        context.add_init_script("delete navigator.__proto__.webdriver")
        
        page = context.new_page()
        
        print("Membuka halaman login X...")
        page.goto("https://x.com/i/flow/login")
        
        print("\n[PETUNJUK PENTING]:")
        print("1. Silakan login ke akun X Anda secara manual pada jendela browser yang terbuka.")
        print("2. Selesaikan semua verifikasi keamanan (2FA/OTP/Captcha) jika ada.")
        print("3. Setelah Anda masuk ke halaman Beranda (Home Feed) X Anda:")
        print("   Kembali ke terminal ini dan tekan [ENTER] untuk menyimpan sesi.")
        print("==================================================================")
        
        # Menunggu input dari pengguna di terminal
        input("\nTekan [ENTER] di sini setelah Anda selesai login...")
        
        # Menyimpan session state (cookies & localStorage)
        print("\nMenyimpan sesi ke session.json...")
        context.storage_state(path=SESSION_PATH)
        
        print(f"Sesi berhasil disimpan di: {SESSION_PATH}")
        print("Menutup browser...")
        browser.close()
        
    print("\nProses selesai. Sesi login Anda siap digunakan untuk auto-posting!")

if __name__ == "__main__":
    save_x_session()
