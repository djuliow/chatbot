# CyberSec Assistant 🛡️

CyberSec Assistant adalah chatbot edukasi sederhana yang ditenagai oleh Gemini 2.5 Pro. Chatbot ini dirancang untuk menjawab pertanyaan seputar keamanan siber.

## ✨ Fitur

- Antarmuka chat interaktif menggunakan Streamlit.
- Terhubung dengan model bahasa `gemini-2.5-pro` dari Google.
- Manajemen API key yang aman menggunakan file `.env`.
- Animasi loading saat jawaban sedang diproses.

## 🚀 Instalasi & Persiapan

Untuk menjalankan proyek ini secara lokal, ikuti langkah-langkah berikut:

1. **Clone repositori ini:**
   ```bash
   git clone https://github.com/username/repo-name.git
   cd repo-name
   ```

2. **Buat dan konfigurasi file `.env`:**
   Buat file bernama `.env` di direktori utama proyek dan tambahkan API key Anda.
   ```
   GEMINI_API_KEY="API_KEY_ANDA"
   ```

3. **Instal dependensi:**
   Pastikan Anda memiliki Python 3.8+ terinstal. Kemudian, instal semua library yang dibutuhkan menggunakan `requirements.txt`.
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Penggunaan

Setelah instalasi selesai, jalankan aplikasi Streamlit dengan perintah berikut:

```bash
streamlit run app.py
```

Aplikasi akan terbuka secara otomatis di browser Anda.

---
Dibuat dengan ❤️ menggunakan Python, Streamlit, dan Gemini.
