# CyberSec Assistant 🛡️

CyberSec Assistant adalah chatbot edukasi yang ditenagai oleh model bahasa dari Groq dan teknologi RAG (Retrieval-Augmented Generation) untuk memberikan jawaban yang relevan dan kontekstual seputar keamanan siber.

## ✨ Fitur

- **Antarmuka Chat Interaktif**: Dibangun dengan Streamlit untuk kemudahan penggunaan.
- **Respons Cepat**: Memanfaatkan Groq API untuk inferensi model bahasa yang sangat cepat.
- **Pencarian Kontekstual**: Menggunakan FAISS untuk membuat indeks vektor dari dokumen lokal, memungkinkan chatbot menjawab pertanyaan berdasarkan informasi yang relevan.
- **Arsitektur Modular**: Kode diorganisir dengan rapi, memisahkan antara UI (`ui.py`), logika backend (`langchain_logic.py`), dan utilitas (`utils.py`).
- **Manajemen API Key**: Konfigurasi kunci API yang aman menggunakan file `.env`.

## 🛠️ Tumpukan Teknologi

- **Frontend**: Streamlit
- **Backend/Logika**: LangChain, Groq API
- **Vector Store**: FAISS (CPU)
- **Model Embedding**: Hugging Face Instructor Embeddings

## 🚀 Instalasi & Persiapan

Untuk menjalankan proyek ini secara lokal, ikuti langkah-langkah berikut:

1.  **Clone repositori ini:**
    ```bash
    git clone https://github.com/username/repo-name.git
    cd repo-name
    ```

2.  **Buat dan konfigurasi file `.env`:**
    Buat file bernama `.env` di direktori utama proyek dan tambahkan API key Anda untuk Groq.
    ```
    GROQ_API_KEY="API_KEY_ANDA"
    ```

3.  **Instal dependensi:**
    Pastikan Anda memiliki Python 3.8+ terinstal. Kemudian, instal semua library yang dibutuhkan.
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
Dibuat dengan menggunakan Python, Streamlit, LangChain, dan Groq.