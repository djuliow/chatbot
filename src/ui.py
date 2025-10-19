import streamlit as st
import os
import shutil

# Import logika dari file lain
from .langchain_logic import get_vector_store, get_conversational_chain, FAISS_INDEX_PATH
from .utils import get_pdf_text, get_text_chunks

def render_sidebar():
    """Merender semua komponen di sidebar dan mengembalikan nilainya."""
    with st.sidebar:
        st.header("🧭 Kontrol & Mode")
        mode = st.radio("🕹️ Mode Interaksi:", ("Chat Biasa", "Mode Edukasi", "Mode Quiz Interaktif"))
        
        st.divider()
        
        st.header("📂 Knowledge Base")
        pdf_docs = st.file_uploader("Unggah file PDF Anda", accept_multiple_files=True, type=["pdf"])
        
        if st.button("Proses Dokumen") and pdf_docs:
            with st.spinner("Memproses dokumen Anda..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                if get_vector_store(text_chunks):
                    st.session_state.doc_info["count"] = len(pdf_docs)
                    # Inisialisasi ulang chain dengan knowledge base baru
                    st.session_state.conversation = get_conversational_chain()
                    st.success("Dokumen berhasil diproses!")
                    st.rerun()

        st.metric("Dokumen Dimuat", st.session_state.doc_info.get("count", 0))
        st.metric("Potongan Teks (Chunks)", st.session_state.doc_info.get("chunks", 0))
        
        if st.button("Hapus Knowledge Base"):
            if os.path.exists(FAISS_INDEX_PATH):
                shutil.rmtree(FAISS_INDEX_PATH)
            st.session_state.conversation = None
            st.session_state.doc_info = {"count": 0, "chunks": 0}
            st.success("Knowledge base telah dihapus.")
            st.rerun()
            
        st.divider()
        
        if st.button("🧹 Hapus Riwayat Chat"):
            st.session_state.chat_history = []
            st.success("Riwayat chat telah dihapus!")
            st.rerun()
            
    return mode

def render_chat_history():
    """Merender riwayat percakapan dari session state."""
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

def display_contextual_images(prompt):
    """Menampilkan gambar berdasarkan kata kunci dalam prompt."""
    if "phishing" in prompt.lower():
        st.image("https://cdn-icons-png.flaticon.com/512/6488/6488757.png", width=80)
    elif "cryptography" in prompt.lower() or "enkripsi" in prompt.lower():
        st.image("https://cdn-icons-png.flaticon.com/512/2920/2920277.png", width=80)
    elif "malware" in prompt.lower():
        st.image("https://cdn-icons-png.flaticon.com/512/5959/5959172.png", width=80)
