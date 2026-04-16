# 🏗️ Ultimate Pro Brochure Engine + AI Automation

Aplikasi pembuat brosur otomatis berbasis AI yang dirancang khusus untuk industri alat berat (Heavy Equipment). Mesin ini mampu membaca katalog PDF atau Website, mengekstrak spesifikasi teknis secara otomatis, dan merancangnya menjadi brosur siap cetak dalam format PDF maupun gambar PNG.

## 🚀 Fitur Utama

- **AI Data Extractor:** Menggunakan Google Gemini AI untuk membaca katalog produk dan mengisi formulir (Tipe Unit, Mesin, Bobot) secara otomatis.
- **AI Copywriting:** Menghasilkan bahasa pemasaran yang maskulin dan persuasif secara instan.
- **Multi-Format Export:** Unduh hasil dalam format **PDF High-Res** untuk cetak atau **PNG** untuk dibagikan di WhatsApp/Sosial Media.
- **Branding Otomatis:** Deteksi merek (AIMIX/TATSUO) yang menyesuaikan skema warna dan logo secara dinamis.
- **Sistem Watermark & QR Code:** Menambahkan watermark transparan anti-plagiat dan QR Code dinamis yang terhubung ke website produk.
- **Shadow Sync Tech:** Memungkinkan pengeditan manual pada data hasil AI tanpa takut terkena auto-refresh/reset.
- **Smart Auto-Retry:** Sistem tangguh yang otomatis mencoba ulang koneksi jika server AI Google sedang sibuk.

## 🛠️ Teknologi yang Digunakan

- **Bahasa:** Python 3.x
- **Framework:** [Streamlit](https://streamlit.io/)
- **AI Engine:** Google Gemini AI (Vertex AI API)
- **PDF Engine:** FPDF2 & PyMuPDF (fitz)
- **Image Processing:** Pillow (PIL)
- **Scraper:** BeautifulSoup4 & Requests

## 📦 Instalasi

1. Clone repository ini:
   ```bash
   git clone [https://github.com/username-anda/repository-anda.git](https://github.com/username-anda/repository-anda.git)
