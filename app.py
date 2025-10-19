import streamlit as st
from dotenv import load_dotenv

# Impor fungsi dari file-file yang telah dipisah
from src.utils import load_css, type_effect
from src.ui import render_sidebar, render_chat_history, display_contextual_images
from src.langchain_logic import get_conversational_chain, generate_quiz_question, evaluate_quiz_answer

# --- 0. SETUP APLIKASI --- 

# Muat environment variables dan CSS
load_dotenv()
load_css("style.css")

st.set_page_config(page_title="Smart CyberSec Assistant", page_icon="🛡️", layout="wide")

# --- 1. INISIALISASI SESSION STATE --- 

if "conversation" not in st.session_state: st.session_state.conversation = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "doc_info" not in st.session_state: st.session_state.doc_info = {"count": 0, "chunks": 0}
if "quiz_state" not in st.session_state: st.session_state.quiz_state = {"is_pending": False}

# --- 2. TAMPILAN UTAMA & ORKESTRASI --- 

st.title("🤖 Smart CyberSec Assistant")

# Render semua komponen UI dari file ui.py
mode = render_sidebar()
render_chat_history()

# Logika input chat utama
if prompt := st.chat_input("Ajukan pertanyaan atau mulai kuis..."):
    # Pastikan chain sudah siap jika ada dokumen
    if st.session_state.doc_info["count"] > 0 and st.session_state.conversation is None:
        st.session_state.conversation = get_conversational_chain()

    # Jika chain belum siap (belum ada dokumen), beri peringatan
    if not st.session_state.conversation:
        st.warning("Silakan unggah dan proses dokumen terlebih dahulu untuk memulai percakapan.")
        st.stop()

    # Tambahkan & tampilkan pesan user
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        display_contextual_images(prompt)
        st.markdown(prompt, unsafe_allow_html=True)

    # Proses & tampilkan respons bot
    with st.chat_message("assistant"):
        with st.spinner("🧠 Smart CyberSec Assistant sedang berpikir..."):
            response_text = ""
            # Tentukan aksi berdasarkan status kuis atau mode interaksi
            if st.session_state.quiz_state.get("is_pending"):
                response_text = evaluate_quiz_answer(prompt)
            else:
                question_to_ask = prompt
                if mode == "Mode Edukasi":
                    question_to_ask = f"Jelaskan konsep keamanan siber ini secara mendalam: {prompt}"
                elif mode == "Mode Quiz Interaktif":
                    response_text = generate_quiz_question(prompt)
                
                # Jika bukan mode kuis, jalankan chain utama untuk menjawab
                if mode != "Mode Quiz Interaktif":
                    response = st.session_state.conversation({"question": question_to_ask})
                    response_text = response["answer"]

            type_effect(response_text)
    
    # Tambahkan respons bot ke riwayat setelah ditampilkan
    st.session_state.chat_history.append({"role": "assistant", "content": response_text})