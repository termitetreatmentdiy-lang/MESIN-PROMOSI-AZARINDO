import streamlit as st
from fpdf import FPDF
import datetime
import os
import uuid
import qrcode
import requests
import json
from bs4 import BeautifulSoup
import fitz  # PyMuPDF (Lebih akurat untuk spek alat berat)
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

# --- 2. INISIALISASI NILAI DEFAULT FORM ---
defaults = {
    'form_tipe_unit': "EXCAVATOR / WHEEL LOADER",
    'form_headline': "LEBIH CERDAS, LEBIH AKURAT, LEBIH ANDAL",
    'form_engine': "-",
    'form_hydraulic': "-",
    'form_bobot': "-",
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
    
    # Perbaikan NameError: default_link didefinisikan secara global
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
        with st.spinner("AI sedang membaca data..."):
            try:
                scraped_text = ""
                # Scraping Website dengan User-Agent
                if ref_link:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    res = requests.get(ref_link, headers=headers, timeout=10)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    scraped_text += f"WEBSITE: {soup.get_text()[:2000]}\n"
                
                # Membaca PDF dengan Fitz (PyMuPDF)
                if pdf_path_to_read:
                    with fitz.open(pdf_path_to_read) as doc:
                        for page in doc:
                            scraped_text += page.get_text()
                
                # Prompt ke Gemini
                prompt = f"Ekstrak data spek alat berat berikut ke JSON: {scraped_text[:8000]}. Format: tipe_unit, headline, engine, hydraulic, bobot, badge1, badge2, badge3, copywriting (JUDUL | Deskripsi)."
                
                api_key = st.secrets["GOOGLE_API_KEY"]
                api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                
                resp = requests.post(api_url, json=payload, timeout=30)
                if resp.status_code == 200:
                    raw_res = resp.json()['candidates'][0]['content']['parts'][0]['text']
                    match = re.search(r'\{.*\}', raw_res.replace("```json", "").replace("```", ""), re.DOTALL)
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
            except Exception as e:
                st.error(f"Gagal ekstrak data: {e}")

    final_copy = st.text_area("Hasil Copywriting", key="form_copywriting", height=150)

# --- GENERATE PDF ---
if st.button("🌟 Generate Ultimate Brochure"):
    if not foto:
        st.warning("Upload foto unit dulu, Pak.")
    else:
        with st.spinner("Sedang merancang brosur..."):
            b_color = (0, 82, 155) if brand == "AIMIX" else (204, 0, 0)
            
            # Simpan Logo & Foto Temporary
            l_path = f"temp_l_{uuid.uuid4()}.png"
            if logo_file: 
                with open(l_path, "wb") as f: f.write(logo_file.getbuffer())
            
            f_path = f"temp_f_{uuid.uuid4()}.png"
            with open(f_path, "wb") as f: f.write(foto.getbuffer())

            pdf = ProBrochure(b_color, brand, ref_link, l_path if logo_file else None, wa_num)
            pdf.add_page()
            
            # Hero Image
            pdf.image(f_path, x=40, y=14, w=130)
            
            # Content
            pdf.set_y(115)
            pdf.set_font('Helvetica', 'B', 18)
            pdf.set_text_color(20, 20, 20)
            pdf.multi_cell(0, 10, f"{brand} {model} - {headline}", align='C')
            
            # Spek Table (Gray Box)
            pdf.set_fill_color(245, 245, 245)
            pdf.rect(10, pdf.get_y()+2, 190, 12, 'F')
            pdf.set_y(pdf.get_y()+5)
            pdf.set_font('Helvetica', 'B', 8)
            pdf.cell(63, 6, f"ENGINE: {spec_engine.upper()}", align='C')
            pdf.cell(63, 6, f"HYDRAULIC: {spec_cap.upper()}", align='C')
            pdf.cell(63, 6, f"BOBOT: {spec_weight.upper()}", align='C', ln=True)

            # Copywriting
            pdf.ln(10)
            for line in final_copy.strip().split('\n'):
                if '|' in line:
                    j, d = line.split('|', 1)
                    pdf.set_font('Helvetica', 'B', 11)
                    pdf.set_text_color(*b_color)
                    pdf.cell(0, 6, j.strip().upper(), ln=True)
                    pdf.set_font('Helvetica', '', 10)
                    pdf.set_text_color(50, 50, 50)
                    pdf.multi_cell(0, 5, d.strip())
                    pdf.ln(3)

            # Kontak WhatsApp
            pdf.set_y(250)
            pdf.set_font('Helvetica', 'B', 14)
            pdf.set_text_color(*b_color)
            pdf.cell(0, 10, f"ORDER VIA WHATSAPP: {wa_num}", align='C')

            # Render & Download
            pdf_bytes = bytes(pdf.output(dest='S'))
            st.download_button("⬇️ Download PDF", pdf_bytes, f"Brosur_{model}.pdf", "application/pdf")
            
            # Cleanup
            if os.path.exists(l_path): os.remove(l_path)
            if os.path.exists(f_path): os.remove(f_path)

st.markdown("<div style='text-align: center; color: gray;'>Developed by Adjie Agung - Azarindo System</div>", unsafe_allow_html=True)
