# ================================
# HAPUS SEMUA DEBUG / WARNING DI TAMPILAN
# AGAR TIDAK MUNCUL:
# - Lokasi Folder
# - Dataset Path
# - chatbot_model.h5 tidak ditemukan
# - tokenizer.pkl tidak ditemukan
# - label_encoder.pkl tidak ditemukan
# - responses.pkl tidak ditemukan
# ================================

import streamlit as st
import numpy as np
import pickle
import re
import time
import pandas as pd
import os
from difflib import get_close_matches

# ================================
# SAFE IMPORT TENSORFLOW
# ================================
try:
    from tensorflow.keras.models import load_model
    TF_AVAILABLE = True
except:
    TF_AVAILABLE = False

# ================================
# CONFIG
# ================================
st.set_page_config(
    page_title="Health Bot Clinic",
    page_icon="🏥",
    layout="wide"
)

# ================================
# CSS PREMIUM UI (PUNYA ASLI)
# ================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');

[data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: url("https://img.freepik.com/free-vector/clean-medical-background_53876-116875.jpg") !important;
    background-size: cover !important;
    background-attachment: fixed !important;
}

.header-box {
    background: rgba(255,255,255,0.4);
    backdrop-filter: blur(15px);
    padding: 30px;
    border-radius: 25px;
    text-align: center;
    margin-bottom: 25px;
}

.info-card {
    background: rgba(255,255,255,0.9);
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 8px 25px rgba(0,0,0,0.05);
}

.user-msg {
    background: linear-gradient(135deg, #00b4db, #0083b0);
    color: white;
    padding: 15px 20px;
    border-radius: 20px 20px 5px 20px;
    margin: 12px 0;
    max-width: 80%;
    margin-left: auto;
}

.bot-msg {
    background: white;
    color: #2d3748;
    padding: 15px 20px;
    border-radius: 20px 20px 20px 5px;
    margin: 12px 0;
    max-width: 80%;
}
</style>
""", unsafe_allow_html=True)

# ================================
# LOAD DATA (TANPA DEBUG TAMPILAN)
# ================================
@st.cache_resource
def load_all():
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        dataset_path = os.path.join(BASE_DIR, "DATASET_PHS.xlsx")

        # HANYA BACA DATASET EXCEL
        if os.path.exists(dataset_path):
            df = pd.read_excel(dataset_path)

            # rapikan nama kolom
            df.columns = df.columns.str.strip().str.lower()

            if "pertanyaan" in df.columns and "jawaban" in df.columns:
                qa_pairs = dict(zip(df["pertanyaan"], df["jawaban"]))
            else:
                qa_pairs = {}

        else:
            qa_pairs = {}

        # model dll tidak wajib untuk versi deploy aman
        model = None
        tokenizer = None
        label_encoder = None
        responses = None

        return model, tokenizer, label_encoder, responses, qa_pairs

    except:
        return None, None, None, None, {
            "demam": "Istirahat yang cukup dan minum air putih.",
            "batuk": "Minum air hangat dan istirahat cukup."
        }

model, tokenizer, label_encoder, responses, qa_pairs = load_all()

# ================================
# SESSION
# ================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "patient" not in st.session_state:
    st.session_state.patient = {
        "nama": "",
        "umur": ""
    }

# ================================
# FUNCTION
# ================================
def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text.lower()).strip()

def get_response(user_input):
    text = clean_text(user_input)
    nama = st.session_state.patient["nama"] or "Pasien"

    # exact match
    if text in qa_pairs:
        return f"Halo {nama}, {qa_pairs[text]}"

    # similar match
    match = get_close_matches(text, qa_pairs.keys(), n=1, cutoff=0.6)
    if match:
        return f"Halo {nama}, {qa_pairs[match[0]]}"

    return f"Maaf {nama}, saya belum menemukan jawaban yang sesuai di database kami. Silakan konsultasi ke tenaga medis."

# ================================
# HEADER
# ================================
st.markdown("""
<div class="header-box">
<h1 style='margin:0; color:#0083b0;'>🏥 Health Bot Clinic</h1>
<p style='color:#718096; font-size:1.1rem;'>
Edukasi Pola Hidup Sehat Berbasis Kecerdasan Buatan
</p>
</div>
""", unsafe_allow_html=True)

# ================================
# DASHBOARD
# ================================
col1, col2, col3 = st.columns(3)

with col1:
    nama_val = st.session_state.patient["nama"] if st.session_state.patient["nama"] else "Pasien Baru"
    st.markdown(f"""
    <div class="info-card">
        👤<br>
        <b>NAMA PASIEN</b><br>
        {nama_val}
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="info-card">
        💬<br>
        <b>HISTORY</b><br>
        {len(st.session_state.messages)} Chat
    </div>
    """, unsafe_allow_html=True)

with col3:
    umur_val = st.session_state.patient["umur"] if st.session_state.patient["umur"] else "-"
    st.markdown(f"""
    <div class="info-card">
        🎂<br>
        <b>UMUR PASIEN</b><br>
        {umur_val}
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ================================
# SIDEBAR
# ================================
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

# ================================
# CHAT AREA
# ================================
if not st.session_state.messages:
    st.markdown("""
    <div style='text-align:center; padding:60px; background:rgba(255,255,255,0.3); border-radius:20px;'>
        <h3>Halo! Apa yang bisa saya bantu hari ini?</h3>
        <p>Silakan masukkan pertanyaan atau keluhan Anda di bawah.</p>
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

# ================================
# INPUT CHAT
# ================================
if prompt := st.chat_input("Ketik di sini untuk berkonsultasi..."):
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
