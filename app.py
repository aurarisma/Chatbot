import streamlit as st
import numpy as np
import pickle
import re
import random
import time
import pandas as pd
import os
from difflib import get_close_matches

# =================================
# SAFE IMPORT TENSORFLOW
# =================================
try:
    from tensorflow.keras.models import load_model
    TF_AVAILABLE = True
except:
    TF_AVAILABLE = False

# =================================
# CONFIG
# =================================
st.set_page_config(
    page_title="Health Bot Clinic",
    page_icon="🏥",
    layout="wide"
)

# =================================
# CSS UI
# =================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');

[data-testid="stAppViewContainer"], 
[data-testid="stSidebar"], 
.stApp {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: url("https://img.freepik.com/free-vector/clean-medical-background_53876-116875.jpg") !important;
    background-size: cover !important;
    background-attachment: fixed !important;
}

.header-box {
    background: rgba(255,255,255,0.85);
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 20px;
}

.info-card {
    background: rgba(255,255,255,0.9);
    padding: 20px;
    border-radius: 18px;
    text-align: center;
    box-shadow: 0 5px 20px rgba(0,0,0,0.05);
}

.user-msg {
    background: #0083b0;
    color: white;
    padding: 14px 18px;
    border-radius: 18px;
    margin: 10px 0;
    margin-left: auto;
    max-width: 80%;
}

.bot-msg {
    background: white;
    color: #2d3748;
    padding: 14px 18px;
    border-radius: 18px;
    margin: 10px 0;
    max-width: 80%;
}
</style>
""", unsafe_allow_html=True)

# =================================
# LOAD DATA
# =================================
@st.cache_resource
def load_all():
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        model_path = os.path.join(BASE_DIR, "chatbot_model.h5")
        tokenizer_path = os.path.join(BASE_DIR, "tokenizer.pkl")
        label_path = os.path.join(BASE_DIR, "label_encoder.pkl")
        responses_path = os.path.join(BASE_DIR, "responses.pkl")
        dataset_path = os.path.join(BASE_DIR, "DATASET_PHS.xlsx")

        st.write("Lokasi Folder:", BASE_DIR)
        st.write("Dataset Path:", dataset_path)

        # LOAD MODEL
        if TF_AVAILABLE and os.path.exists(model_path):
            model = load_model(model_path)
        else:
            model = None
            st.warning("chatbot_model.h5 tidak ditemukan / TensorFlow tidak tersedia")

        # LOAD PICKLE
        if os.path.exists(tokenizer_path):
            tokenizer = pickle.load(open(tokenizer_path, "rb"))
        else:
            tokenizer = None
            st.warning("tokenizer.pkl tidak ditemukan")

        if os.path.exists(label_path):
            label_encoder = pickle.load(open(label_path, "rb"))
        else:
            label_encoder = None
            st.warning("label_encoder.pkl tidak ditemukan")

        if os.path.exists(responses_path):
            responses = pickle.load(open(responses_path, "rb"))
        else:
            responses = None
            st.warning("responses.pkl tidak ditemukan")

        # LOAD DATASET
        if os.path.exists(dataset_path):
            df = pd.read_excel(dataset_path)

            # rapikan nama kolom
            df.columns = df.columns.str.strip().str.lower()

            # DEBUG
            st.write("Preview Dataset:")
            st.write(df.head())

            st.write("Nama Kolom:")
            st.write(df.columns)

            if "pertanyaan" in df.columns and "jawaban" in df.columns:
                qa_pairs = dict(zip(df["pertanyaan"], df["jawaban"]))
                st.success("Dataset berhasil dibaca")
            else:
                st.error("Kolom 'pertanyaan' dan 'jawaban' tidak ditemukan")
                qa_pairs = {}

        else:
            st.error("DATASET_PHS.xlsx tidak ditemukan")
            qa_pairs = {}

        return model, tokenizer, label_encoder, responses, qa_pairs

    except Exception as e:
        st.error(f"Error load data: {str(e)}")

        return None, None, None, None, {
            "demam": "Istirahat yang cukup dan minum air putih.",
            "batuk": "Minum air hangat dan istirahat cukup."
        }

model, tokenizer, label_encoder, responses, qa_pairs = load_all()

# =================================
# SESSION STATE
# =================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "patient" not in st.session_state:
    st.session_state.patient = {
        "nama": "",
        "umur": ""
    }

# =================================
# FUNCTIONS
# =================================
def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text.lower()).strip()

def get_response(user_input):
    text = clean_text(user_input)
    nama = st.session_state.patient["nama"] or "Pasien"

    # exact match
    if text in qa_pairs:
        return f"Halo {nama}, {qa_pairs[text]}"

    # close match
    match = get_close_matches(text, qa_pairs.keys(), n=1, cutoff=0.6)
    if match:
        return f"Halo {nama}, {qa_pairs[match[0]]}"

    return f"Maaf {nama}, saya belum menemukan jawaban yang sesuai di database kami. Silakan konsultasi ke tenaga medis."

# =================================
# HEADER
# =================================
st.markdown("""
<div class="header-box">
    <h1 style='color:#0083b0;'>🏥 Health Bot Clinic</h1>
    <p>Edukasi Pola Hidup Sehat Berbasis Kecerdasan Buatan</p>
</div>
""", unsafe_allow_html=True)

# =================================
# DASHBOARD MINI
# =================================
col1, col2, col3 = st.columns(3)

with col1:
    nama = st.session_state.patient["nama"] if st.session_state.patient["nama"] else "Pasien Baru"
    st.markdown(f"""
    <div class="info-card">
        <h4>👤 Nama Pasien</h4>
        <p>{nama}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="info-card">
        <h4>💬 History</h4>
        <p>{len(st.session_state.messages)} Chat</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    umur = st.session_state.patient["umur"] if st.session_state.patient["umur"] else "-"
    st.markdown(f"""
    <div class="info-card">
        <h4>🎂 Umur</h4>
        <p>{umur}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =================================
# SIDEBAR
# =================================
with st.sidebar:
    st.markdown("## 📋 Data Pasien")

    with st.form("form_pasien"):
        nama_input = st.text_input("Nama Lengkap", st.session_state.patient["nama"])
        umur_input = st.text_input("Usia", st.session_state.patient["umur"])

        submit = st.form_submit_button("Simpan")

        if submit:
            if nama_input and umur_input.isdigit():
                st.session_state.patient["nama"] = nama_input
                st.session_state.patient["umur"] = umur_input
                st.success("Data berhasil disimpan")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Input tidak valid")

    st.markdown("---")

    if st.button("🗑️ Hapus Riwayat Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# =================================
# CHAT AREA
# =================================
if not st.session_state.messages:
    st.markdown("""
    <div style='text-align:center; padding:50px; background:rgba(255,255,255,0.6); border-radius:20px;'>
        <h3>Halo! Apa yang bisa saya bantu hari ini?</h3>
        <p>Silakan ketik pertanyaan kesehatan Anda.</p>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div class='user-msg'>{msg['content']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='bot-msg'><b>⚕️ HealthBot:</b><br>{msg['content']}</div>",
            unsafe_allow_html=True
        )

# =================================
# CHAT INPUT
# =================================
if prompt := st.chat_input("Ketik pertanyaan Anda di sini..."):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.spinner("Sedang memproses..."):
        time.sleep(0.5)
        response = get_response(prompt)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    st.rerun()
