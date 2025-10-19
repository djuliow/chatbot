import streamlit as st
from dotenv import load_dotenv
import re

# Impor fungsi dari file-file yang telah dipisah
from src.utils import load_css, type_effect
from src.ui import render_sidebar, render_chat_history, display_contextual_images
from src.langchain_logic import get_conversational_chain, generate_quiz_question, evaluate_quiz_answer

# --- 0. SETUP APLIKASI --- 

load_dotenv()
load_css("style.css")
st.set_page_config(page_title="Smart CyberSec Assistant", page_icon="🛡️", layout="wide")

# --- 1. INISIALISASI SESSION STATE --- 

if "conversation" not in st.session_state: st.session_state.conversation = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "doc_info" not in st.session_state: st.session_state.doc_info = {"count": 0, "chunks": 0}
if "quiz_state" not in st.session_state: 
    st.session_state.quiz_state = {"is_pending": False, "awaiting_topic": False}
if "score" not in st.session_state: st.session_state.score = 0

# --- 2. TAMPILAN UTAMA & ORKESTRASI --- 

st.title("🤖 Smart CyberSec Assistant")

# Render UI dan dapatkan pilihan mode dari user
mode = render_sidebar()
render_chat_history()

# Logika input chat utama
if prompt := st.chat_input("Ajukan pertanyaan atau mulai kuis..."):
    # Inisialisasi chain jika belum ada & dokumen sudah diproses
    if st.session_state.doc_info.get("count", 0) > 0 and st.session_state.conversation is None:
        st.session_state.conversation = get_conversational_chain()

    # Tambahkan pesan user ke riwayat untuk ditampilkan
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        display_contextual_images(prompt)
        st.markdown(prompt, unsafe_allow_html=True)

    # Proses & tampilkan respons bot
    with st.chat_message("assistant"):
        with st.spinner("🧠 Smart CyberSec Assistant sedang berpikir..."):
            response_text = ""
            
            # 1. Prioritas utama: jika ada kuis yang menunggu jawaban
            if st.session_state.quiz_state.get("is_pending"):
                response_text = evaluate_quiz_answer(prompt)
                if response_text.strip().startswith("[BENAR]"):
                    st.session_state.score = st.session_state.get("score", 0) + 10
                    st.balloons()
                    response_text = response_text.replace("[BENAR]", "").strip()
                elif response_text.strip().startswith("[SALAH]"):
                    response_text = response_text.replace("[SALAH]", "").strip()
            
            # 2. Jika bot sedang menunggu topik kuis dari user
            elif st.session_state.quiz_state.get("awaiting_topic"):
                st.session_state.quiz_state["awaiting_topic"] = False # Reset flag
                response_text = generate_quiz_question(prompt) # Anggap prompt ini adalah topiknya

            # 3. Jika tidak ada status khusus, proses sebagai prompt baru
            else:
                is_quiz_request = any(keyword in prompt.lower() for keyword in ["kuis", "quiz", "tes"])
                
                if mode == "Mode Quiz Interaktif" and is_quiz_request:
                    topic = re.sub(r'(kuis|quiz|tes|tentang|berikan|saya|dong|dari|materi|yang|ada|di|dalam|upload|saja)', '', prompt, flags=re.IGNORECASE).strip(" ,.")
                    if topic:
                        response_text = generate_quiz_question(topic)
                    elif st.session_state.doc_info["count"] > 0:
                        response_text = generate_quiz_question("keseluruhan isi dokumen")
                    else:
                        response_text = "Tentu! Mohon sebutkan topik spesifik untuk kuisnya."
                        st.session_state.quiz_state["awaiting_topic"] = True
                
                else:  # Default ke "Chat Biasa"
                    if not st.session_state.conversation:
                        st.warning("Silakan unggah dan proses dokumen terlebih dahulu.")
                        st.stop()
                    response = st.session_state.conversation({"question": prompt})
                    response_text = response["answer"]

            type_effect(response_text)
    
    # Tambahkan respons final bot ke riwayat
    st.session_state.chat_history.append({"role": "assistant", "content": response_text})
