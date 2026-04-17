import streamlit as st
from fpdf import FPDF
import datetime
import os
import uuid
import qrcode
import requests
import json
import fitz  # PyMuPDF
from PIL import Image
import time
import re

st.set_page_config(page_title="Ultimate Pro Brochure Engine", layout="wide")

# --- AKSES MEMORI ---
CATALOG_DIR = "katalog_tersimpan"
if not os.path.exists(CATALOG_DIR):
    os.makedirs(CATALOG_DIR)

# --- SISTEM SYNC DATA ---
if 'data_ai' not in st.session_state:
    st.session_state.data_ai = {}

# --- FUNGSI EKSTRAKSI ---
def tarik_data_ai(scraped_text):
    prompt = f"""
    Ekstrak data spek alat berat berikut ke JSON murni:
    {scraped_text[:10000]}
    Format wajib JSON:
    {{
        "tipe_unit": "...",
        "headline": "...",
        "engine": "...",
        "hydraulic": "...",
        "bobot": "...",
        "badge1": "...",
        "badge2": "...",
        "badge3": "...",
        "copywriting": "JUDUL | Deskripsi"
    }}
    """
    api_key = st.secrets["GOOGLE_API_KEY"]
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    for attempt in range(3):
        try:
            resp = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
            if resp.status_code == 200:
                raw_res = resp.json()['candidates'][0]['content']['parts'][0]['text']
                match = re.search(r'\{.*\}', raw_res.replace("```json", "").replace("```", ""), re.DOTALL)
                if match:
                    return json.loads(match.group(0))
            time.sleep(2)
        except Exception as e:
            st.warning(f"Percobaan {attempt+1} gagal: {e}")
            continue
    return None

# --- FUNGSI GENERATE PDF ---
def generate_pdf(data, logo_file=None, foto_file=None, wa_num="+62 823-7626-2781"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)

    # Judul
    pdf.cell(200, 10, data.get("headline", "BROSUR PRODUK"), ln=True, align="C")
    pdf.ln(10)

    # Logo
    if logo_file:
        logo_path = f"temp_logo_{uuid.uuid4().hex}.png"
        with open(logo_path, "wb") as f: f.write(logo_file.getbuffer())
        pdf.image(logo_path, x=10, y=25, w=40)
        os.remove(logo_path)

    # Foto Unit
    if foto_file:
        foto_path = f"temp_foto_{uuid.uuid4().hex}.png"
        with open(foto_path, "wb") as f: f.write(foto_file.getbuffer())
        pdf.image(foto_path, x=60, y=25, w=100)
        os.remove(foto_path)

    pdf.ln(80)

    # Spesifikasi
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Tipe Unit: {data.get('tipe_unit', '-')}", ln=True)
    pdf.cell(200, 10, f"Engine: {data.get('engine', '-')}", ln=True)
    pdf.cell(200, 10, f"Hydraulic: {data.get('hydraulic', '-')}", ln=True)
    pdf.cell(200, 10, f"Bobot: {data.get('bobot', '-')}", ln=True)

    pdf.ln(10)

    # Badge
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"• {data.get('badge1', '')}", ln=True)
    pdf.cell(200, 10, f"• {data.get('badge2', '')}", ln=True)
    pdf.cell(200, 10, f"• {data.get('badge3', '')}", ln=True)

    pdf.ln(10)

    # Copywriting
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 10, data.get("copywriting", "JUDUL | Deskripsi..."))

    pdf.ln(10)

    # QR WhatsApp
    qr = qrcode.make(f"https://wa.me/{wa_num.replace('+', '').replace(' ', '')}")
    qr_path = f"temp_qr_{uuid.uuid4().hex}.png"
    qr.save(qr_path)
    pdf.image(qr_path, x=160, y=220, w=40)
    os.remove(qr_path)

    # Simpan PDF
    filename = f"brosur_{uuid.uuid4().hex}.pdf"
    pdf.output(filename)
    return filename

