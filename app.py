import streamlit as st
import numpy as np
import pickle
import re
import time
import pandas as pd
import os
from difflib import get_close_matches

# ================================
# SAFE IMPORT TENSORFLOW (OPTIONAL)
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
# CSS (TETAP PREMIUM - TIDAK DIUBAH)
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

[data-testid="stAppViewContainer"]::before {
    content: "";
    position: absolute;
    width: 100%; height: 100%;
    background: rgba(255,255,255,0.75);
    z-index: -1;
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
    padding: 15px 20px;
    border-radius: 20px 20px 20px 5px;
    margin: 12px 0;
    max-width: 80%;
}
</style>
""", unsafe_allow_html=True)

# ================================
# LOAD DATA (AMAN TANPA ERROR)
# ================================
@st.cache_resource
def load_all():
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        dataset_path = os.path.join(BASE_DIR, "DATASET_PHS.xlsx")

        if os.path.exists(dataset_path):
            df = pd.read_excel(dataset_path)
            df.columns = df.columns.str.strip().str.lower()

            if "pertanyaan" in df.columns and "jawaban" in df.columns:
                qa_pairs = dict(zip(df["pertanyaan"], df["jawaban"]))
            else:
                qa_pairs = {}
        else:
            qa_pairs = {}

        return None, None, None, None, qa_pairs

    except:
        return None, None, None, None, {
            "demam": "Istirahat yang cukup dan minum air putih.",
            "batuk": "Minum air hangat dan istirahat cukup.",
            "sakit kepala": "Istirahat cukup dan kurangi stres."
        }

model, tokenizer, label_encoder, responses, qa_pairs = load_all()

# ================================
# SESSION
# ================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "patient" not in st.session_state:
    st.session_state.patient = {"nama": "", "umur": ""}

# ================================
# FUNCTION
# ================================
def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text.lower()).strip()

# 🔥 COMBINE: SMART + SAFE
def get_response(user_input):
    text = clean_text(user_input)
    nama = st.session_state.patient["nama"] or "Pasien"

    # 1. EXACT MATCH
    if text in qa_pairs:
        return f"Halo {nama}, {qa_pairs[text]}"

    # 2. KEYWORD MATCHING (SEMUA DATASET)
    input_words = set(text.split())

    best_match = None
    best_score = 0

    for key, value in qa_pairs.items():
        key_words = set(clean_text(key).split())
        common = input_words.intersection(key_words)

        if len(key_words) > 0:
            score = len(common) / len(key_words)
        else:
            score = 0

        if score > best_score:
            best_score = score
            best_match = key

    if best_match and best_score >= 0.4:
        return f"Halo {nama}, {qa_pairs[best_match]}"

    # 3. FUZZY MATCH
    match = get_close_matches(text, qa_pairs.keys(), n=1, cutoff=0.6)
    if match:
        return f"Halo {nama}, {qa_pairs[match[0]]}"

    # 4. FALLBACK
    return f"Maaf {nama}, saya belum menemukan jawaban yang sesuai di database kami. Silakan konsultasi ke tenaga medis."

# ================================
# HEADER
# ================================
st.markdown("""
<div class="header-box">
<h1>🏥 Health Bot Clinic</h1>
<p>Edukasi Pola Hidup Sehat Berbasis AI</p>
</div>
""", unsafe_allow_html=True)

# ================================
# DASHBOARD
# ================================
col1, col2, col3 = st.columns(3)

with col1:
    nama_val = st.session_state.patient["nama"] or "Pasien Baru"
    st.markdown(f"<div class='info-card'>👤<br>{nama_val}</div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='info-card'>💬<br>{len(st.session_state.messages)} Chat</div>", unsafe_allow_html=True)

with col3:
    umur_val = st.session_state.patient["umur"] or "-"
    st.markdown(f"<div class='info-card'>🎂<br>{umur_val}</div>", unsafe_allow_html=True)

# ================================
# SIDEBAR
# ================================
with st.sidebar:
    with st.form("form_pasien"):
        nama_input = st.text_input("Nama", st.session_state.patient["nama"])
        umur_input = st.text_input("Usia", st.session_state.patient["umur"])

        if st.form_submit_button("Simpan"):
            if nama_input and umur_input.isdigit():
                st.session_state.patient["nama"] = nama_input
                st.session_state.patient["umur"] = umur_input
                st.rerun()

    if st.button("🗑️ Hapus Chat"):
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
        st.markdown(f"<div class='user-msg'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-msg'><b>⚕️ HealthBot:</b><br>{msg['content']}</div>", unsafe_allow_html=True)

# ================================
# INPUT
# ================================
if prompt := st.chat_input("Ketik di sini untuk berkonsultasi..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Sedang memproses..."):
        time.sleep(0.5)
        response = get_response(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
