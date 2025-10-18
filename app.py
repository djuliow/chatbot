import streamlit as st
import google.generativeai as genai
import time
import os
from dotenv import load_dotenv

# Muat variabel lingkungan dari .env
load_dotenv()

# Konfigurasi Gemini API
st.set_page_config(page_title="CyberSec Assistant", page_icon="🛡️")

# Judul aplikasi
st.title("CyberSec Assistant")
st.write("Tanya apa saja tentang keamanan siber!")

# Ambil API Key dari .env
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

    # Inisialisasi model Gemini
    model = genai.GenerativeModel('gemini-2.5-pro')

    # Inisialisasi riwayat chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Tampilkan riwayat chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input pertanyaan dari user
    if prompt := st.chat_input("Tulis pertanyaan Anda di sini..."):
        # Tampilkan pertanyaan user
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Tampilkan jawaban chatbot
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner('Memproses jawaban...'): # Animasi loading
                try:
                    response = model.generate_content(prompt)
                    full_response = response.text
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
else:
    st.warning("API Key tidak ditemukan. Harap buat file .env dan tambahkan GEMINI_API_KEY.")
