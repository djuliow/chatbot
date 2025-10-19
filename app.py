import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- 1. KONFIGURASI AWAL --- 

# Muat variabel lingkungan (API Key) dari file .env
load_dotenv()

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Smart CyberSec Assistant",
    page_icon="🤖",
    layout="centered"
)

# Konfigurasi API Google Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("API Key Gemini tidak ditemukan. Harap tambahkan di file .env Anda.")
    st.stop()

# --- 2. FUNGSI UTAMA & LOGIKA --- 

def get_gemini_response(prompt, mode):
    """Mengirim prompt ke Gemini dan mengembalikan responsnya."""
    
    # Tentukan instruksi sistem berdasarkan mode yang dipilih
    system_instruction = ""
    if mode == "Mode Edukasi":
        system_instruction = "Anda adalah seorang guru keamanan siber. Jelaskan konsep berikut secara mendalam, detail, dan mudah dipahami dengan analogi jika memungkinkan: "
    elif mode == "Mode Quiz":
        system_instruction = "Anda adalah seorang pembuat kuis. Buat satu pertanyaan latihan (kuis) pilihan ganda beserta jawabannya (tandai jawaban yang benar) tentang topik keamanan siber berikut: "
    else: # Chat Biasa
        system_instruction = "Anda adalah asisten keamanan siber yang membantu menjawab pertanyaan pengguna. "

    # Gabungkan instruksi sistem dengan prompt pengguna
    full_prompt = system_instruction + prompt

    try:
        # Inisialisasi model Gemini
        model = genai.GenerativeModel('gemini-2.5-pro')
        # Dapatkan respons
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        # Penanganan error jika API call gagal
        st.error(f"Terjadi kesalahan saat menghubungi Gemini: {e}")
        return None

# --- 3. TAMPILAN / UI STREAMLIT --- 

# Judul utama aplikasi
st.title("🤖 Smart CyberSec Assistant")

# Sidebar untuk memilih mode
st.sidebar.title("Mode Interaksi")
mode = st.sidebar.radio(
    "Pilih mode chatbot:",
    ("Chat Biasa", "Mode Edukasi", "Mode Quiz")
)
st.sidebar.info(f"Anda sedang dalam **{mode}**.")

# Inisialisasi riwayat percakapan dalam session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan pesan dari riwayat percakapan
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Terima input dari pengguna
if prompt := st.chat_input("Tanyakan sesuatu tentang cybersecurity..."):
    # 1. Tambahkan dan tampilkan pesan pengguna
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Dapatkan dan tampilkan respons dari bot
    with st.chat_message("assistant"):
        # Tampilkan animasi loading saat menunggu respons
        with st.spinner("CyberSec Assistant sedang berpikir..."):
            response = get_gemini_response(prompt, mode)
            if response:
                st.markdown(response)
                # Tambahkan respons bot ke riwayat
                st.session_state.messages.append({"role": "assistant", "content": response})