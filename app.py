import streamlit as st
import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv
import PyPDF2
from io import BytesIO

# --- 0. KONFIGURASI & FUNGSI CSS ---

def load_css(file_name):
    """Membaca file CSS eksternal dan menerapkannya."""
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"File CSS '{file_name}' tidak ditemukan.")

# Panggil fungsi untuk memuat CSS dari file eksternal
load_css("style.css")

load_dotenv()
st.set_page_config(page_title="Smart CyberSec Assistant", page_icon="🤖", layout="wide")

# --- 1. LOGIKA BACKEND (LENGKAP & TIDAK BERUBAH) ---

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("API Key Gemini tidak ditemukan. Harap tambahkan di file .env Anda.")
    st.stop()

PERSONA = "Peran Anda adalah \"Smart CyberSec Assistant\", seorang mentor keamanan siber. Jawab dengan edukatif, profesional, dan ramah. Jangan pernah sebut diri Anda AI atau model bahasa."
MODEL_NAME = 'gemini-2.5-pro'

if "messages" not in st.session_state: st.session_state.messages = []
if "quiz_state" not in st.session_state: st.session_state.quiz_state = {"is_pending": False}
if "knowledge_base" not in st.session_state: st.session_state.knowledge_base = ""

def _call_gemini_raw(prompt):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"API_ERROR: {e}"

def handle_chat(prompt, answer_source_mode, instruction=""):
    context = ""
    if st.session_state.knowledge_base:
        if answer_source_mode == "🔍 Berdasarkan Dokumen":
            context = f"Anda HANYA boleh menjawab dari KONTEKS berikut. Jika tidak ada, jawab: 'Maaf, informasi tersebut tidak ada dalam dokumen ini.'\nKONTEKS: {st.session_state.knowledge_base}\n---\n"
        else:
            context = f"Prioritaskan jawaban dari KONTEKS berikut. Jika tidak relevan, gunakan pengetahuan umum Anda.\nKONTEKS: {st.session_state.knowledge_base}\n---\n"
    full_prompt = PERSONA + context + instruction + prompt
    return _call_gemini_raw(full_prompt)

def extract_text_from_file(uploaded_file):
    text = ""
    try:
        if uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.getvalue()))
            for page in pdf_reader.pages:
                text += page.extract_text()
    except Exception as e:
        st.error(f"Gagal membaca file PDF: {e}")
    return text

def generate_quiz_question(topic, answer_source_mode):
    context_instruction = ""
    if st.session_state.knowledge_base:
        context_instruction = f"Berdasarkan konteks berikut: {st.session_state.knowledge_base}. "
    prompt = f'{context_instruction}Buat satu pertanyaan kuis tentang "{topic}". Berikan dalam format JSON dengan key "question", "options", dan "correct_answer".'
    raw_response = _call_gemini_raw(prompt)
    if "API_ERROR" in raw_response: return f"Gagal menghubungi API: {raw_response}"
    try:
        json_match = re.search(r'{{.*}}', raw_response, re.DOTALL)
        if not json_match: return f"Gagal membuat kuis (model tidak memberikan format JSON)."
        json_response = json.loads(json_match.group(0))
        options = json_response.get("options", {})
        options_str = ""
        if isinstance(options, dict): options_str = "\n\n".join([f"{k}. {v}" for k, v in options.items()])
        elif isinstance(options, list): options_str = "\n\n".join([f"{chr(65+i)}. {item}" for i, item in enumerate(options)])
        st.session_state.quiz_state = {"question": json_response["question"], "answer": json_response["correct_answer"], "is_pending": True}
        return f"**Tentu, ini pertanyaannya:**\n\n{json_response['question']}\n\n{options_str}"
    except Exception as e:
        return f"Gagal memproses format kuis. Error: {e}"

def evaluate_quiz_answer(user_answer, answer_source_mode):
    quiz = st.session_state.quiz_state
    prompt = f'Tugas Anda adalah mengevaluasi jawaban kuis. Abaikan perbedaan huruf besar/kecil. Pertanyaannya: "{quiz["question"]}". Jawaban benar: "{quiz["answer"]}". Jawaban pengguna: "{user_answer}". Evaluasi dan berikan penjelasan singkat.'
    st.session_state.quiz_state["is_pending"] = False
    return handle_chat(prompt, answer_source_mode)

# --- 2. TAMPILAN / UI STREAMLIT ---

st.title("🤖 Smart CyberSec Assistant")
st.caption("Cybersecurity Mentor & Training Chatbot")

with st.sidebar:
    st.title("🧭 Kontrol & Mode")
    answer_source_mode = st.selectbox("⚙️ Sumber Jawaban:", ("🌐 Mode Campuran", "🔍 Berdasarkan Dokumen"))
    mode = st.radio("🕹️ Mode Interaksi:", ("Chat Biasa", "Mode Edukasi", "Mode Quiz Interaktif"))
    st.info(f"Sumber: **{answer_source_mode.split(' ')[2]}** | Mode: **{mode.split(' ')[1]}**")
    st.divider()
    st.header("📂 Materi Kamu")
    uploaded_file = st.file_uploader("Unggah file PDF untuk dianalisis", type=["pdf"])
    if uploaded_file:
        with st.spinner("Mengekstrak teks..."):
            st.session_state.knowledge_base = extract_text_from_file(uploaded_file)
            st.success(f"Dokumen '{uploaded_file.name}' berhasil diproses!")
    st.divider()
    if st.button("🧹 Hapus Riwayat Chat"):
        st.session_state.messages = []
        st.session_state.quiz_state = {"is_pending": False}
        st.success("Riwayat chat telah dihapus!")
        st.rerun()

# Area Chat Utama
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

if prompt := st.chat_input("Tanya berdasarkan dokumen atau topik umum..."):
    if answer_source_mode == "🔍 Berdasarkan Dokumen" and not st.session_state.knowledge_base:
        st.warning("Tidak ada dokumen yang diunggah. Silakan unggah file PDF terlebih dahulu.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=True)

    with st.chat_message("assistant"):
        with st.spinner("Bot sedang berpikir..."):
            response = ""
            if st.session_state.quiz_state.get("is_pending"):
                response = evaluate_quiz_answer(prompt, answer_source_mode)
            else:
                if mode == "Chat Biasa":
                    response = handle_chat(prompt, answer_source_mode)
                elif mode == "Mode Edukasi":
                    instruction = "Jelaskan konsep berikut secara mendalam: "
                    response = handle_chat(prompt, answer_source_mode, instruction=instruction)
                elif mode == "Mode Quiz Interaktif":
                    if len(prompt.strip()) <= 2:
                        response = "Itu sepertinya sebuah jawaban singkat. Untuk memulai kuis baru, silakan berikan topik yang lebih deskriptif."
                    else:
                        response = generate_quiz_question(prompt, answer_source_mode)
            st.markdown(response, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": response})