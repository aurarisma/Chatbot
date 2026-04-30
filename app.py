import streamlit as st
import numpy as np
import pickle
import re
import random
import time
import pandas as pd
from difflib import get_close_matches

try:
    from tensorflow.keras.models import load_model
    TF_AVAILABLE = True
except:
    TF_AVAILABLE = False

if TF_AVAILABLE:
    model = load_model("chatbot_model.h5")
else:
    st.error("TensorFlow tidak tersedia")
# ================================
# CONFIG
# ================================
st.set_page_config(
    page_title="Health Bot Clinic",
    page_icon="🏥",
    layout="wide"
)

# ================================
# CSS ULTRA PREMIUM UI (FULL BACKGROUND & CARDS)
# ================================
st.markdown("""
<style>
/* FONT DAN BACKGROUND UTAMA UNTUK SELURUH APLIKASI */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');

/* Background mencakup main content dan sidebar */
[data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: url("https://img.freepik.com/free-vector/clean-medical-background_53876-116875.jpg") !important;
    background-size: cover !important;
    background-attachment: fixed !important;
}

/* Overlay agar konten tetap terbaca jelas */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(255, 255, 255, 0.75); 
    z-index: -1;
}

/* HEADER GLASS MORPHISM */
.header-box {
    background: rgba(255, 255, 255, 0.4);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.6);
    padding: 30px;
    border-radius: 25px;
    color: #1e3d59;
    box-shadow: 0 15px 35px rgba(0,0,0,0.05);
    margin-bottom: 25px;
    text-align: center;
}

/* INFO CARD (DASHBOARD VISUAL) */
.info-card {
    background: rgba(255, 255, 255, 0.9);
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 8px 25px rgba(0,0,0,0.05);
    border: 1px solid rgba(0, 131, 176, 0.1);
    transition: 0.3s;
}

.info-card:hover {
    border-color: #0083b0;
    transform: translateY(-5px);
}

/* CHAT BUBBLE CUSTOM */
.user-msg {
    background: linear-gradient(135deg, #00b4db, #0083b0);
    color: white;
    padding: 15px 20px;
    border-radius: 20px 20px 5px 20px;
    margin: 12px 0;
    max-width: 80%;
    margin-left: auto;
    box-shadow: 0 10px 20px rgba(0,180,219,0.2);
}

.bot-msg {
    background: white;
    color: #2d3748;
    padding: 15px 20px;
    border-radius: 20px 20px 20px 5px;
    margin: 12px 0;
    max-width: 80%;
    box-shadow: 0 10px 20px rgba(0,0,0,0.05);
    border: 1px solid #f0f0f0;
}

/* BUTTONS */
.stButton button {
    border-radius: 12px !important;
}

/* SIDEBAR STYLING */
section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.4) !important;
    backdrop-filter: blur(10px);
}
</style>
""", unsafe_allow_html=True)

# ================================
# LOAD DATA
# ================================
@st.cache_resource
def load_all():
import os
import pandas as pd
import streamlit as st

# SAFE IMPORT TENSORFLOW
try:
    from tensorflow.keras.models import load_model
    TF_AVAILABLE = True
except:
    TF_AVAILABLE = False

# LOAD DATASET
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(BASE_DIR, "DATASET_PHS.xlsx")

if os.path.exists(dataset_path):
    df = pd.read_excel(dataset_path)

    st.write("Preview Dataset:")
    st.write(df.head())

    st.write("Nama Kolom:")
    st.write(df.columns)

    st.success("Dataset berhasil dibaca")
else:
    st.error("Dataset tidak ditemukan")

    # DEBUG CEK DATASET
    st.write("Preview Dataset:")
    st.write(df.head())

    st.write("Nama Kolom:")
    st.write(df.columns)

    st.success("Dataset berhasil dibaca")

else:
    st.error("Dataset tidak ditemukan")
        df.columns = df.columns.str.strip().str.lower()
        qa_pairs = dict(zip(df["pertanyaan"], df["jawaban"]))
        
        return model, tokenizer, label_encoder, responses, qa_pairs
    except:
        # Fallback jika file lokal tidak ditemukan
        return None, None, None, None, {"demam": "Istirahat dan minum air putih.", "batuk": "Minum air hangat."}

