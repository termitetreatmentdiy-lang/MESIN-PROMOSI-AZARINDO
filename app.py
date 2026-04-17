import streamlit as st
from fpdf import FPDF
import datetime
import os
import uuid
import qrcode
import requests
import json
from bs4 import BeautifulSoup
import fitz  # PyMuPDF untuk baca PDF lebih akurat
from PIL import Image
import time
import re

st.set_page_config(page_title="Ultimate Pro Brochure Engine", layout="wide")

# --- INISIALISASI FOLDER MEMORI ---
CATALOG_DIR = "katalog_tersimpan"
if not os.path.exists(CATALOG_DIR):
    os.makedirs(CATALOG_DIR)

# --- 1. SISTEM BAYANGAN (SHADOW SYNC) ANTI-RESET ---
if 'update_from_ai' not in st.session_state:
    st.session_state.update_from_ai = False

if st.session_state.update_from_ai:
    st.session_state.form_tipe_unit = st.session_state.ai_tipe_unit
    st.session_state.form_headline = st.session_state.ai_headline
    st.session_state.form_engine = st.session_state.ai_engine
    st.session_state.form_hydraulic = st.session_state.ai_hydraulic
    st.session_state.form_bobot = st.session_state.ai_bobot
    st.session_state.form_badge1 = st.session_state.ai_badge1
    st.session_state.form_badge2 = st.session_state.ai_badge2
    st.session_state.form_badge3 = st.session_state.ai_badge3
    st.session_state.form_copywriting = st.session_state.ai_copywriting
    st.session_state.update_from_ai = False

# --- 2. INISIALISASI NILAI DEFAULT KOTAK MERAH ---
defaults = {
    'form_tipe_unit': "EXCAVATOR / WHEEL LOADER",
    'form_headline': "LEBIH CERDAS, LEBIH AKURAT, LEBIH ANDAL",
    'form_engine': "Yanmar 4TNV98",
    'form_hydraulic': "Rexroth",
    'form_bobot': "9600kg",
    'form_badge1': "GARANSI 1 TAHUN",
    'form_badge2': "READY STOCK",
    'form_badge3': "TEKNISI 24/7",
    'form_copywriting': "JUDUL | Deskripsi singkat..."
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

class ProBrochure(FPDF):
    def __init__(self, brand_color, brand_name, website_link, logo_path, wa_number):
        super().__init__()
        self.brand_color = brand_color
        self.brand_name = brand_name
        self.website_link = website_link
        self.logo_path = logo_path
        self.wa_number = wa_number

    def header(self):
        self.set_fill_color(*self.brand_color)
        self.rect(0, 0, 210, 4, 'F')
        if self.logo_path and os.path.exists(self.logo_path):
            self.image(self.logo_path, x=160, y=8, w=40)
        else:
            self.set_font('Helvetica', 'B', 24)
            self.set_text_color(*self.brand_color)
            self.set_xy(160, 10)
            self.cell(40, 10, self.brand_name, align='R')

    def footer(self):
        self.set_y(-25)
        self.set_draw_color(*self.brand_color)
        self.line(10, 272, 200, 272)
        self.set_text_color(50, 50, 50)
        self.set_font('Helvetica', 'B', 9)
        self.cell(0, 6, f'{self.brand_name} - SMART EQUIPMENT FOR SMART BUILDERS', align='C', ln=True)
        clean_link = self.website_link.replace("https://", "").replace("http://", "").rstrip("/")
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 4, f'Authorized Representative: Azarindo.id | {clean_link}', align='C', ln=True)

# --- UI DASHBOARD ---
st.title("🚀 Ultimate Brochure Engine + Full Auto")
st.write("Cukup Tarik Data AI, Kotak Merah akan terisi otomatis!")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. Visual & Identitas")
    brand = st.selectbox("Pilih Merek", ["AIMIX", "TATSUO"])
    
    # Penentuan Link Default Anti-Error
    default_link = "https://azarindo.id" if brand == "AIMIX" else "https://azarindo.id"

    logo_file = st.file_uploader("Upload Logo Brand (PNG Transparan)", type=['png', 'jpg', 'jpeg'])
    foto = st.file_uploader("Upload Foto Unit Utama", type=['png', 'jpg', 'jpeg'])
    
    st.markdown("---")
    model = st.text_input("Tipe Unit", key="form_tipe_unit")
    headline = st.text_input("Headline Utama", key="form_headline")
    
    st.caption("Highlight Spesifikasi Cepat")
    c_sp1, c_sp2, c_sp3 = st.columns(3)
    with c_sp1: spec_engine = st.text_input("Engine / Power", key="form_engine")
    with c_sp2: spec_cap = st.text_input("Hydraulic System", key="form_hydraulic")
    with c_sp3: spec_weight = st.text_input("Bobot Unit", key="form_bobot")

    st.caption("Stempel Kepercayaan (Trust Badges)")
    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1: badge1 = st.text_input("Badge 1", key="form_badge1")
    with b_col2: badge2 = st.text_input("Badge 2", key="form_badge2")
    with b_col3: badge3 = st.text_input("Badge 3", key="form_badge3")

