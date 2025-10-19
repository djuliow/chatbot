import streamlit as st
import os
import json
import re
from dotenv import load_dotenv

# Import komponen LangChain yang baru
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# --- Muat API Key di awal --- 
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# --- Konstanta & Persona ---
PERSONA = "Peran Anda adalah \"Smart CyberSec Assistant\", seorang mentor keamanan siber. Jawab dengan edukatif, profesional, dan ramah. Jangan pernah sebut diri Anda AI atau model bahasa."
MODEL_NAME = 'llama-3.3-70b-versatile'
FAISS_INDEX_PATH = "faiss_index"

# --- Fungsi Inti LangChain & Groq (Versi Baru) ---

def get_vector_store(text_chunks):
    """Membuat vector store menggunakan embedding lokal (HuggingFace)."""
    try:
        embeddings = HuggingFaceEmbeddings(model_name="hkunlp/instructor-large")
        vector_store = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
        vector_store.save_local(FAISS_INDEX_PATH)
        st.session_state.doc_info["chunks"] = len(text_chunks)
        return True
    except Exception as e:
        st.error(f"Gagal membuat vector store: {e}")
        return False

def get_conversational_chain():
    """Membuat conversational chain menggunakan Groq LLM dan embedding lokal."""
    template = f"""{PERSONA}
Gunakan riwayat chat dan konteks berikut untuk menjawab pertanyaan. Jika tidak tahu, katakan tidak tahu.
Konteks:
{{context}}
Riwayat Chat:
{{chat_history}}
Pertanyaan Pengguna: {{question}}
Jawaban Asisten:"""
    prompt = PromptTemplate(template=template, input_variables=["context", "chat_history", "question"])
    
    # Menggunakan ChatGroq sebagai LLM
    llm = ChatGroq(temperature=0.3, groq_api_key=groq_api_key, model_name=MODEL_NAME)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    try:
        # Menggunakan model embedding lokal untuk memuat indeks
        embeddings = HuggingFaceEmbeddings(model_name="hkunlp/instructor-large")
        vector_store = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        return ConversationalRetrievalChain.from_llm(llm=llm, retriever=vector_store.as_retriever(), memory=memory, combine_docs_chain_kwargs={"prompt": prompt})
    except Exception as e:
        st.error(f"Gagal memuat knowledge base: {e}. Pastikan ada file yang diproses.")
        return None

# Fungsi untuk kuis tidak lagi diperlukan karena fungsionalitasnya digantikan oleh chain utama
# Namun, kita bisa membuat fungsi raw call ke Groq jika diperlukan untuk tugas spesifik
def _call_groq_raw(prompt):
    try:
        chat = ChatGroq(temperature=0, groq_api_key=groq_api_key, model_name=MODEL_NAME)
        return chat.invoke(prompt).content
    except Exception as e:
        return f"API_ERROR: {e}"

# Fungsi generate_quiz dan evaluate_quiz di-refactor untuk menggunakan _call_groq_raw atau chain utama
def generate_quiz_question(topic):
    """Membuat kuis dengan mengambil konteks relevan dari vector store secara manual."""
    context_instruction = ""
    # Jika ada dokumen, lakukan pencarian manual untuk mendapatkan konteks
    if st.session_state.doc_info.get("count", 0) > 0:
        try:
            embeddings = HuggingFaceEmbeddings(model_name="hkunlp/instructor-large")
            vector_store = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            retriever = vector_store.as_retriever(search_kwargs={"k": 3}) # Ambil 3 potongan paling relevan
            retrieved_docs = retriever.get_relevant_documents(topic)
            
            if retrieved_docs:
                context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
                context_instruction = f"Berdasarkan konteks berikut:\n---\n{context_text}\n---\n"
        except Exception as e:
            return f"Gagal mengambil konteks dari dokumen: {e}"

    prompt = f'''{context_instruction}
Buat satu pertanyaan kuis pilihan ganda tentang "{topic}".

PENTING:
1. Pertanyaan harus memiliki SATU jawaban yang paling tepat dan tidak ambigu.
2. Tiga pilihan lainnya harus menjadi pengecoh (distractor) yang jelas salah.
3. Berikan dalam format JSON dengan key "question", "options" (sebuah dictionary dengan key "A", "B", "C", "D"), dan "correct_answer".
4. Nilai dari "correct_answer" HARUS berupa salah satu dari huruf "A", "B", "C", atau "D".

Contoh format JSON:
{{
  "question": "Apa warna langit?",
  "options": {{
    "A": "Biru",
    "B": "Hijau",
    "C": "Merah",
    "D": "Kuning"
  }},
  "correct_answer": "A"
}}
'''
    raw_response = _call_groq_raw(prompt)
    if "API_ERROR" in raw_response: return f"Gagal menghubungi API: {raw_response}"
    try:
        # Perbaikan: Gunakan find dan rfind untuk ekstraksi JSON yang lebih kuat
        start_index = raw_response.find('{')
        end_index = raw_response.rfind('}') + 1
        
        if start_index == -1 or end_index == 0:
            return f"Gagal membuat kuis (model tidak memberikan format JSON)."

        json_str = raw_response[start_index:end_index]
        json_response = json.loads(json_str)
        options = json_response.get("options", {})
        options_str = ""
        if isinstance(options, dict): options_str = "\n\n".join([f"{k}. {v}" for k, v in options.items()])
        elif isinstance(options, list): options_str = "\n\n".join([f"{chr(65+i)}. {item}" for i, item in enumerate(options)])
        st.session_state.quiz_state = {"question": json_response["question"], "answer": json_response["correct_answer"], "is_pending": True}
        return f"**Tentu, ini pertanyaannya:**\n\n{json_response['question']}\n\n{options_str}"
    except Exception as e:
        return f"Gagal memproses format kuis. Error: {e}"

def evaluate_quiz_answer(user_answer):
    """Mengevaluasi jawaban kuis menggunakan panggilan API langsung untuk output yang lebih pasti."""
    quiz = st.session_state.quiz_state
    eval_prompt = f'Tugas: Evaluasi jawaban kuis. Abaikan huruf besar/kecil. Pertanyaan: "{quiz["question"]}". Jawaban benar: "{quiz["answer"]}". Jawaban pengguna: "{user_answer}". Mulai respons Anda HANYA dengan [BENAR] atau [SALAH], lalu berikan penjelasan singkat.'
    st.session_state.quiz_state["is_pending"] = False
    # Gunakan panggilan langsung untuk memastikan format [BENAR]/[SALAH] tidak terganggu oleh template chain
    full_prompt_for_eval = PERSONA + eval_prompt
    return _call_groq_raw(full_prompt_for_eval)