model, tokenizer, label_encoder, responses, qa_pairs = load_all()

# ================================
# SESSION
# ================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "patient" not in st.session_state:
    st.session_state.patient = {"nama": "", "umur": "", "status": "Ringan"}

# ================================
# FUNCTION
# ================================
def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())

def get_response(user_input):
    text = clean_text(user_input)
    nama = st.session_state.patient["nama"] or "Pasien"

    if text in qa_pairs:
        return f"Halo {nama}, {qa_pairs[text]}"

    match = get_close_matches(text, qa_pairs.keys(), n=1, cutoff=0.6)
    if match:
        return f"Halo {nama}, {qa_pairs[match[0]]}"

    return f"Maaf {nama}, saya belum menemukan jawaban yang sesuai di database kami. Mohon konsultasi ke tenaga medis."

# ================================
# HEADER
# ================================
st.markdown(f"""
<div class="header-box">
<h1 style='margin:0; color:#0083b0;'>🏥 Health Bot Clinic</h1>
<p style='color:#718096; font-size:1.1rem;'>Edukasi Pola Hidup Sehat Berbasis Kecerdasan Buatan</p>
</div>
""", unsafe_allow_html=True)

# ================================
# DASHBOARD MINI (PASIEN, HISTORY, UMUR)
# ================================
col1, col2, col3 = st.columns(3)

with col1:
    nama_val = st.session_state.patient['nama'] if st.session_state.patient['nama'] else "Pasien Baru"
    st.markdown(f"""
        <div class='info-card'>
            <span style='font-size:1.5rem;'>👤</span><br>
            <span style='font-size:0.8rem; color:gray; font-weight:bold;'>NAMA PASIEN</span><br>
            <span style='font-size:1.1rem; color:#1e3d59;'>{nama_val}</span>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class='info-card'>
            <span style='font-size:1.5rem;'>💬</span><br>
            <span style='font-size:0.8rem; color:gray; font-weight:bold;'>HISTORY</span><br>
            <span style='font-size:1.1rem; color:#1e3d59;'>{len(st.session_state.messages)} Chat</span>
        </div>
    """, unsafe_allow_html=True)

with col3:
    umur_val = st.session_state.patient['umur'] + " Tahun" if st.session_state.patient['umur'] else "-"
    st.markdown(f"""
        <div class='info-card'>
            <span style='font-size:1.5rem;'>🎂</span><br>
            <span style='font-size:0.8rem; color:gray; font-weight:bold;'>UMUR PASIEN</span><br>
            <span style='font-size:1.1rem; color:#1e3d59;'>{umur_val}</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ================================
# SIDEBAR
# ================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#0083b0;'>📋 Data Pasien</h2>", unsafe_allow_html=True)
    
    with st.form("form_pasien"):
        nama_input = st.text_input("Nama Lengkap", st.session_state.patient["nama"])
        umur_input = st.text_input("Usia", st.session_state.patient["umur"])
        btn_save = st.form_submit_button("Simpan & Update", use_container_width=True)

        if btn_save:
            if nama_input and umur_input.isdigit():
                st.session_state.patient["nama"] = nama_input
                st.session_state.patient["umur"] = umur_input
                st.success("Data Diperbarui!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Input tidak valid!")

    st.markdown("---")
    st.markdown("### Pengaturan")
    
    # FITUR MENGHAPUS RIWAYAT CHAT
    if st.button("🗑️ Hapus Riwayat Chat", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()

# ================================
# CHAT AREA
# ================================
chat_area = st.container()

with chat_area:
    if not st.session_state.messages:
        st.markdown("""
            <div style='text-align:center; padding:60px; color:#a0aec0; background:rgba(255,255,255,0.3); border-radius:20px;'>
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
# INPUT CHAT
# ================================
if prompt := st.chat_input("Ketik di sini untuk berkonsultasi..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Sedang memproses..."):
        time.sleep(0.5)
        response = get_response(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