with col2:
    st.subheader("2. AI Data Extractor & Copywriter")
    ref_link = st.text_input("Link Website Produk (Opsional)", default_link)
    
    saved_files = [f for f in os.listdir(CATALOG_DIR) if f.endswith('.pdf')]
    pilihan_katalog = st.selectbox("Pilih File dari Memori / Upload Baru", ["-- Upload Katalog Baru --"] + saved_files)
    
    pdf_path_to_read = None
    if pilihan_katalog == "-- Upload Katalog Baru --":
        pdf_ref = st.file_uploader("Upload Katalog Spesifikasi (PDF)", type=['pdf'])
        if pdf_ref:
            pdf_path_to_read = os.path.join(CATALOG_DIR, pdf_ref.name)
            with open(pdf_path_to_read, "wb") as f:
                f.write(pdf_ref.getbuffer())
            st.success(f"✅ Katalog '{pdf_ref.name}' tersimpan!")
    else:
        pdf_path_to_read = os.path.join(CATALOG_DIR, pilihan_katalog)

    wa_num = st.text_input("Nomor WhatsApp Sales", "+62 823-7626-2781")
    
    if st.button("✨ Tarik Data & Isi Formulir Otomatis"):
        if not ref_link and not pdf_path_to_read:
            st.error("Silakan masukkan Link Website atau pilih/upload Katalog PDF.")
        else:
            with st.spinner("Mesin gemini-2.5-flash sedang mengekstrak data..."):
                scraped_text = ""
                
                # Scraping Website
                if ref_link:
                    try:
                        headers = {"User-Agent": "Mozilla/5.0"}
                        res = requests.get(ref_link, headers=headers, timeout=10)
                        if res.status_code == 200:
                            soup = BeautifulSoup(res.text, 'html.parser')
                            scraped_text += f"DATA WEBSITE:\n{soup.get_text(separator=' ', strip=True)[:3000]}\n\n"
                    except:
                        pass

                # Membaca PDF
                if pdf_path_to_read:
                    try:
                        with fitz.open(pdf_path_to_read) as doc:
                            for page in doc:
                                scraped_text += page.get_text() + "\n"
                    except:
                        pass

                scraped_text = scraped_text[:12000]

                # --- PERBAIKAN INDENTASI DI SINI ---
                if len(scraped_text) < 50:
                    st.error("⚠️ Data sumber tidak terbaca (PDF Scan/Web Proteksi).")
                else:
                    prompt = f"""
                    Anda adalah Data Extractor Alat Berat. Ekstrak teks ini ke JSON:
                    {scraped_text}
                    Format: tipe_unit, headline, engine, hydraulic, bobot, badge1, badge2, badge3, copywriting (JUDUL | Deskripsi).
                    """

                    api_key = st.secrets["GOOGLE_API_KEY"]
                    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    
                    # Auto-Retry 3x
                    for attempt in range(3):
                        try:
                            resp = requests.post(api_url, json=payload, timeout=30)
                            if resp.status_code == 200:
                                raw_res = resp.json()['candidates'][0]['content']['parts'][0]['text']
                                clean_json = raw_res.replace("```json", "").replace("```", "").strip()
                                match = re.search(r'\{.*\}', clean_json, re.DOTALL)
                                if match:
                                    ext = json.loads(match.group(0))
                                    st.session_state.ai_tipe_unit = ext.get('tipe_unit', '-').upper()
                                    st.session_state.ai_headline = ext.get('headline', '-').upper()
                                    st.session_state.ai_engine = ext.get('engine', '-')
                                    st.session_state.ai_hydraulic = ext.get('hydraulic', '-')
                                    st.session_state.ai_bobot = ext.get('bobot', '-')
                                    st.session_state.ai_badge1 = ext.get('badge1', 'GARANSI').upper()
                                    st.session_state.ai_badge2 = ext.get('badge2', 'READY').upper()
                                    st.session_state.ai_badge3 = ext.get('badge3', 'TEKNISI').upper()
                                    st.session_state.ai_copywriting = ext.get('copywriting', '-')
                                    st.session_state.update_from_ai = True
                                    st.rerun()
                                    break
                            time.sleep(2)
                        except:
                            time.sleep(2)

# ==========================================
# FOOTER
# ==========================================
st.markdown("<div class='footer'>Architected & Developed by <b>Adjie Agung</b> <br> VORTEX 4.0 - Heavy-Asset Domination System</div>", unsafe_allow_html=True) 
