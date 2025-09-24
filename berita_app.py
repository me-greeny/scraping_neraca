import streamlit as st
import pandas as pd
from datetime import datetime
import re # Modul untuk regular expression
from parsers import (
    parse_presmedia,
    parse_sketsanews,
    parse_vnews,
    parse_kepripedia,
    parse_hariankepri,
    parse_seputarkita,
    parse_zonakepri,
    parse_ulasan,
    parse_batampos
)

# --- UI Configuration ---
st.set_page_config(page_title="Scraper & Kategorisasi Berita", layout="wide")
st.title("📡 Scraper & Kategorisasi Berita PDRB")
st.markdown("Aplikasi untuk mengambil dan mengkategorikan data berita dari berbagai portal berita di Kepulauan Riau.")

# --- Helper Functions for Categorization ---

@st.cache_data # Cache data agar tidak perlu load file berulang kali
def load_kategori_pdrb():
    """
    Memuat dan memproses file CSV untuk kategori PDRB.
    Mengembalikan dua dictionary, satu untuk produksi dan satu untuk pengeluaran.
    """
    try:
        # Load data dari file CSV yang diunggah
        df_produksi = pd.read_csv("Produksi.csv", header=2)
        df_pengeluaran = pd.read_csv("Pengeluaran.csv", header=2)

        # Proses Kategori Produksi
        kategori_produksi = {}
        current_category = ''
        for _, row in df_produksi.iterrows():
            # Jika kolom 'Kategori' berisi nilai (misal: 'A', 'B'), itu adalah kategori utama
            if pd.notna(row['Kategori']):
                current_category = row['Uraian']
            # Jika kolom 'Uraian' ada isinya, itu adalah sub-kategori
            elif pd.notna(row['Uraian']):
                # Membersihkan uraian dari nomor atau huruf di depannya
                uraian = re.sub(r'^[a-z]\.\s*|^[0-9]+\s*|\s*,\s*$', '', str(row['Uraian'])).strip()
                # Menggunakan uraian sebagai kata kunci (disederhanakan)
                # Contoh: "Industri Makanan dan Minuman" -> ['industri', 'makanan', 'minuman']
                keywords = [word.lower() for word in re.split(r'[\s,]+', uraian) if len(word) > 3]
                kategori_produksi[uraian] = {
                    'kategori_utama': current_category,
                    'keywords': list(set(keywords)) # Hilangkan duplikat
                }

        # Proses Kategori Pengeluaran
        kategori_pengeluaran = {}
        for _, row in df_pengeluaran.iterrows():
            if pd.notna(row['Uraian']):
                uraian = re.sub(r'^[0-9]\.[a-z]\.\s*|^[0-9]\.\s*', '', str(row['Uraian'])).strip()
                # Membersihkan dan mengambil kata kunci dari uraian
                # Contoh: "Pakaian" atau "Transportasi/Angkutan"
                cleaned_uraian = re.sub(r'\(.*\)|/', ' ', uraian) # Hapus kurung dan slash
                keywords = [word.lower() for word in re.split(r'[\s,]+', cleaned_uraian) if len(word) > 3]
                kategori_pengeluaran[uraian] = list(set(keywords))

        return kategori_produksi, kategori_pengeluaran

    except FileNotFoundError:
        st.error("File CSV 'PRODUKSI.csv' atau 'PENGELUARAN.csv' tidak ditemukan. Pastikan file ada di direktori yang sama.")
        return None, None

def classify_article(text, categories, classification_type):
    """
    Mengklasifikasikan teks artikel berdasarkan kata kunci dari kategori yang diberikan.
    """
    if not isinstance(text, str) or not categories:
        return "Tidak Terkategori"

    text_lower = text.lower()
    
    # Skor untuk setiap kategori
    scores = {kategori: 0 for kategori in categories.keys()}

    if classification_type == "Produksi":
        for kategori, data in categories.items():
            for keyword in data['keywords']:
                if keyword in text_lower:
                    scores[kategori] += 1
    else: # Pengeluaran
        for kategori, keywords in categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[kategori] += 1
    
    # Cari kategori dengan skor tertinggi
    max_score = 0
    best_category = "Tidak Terkategori"
    for kategori, score in scores.items():
        if score > max_score:
            max_score = score
            best_category = kategori

    return best_category


# --- Load Kategori ---
kategori_produksi, kategori_pengeluaran = load_kategori_pdrb()