# --- UI DASHBOARD ---
st.title("🚀 Ultimate Brochure Engine + Full Auto")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. Visual & Identitas")
    brand = st.selectbox("Pilih Merek", ["AIMIX", "TATSUO"])
    logo_file = st.file_uploader("Upload Logo", type=['png', 'jpg'])
    foto = st.file_uploader("Upload Foto Unit", type=['png', 'jpg'])
    
    st.markdown("---")
    model = st.text_input("Tipe Unit", value=st.session_state.data_ai.get('tipe_unit', "MIXER CONCRETE PUMP"))
    headline = st.text_input("Headline Utama", value=st.session_state.data_ai.get('headline', "READY STOCK UNIT TERBAIK"))
    
    c_sp1, c_sp2, c_sp3 = st.columns(3)
    spec_engine = c_sp1.text_input("Engine", value=st.session_state.data_ai.get('engine', "-"))
    spec_cap = c_sp2.text_input("Hydraulic", value=st.session_state.data_ai.get('hydraulic', "-"))
    spec_weight = c_sp3.text_input("Bobot", value=st.session_state.data_ai.get('bobot', "-"))

    b_col1, b_col2, b_col3 = st.columns(3)
    badge1 = b_col1.text_input("Badge 1", value=st.session_state.data_ai.get('badge1', "GARANSI 1 TAHUN"))
    badge2 = b_col2.text_input("Badge 2", value=st.session_state.data_ai.get('badge2', "READY STOCK"))
    badge3 = b_col3.text_input("Badge 3", value=st.session_state.data_ai.get('badge3', "TEKNISI 24/7"))

with col2:
    st.subheader("2. AI Data Extractor")
    ref_link = st.text_input("Link Website (Opsional)", "https://azarindo.id")
    
    pdf_ref = st.file_uploader("Upload Katalog (PDF)", type=['pdf'])
    if pdf_ref:
        pdf_path = os.path.join(CATALOG_DIR, pdf_ref.name)
        with open(pdf_path, "wb") as f: f.write(pdf_ref.getbuffer())
        st.success(f"✅ Katalog '{pdf_ref.name}' tersimpan!")

    wa_num = st.text_input("WhatsApp Sales", "+62 823-7626-2781")
    
    if st.button("✨ Tarik Data & Isi Formulir Otomatis"):
        with st.spinner("AI sedang membaca data..."):
            scraped_text = ""
            if pdf_ref:
                doc = fitz.open(pdf_path)
                for page in doc: scraped_text += page.get_text()
            
            hasil = tarik_data_ai(scraped_text)
            if hasil:
                st.session_state.data_ai = hasil
                st.success("✅ Data Berhasil Ditarik!")
                st.rerun()
            else:
                st.error("Gagal menarik data. Pastikan API Key benar dan PDF bukan hasil scan gambar.")

    final_copy = st.text_area("Hasil Copywriting", value=st.session_state.data_ai.get('copywriting', "JUDUL | Deskripsi..."), height=150)

# --- TOMBOL GENERATE PDF ---
if st.button("🌟 Generate Ultimate Brochure"):
    data = {
        "tipe_unit": model,
        "headline": headline,
        "engine": spec_engine,
        "hydraulic": spec_cap,
        "bobot": spec_weight,
        "badge1": badge1,
        "badge2": badge2,
        "badge3": badge3,
        "copywriting": final_copy
    }
    filename = generate_pdf(data, logo_file, foto, wa_num)
    with open(filename, "rb") as f:
        st.download_button("⬇️ Download Brosur PDF", f, file_name=filename)

# ==========================================
# FOOTER
# ==========================================
st.markdown("<div class='footer'>Architected & Developed by <b>Adjie Agung</b> <br> VORTEX 4.0 - Heavy-Asset Domination System</div>", unsafe_allow_html=True)
