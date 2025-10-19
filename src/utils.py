import streamlit as st
import time
import PyPDF2
from io import BytesIO
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_css(file_name):
    """Membaca file CSS eksternal dan menerapkannya."""
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"File CSS '{file_name}' tidak ditemukan.")

def type_effect(text):
    """Menampilkan teks dengan efek ketikan per karakter untuk menjaga format."""
    container = st.empty()
    displayed_text = ""
    for char in text:
        displayed_text += char
        container.markdown(displayed_text + "<span class='typing-cursor'></span>", unsafe_allow_html=True)
        time.sleep(0.01) # Waktu jeda yang sangat singkat
    # Tampilkan teks final tanpa kursor
    container.markdown(displayed_text, unsafe_allow_html=True)

def get_pdf_text(pdf_docs):
    """Mengekstrak teks dari daftar file PDF yang diunggah."""
    text = ""
    for pdf in pdf_docs:
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf.getvalue()))
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
        except Exception as e:
            st.error(f"Gagal membaca file {pdf.name}: {e}")
    return text

def get_text_chunks(text):
    """Memecah teks mentah menjadi potongan-potongan (chunks)."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    return chunks
