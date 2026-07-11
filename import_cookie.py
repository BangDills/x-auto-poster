import json
import os
import sys

SESSION_PATH = os.path.join(os.path.dirname(__file__), "session.json")

def create_session_from_token(auth_token):
    auth_token = auth_token.strip()
    if not auth_token:
        print("Error: auth_token tidak boleh kosong.")
        return False
        
    # Format session state yang kompatibel dengan Playwright
    session_data = {
        "cookies": [
            {
                "name": "auth_token",
                "value": auth_token,
                "domain": ".x.com",
                "path": "/",
                "expires": -1,
                "httpOnly": True,
                "secure": True,
                "sameSite": "Lax"
            }
        ],
        "origins": []
    }
    
    try:
        with open(SESSION_PATH, "w") as f:
            json.dump(session_data, f, indent=2)
        print(f"\n[SUKSES]: Berkas sesi berhasil dibuat di {SESSION_PATH}")
        print("Sekarang bot akan otomatis masuk sebagai akun Anda tanpa perlu melewati halaman login X.")
        return True
    except Exception as e:
        print(f"Error menyimpan berkas: {e}")
        return False

if __name__ == "__main__":
    print("==================================================================")
    print("X AUTH_TOKEN COOKIE IMPORTER")
    print("==================================================================")
    print("Membantu Anda login tanpa diblokir oleh sistem deteksi bot X.")
    print("==================================================================")
    
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        print("Langkah mendapatkan auth_token:")
        print("1. Buka x.com di browser biasa Anda (Chrome/Firefox/Edge) dan pastikan sudah login.")
        print("2. Klik kanan di halaman -> pilih Inspect (Periksa) -> masuk ke tab 'Application' (Chrome) atau 'Storage' (Firefox).")
        print("3. Di menu sebelah kiri, cari 'Cookies' -> klik 'https://x.com'.")
        print("4. Cari baris bernama 'auth_token' dan salin nilai (Value) berupa string panjang.")
        print("==================================================================\n")
        token = input("Masukkan nilai auth_token Anda: ").strip()
        
    create_session_from_token(token)