# --- Sidebar Inputs ---
st.sidebar.header("⚙️ Konfigurasi Scraper")

# Choose portal
portal = st.sidebar.selectbox(
    "📰 Pilih Portal Berita:",
    ["Presmedia", "Sketsa News", "Vision News", "KepriPedia", "Harian Kepri", "Seputar Kita", "Zona Kepri", "Ulasan", "Batampos"]
)

# Date Range
st.sidebar.subheader("🗓️ Filter Tanggal")
start_date = st.sidebar.date_input("Tanggal Mulai", value=datetime(2025, 8, 1))
end_date = st.sidebar.date_input("Tanggal Akhir", value=datetime(2025, 8, 31))

# Max Pages
max_pages = st.sidebar.slider(
    "Halaman Maksimal:", min_value=1, max_value=50, value=5,
    help="Jumlah halaman maksimum yang akan di-scrape."
)

# ✅ NEW: Categorization Selection
st.sidebar.subheader("📊 Kategorisasi PDRB")
kategori_pilihan = st.sidebar.selectbox(
    "Pilih Jenis Kategorisasi:",
    ["Tanpa Kategorisasi", "PDRB Produksi", "PDRB Pengeluaran"],
    help="Pilih untuk mengklasifikasikan berita ke dalam kategori PDRB."
)

# Action Button
if st.sidebar.button("🚀 Mulai Scraping & Kategorisasi"):
    if start_date > end_date:
        st.error("❌ Error: Tanggal mulai tidak boleh melebihi tanggal akhir.")
    else:
        with st.spinner(f"Mengambil berita dari **{portal}**... Mohon tunggu ⏳"):
            
            parser_map = {
                "Presmedia": parse_presmedia, "Sketsa News": parse_sketsanews, "Vision News": parse_vnews,
                "KepriPedia": parse_kepripedia, "Harian Kepri": parse_hariankepri, "Seputar Kita": parse_seputarkita,
                "Zona Kepri": parse_zonakepri, "Ulasan": parse_ulasan, "Batampos": parse_batampos
            }

            parse_function = parser_map.get(portal)
            hasil = parse_function(keyword=None, start_date=start_date, end_date=end_date, max_pages=max_pages) if parse_function else []

            if not hasil:
                st.warning(f"⚠️ Tidak ada artikel ditemukan di **{portal}** dalam rentang waktu yang ditentukan.")
            else:
                df = pd.DataFrame(hasil)
                
                # --- Categorization Logic ---
                if kategori_pilihan != "Tanpa Kategorisasi" and (kategori_produksi and kategori_pengeluaran):
                    st.info(f"Melakukan kategorisasi berdasarkan **{kategori_pilihan}**...")
                    if kategori_pilihan == "PDRB Produksi":
                        df['kategori_pdrb'] = df['isi'].apply(lambda x: classify_article(x, kategori_produksi, "Produksi"))
                    elif kategori_pilihan == "PDRB Pengeluaran":
                        df['kategori_pdrb'] = df['isi'].apply(lambda x: classify_article(x, kategori_pengeluaran, "Pengeluaran"))
                    
                    # Reorder columns to show category first
                    cols = ['kategori_pdrb', 'tanggal', 'judul', 'isi', 'link']
                    df = df[[col for col in cols if col in df.columns]]

                else:
                    # Default column order if no categorization
                    df = df[['tanggal', 'judul', 'isi', 'link']]

                st.success(f"✅ Berhasil mengambil **{len(df)}** artikel.")
                st.dataframe(df, use_container_width=True)

                # --- Download Button ---
                @st.cache_data
                def convert_df_to_excel(dataframe):
                    return dataframe.to_excel(index=False).encode('utf-8')

                excel_data = convert_df_to_excel(df)
                file_name = f"{portal.lower().replace(' ', '_')}_{start_date}_to_{end_date}.xlsx"
                
                st.download_button(
                    label="📥 Download Hasil sebagai Excel",
                    data=excel_data,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# --- Instructions ---
st.sidebar.markdown("---")
st.sidebar.info(
    "**Cara Penggunaan:**\n"
    "1. Pilih portal berita.\n"
    "2. Atur rentang tanggal & halaman.\n"
    "3. **Pilih jenis kategorisasi PDRB** (opsional).\n"
    "4. Klik tombol 'Mulai'."
)