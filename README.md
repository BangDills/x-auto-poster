# X Auto Poster & Scraper 🤖📡

Proyek bot otomasi berbasis **Python** dan **Playwright** untuk mencari tweet viral di X (Twitter) berdasarkan kriteria pencarian tertentu, menyimpannya ke database lokal SQLite, dan memposting ulang (*repost*) secara aman menggunakan sesi browser (cookie) yang tersimpan tanpa biaya API resmi.

## Fitur Utama
1. **Otomasi Login Aman**: Melakukan login sekali secara interaktif dan menyimpan sesi ke `session.json`.
2. **Scrape Satu Niche (AI)**: Mengambil tweet viral tentang AI berdasarkan filter pencarian (minimal likes, bahasa) dan menyimpannya ke database SQLite.
3. **AI Rewrite (Opsional)**: Menulis ulang konten menggunakan Gemini API agar unik dan ramah algoritma X sebelum diunggah kembali.
4. **Otomatisasi Posting dengan Penyamaran**: Mengunggah postingan secara otomatis lewat browser dengan menyamar sebagai pengguna biasa (user agent asli, jeda waktu acak).
5. **Mode Uji Coba (Dry-Run)**: Meninjau tweet hasil tulisan ulang AI di browser otomasi tanpa benar-benar mengirimkannya ke publik.

---

## Persiapan Instalasi

Jalankan perintah berikut di direktori proyek ini untuk melakukan instalasi dependensi:

```bash
# 1. Buat dan aktifkan virtual environment Python
python3 -m venv venv
source venv/bin/activate

# 2. Install library yang dibutuhkan
pip install -r requirements.txt

# 3. Install browser Chromium yang digunakan oleh Playwright
playwright install chromium
```

---

## Panduan Penggunaan

### Langkah 1: Simpan Sesi Login X Anda
Jalankan skrip berikut untuk membuka browser Chromium interaktif dan login:

```bash
python login.py
```
* **Langkah**: Jendela browser akan terbuka. Masukkan akun X Anda seperti biasa dan selesaikan tantangan OTP/2FA jika ada. Setelah Anda berada di Beranda X, kembali ke terminal dan tekan **ENTER**. File `session.json` akan terbuat secara otomatis.

---

### Langkah 2: Ambil Tweet Viral (Scraping)
Jalankan skrip pencarian untuk mengambil postingan viral berdasarkan query pencarian Anda:

```bash
python scrape.py
```
Skrip akan mencari tweet tentang AI (`#AI` atau "artificial intelligence", minimal 300 likes, bahasa Inggris). Niche tunggal — hanya topik AI yang di-scrape.
Tweet hasil scraping yang unik akan disimpan di database SQLite `bot_data.db`.

---

### Langkah 3: Posting Otomatis ke X

#### Mode Uji Coba (Dry Run / Preview)
Untuk memastikan konten AI terisi dengan benar tanpa mempostingnya ke publik:
```bash
python post.py --dry-run
```
* Skrip ini akan melakukan *rewrite* pada tweet teratas di database, membuka browser X, memasukkan teks ke kolom input, mengambil screenshot preview ke berkas `post_preview.png`, lalu menutup browser kembali (tidak mengeklik tombol Post).

#### Mode Publikasi Asli
Untuk mengirim postingan secara langsung:
```bash
python post.py
```
* Skrip akan otomatis mengirim tweet ke akun Anda dan memperbarui status tweet tersebut di database menjadi `'posted'`.

---

## Konfigurasi AI Rewrite (Opsional)

Untuk menulis ulang tweet agar tidak terdeteksi plagiat, Anda dapat mengaktifkan Gemini API:
1. Dapatkan API Key gratis di [Google AI Studio](https://aistudio.google.com/).
2. Buka berkas `.env` dan masukkan API Key Anda:
   ```env
   GEMINI_API_KEY=AIzaSy...
   ```
3. Saat Anda menjalankan `post.py`, skrip akan secara otomatis memanggil Gemini untuk menulis ulang tweet tersebut.

---

## ⚠️ Tips Keamanan Akun (Sangat Penting)
Otomasi di luar API Resmi melanggar Ketentuan Layanan X. Agar akun Anda aman dari pembatasan/blokir:
1. **Batasi Frekuensi**: Jangan memposting terlalu sering. Direkomendasikan maksimal 2-4 kali sehari dengan rentang waktu beberapa jam.
2. **Gunakan Penjeda Acak**: Skrip kami sudah dilengkapi jeda acak (*random sleep*) untuk mensimulasikan perilaku pengetikan dan penelusuran manusia.
3. **Penyimpanan Sesi yang Benar**: Jangan hapus berkas `session.json` agar Anda tidak perlu login ulang terlalu sering.
4. **Metode Transfer Sesi (VPS)**: Jika Anda ingin menjalankan bot ini di server VPS Linux tanpa GUI (headless), Anda cukup melakukan login terlebih dahulu di komputer lokal Anda, lalu salin berkas `session.json` yang dihasilkan ke server VPS Anda.
