import streamlit as st
import pandas as pd
from datetime import datetime
import re
from collections import Counter
from parsers import (
    parse_presmedia, parse_sketsanews, parse_vnews,
    parse_kepripedia, parse_hariankepri, parse_seputarkita,
    parse_zonakepri, parse_ulasan, parse_batampos
)

# --- UI Configuration ---
st.set_page_config(page_title="Scraper & Kategorisasi Berita", layout="wide")
st.title("📡 Scraper & Kategorisasi Berita PDRB Multi-Label")
st.markdown("Aplikasi untuk mengambil berita dan mengklasifikasikannya ke dalam beberapa kategori PDRB spesifik.")

# --- Helper Functions for New Categorization Logic ---

@st.cache_data
def load_and_process_categories():
    """
    Memuat kategori dan kata kunci dari file Produksi.csv dan Pengeluaran.csv.
    Menggabungkan keduanya menjadi satu dictionary.
    """
    all_categories = {}
    try:
        # Muat kedua file CSV
        df_produksi = pd.read_csv("Produksi.csv")
        df_pengeluaran = pd.read_csv("Pengeluaran.csv")
        
        # Gabungkan kedua DataFrame
        df_combined = pd.concat([df_produksi, df_pengeluaran], ignore_index=True)

        for _, row in df_combined.iterrows():
            # Pastikan ada nilai di kolom Kategori dan Uraian
            if pd.notna(row['Kategori']) and pd.notna(row['Uraian']):
                kategori = str(row['Kategori']).strip()
                # Uraian berisi keywords yang dipisahkan oleh newline
                # Bersihkan setiap keyword: lowercase, hapus spasi, dan filter kata pendek
                keywords = [
                    re.sub(r'[^a-z0-9\s]', '', word.lower().strip())
                    for word in str(row['Uraian']).split('\n')
                    if len(word.strip()) > 2
                ]
                # Hindari duplikat keywords
                all_categories[kategori] = list(set(keywords))
        
        return all_categories

    except FileNotFoundError as e:
        st.error(f"❌ File tidak ditemukan: {e.filename}. Pastikan 'Produksi.csv' dan 'Pengeluaran.csv' ada di direktori yang sama.")
        return None
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat file kategori: {e}")
        return None

def classify_article_multi_label(text, categories):
    """
    Mengklasifikasikan teks artikel ke dalam maksimal 3 kategori teratas.
    """
    if not isinstance(text, str) or not categories:
        return ["Bukan Kategori PDRB"]

    text_lower = text.lower()
    scores = Counter()

    # Hitung skor untuk setiap kategori berdasarkan jumlah keyword yang cocok
    for category, keywords in categories.items():
        for keyword in keywords:
            # Menggunakan word boundary (\b) agar tidak salah cocok (misal: 'emas' di dalam 'kemasan')
            if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                scores[category] += 1
    
    # Jika tidak ada keyword yang cocok sama sekali
    if not scores:
        return ["Bukan Kategori PDRB"]

    # Urutkan kategori berdasarkan skor tertinggi dan ambil top 3
    top_categories = [category for category, count in scores.most_common(3)]
    
    return top_categories

# --- Load Categories ---
all_pdrb_categories = load_and_process_categories()

# --- Sidebar Inputs ---
st.sidebar.header("⚙️ Konfigurasi Scraper")

portal = st.sidebar.selectbox(
    "📰 Pilih Portal Berita:",
    ["Presmedia", "Sketsa News", "Vision News", "KepriPedia", "Harian Kepri", "Seputar Kita", "Zona Kepri", "Ulasan", "Batampos"]
)

st.sidebar.subheader("🗓️ Filter Tanggal")
start_date = st.sidebar.date_input("Tanggal Mulai", value=datetime(2025, 8, 1))
end_date = st.sidebar.date_input("Tanggal Akhir", value=datetime(2025, 8, 31))

max_pages = st.sidebar.slider(
    "Halaman Maksimal:", min_value=1, max_value=100, value=5,
    help="Jumlah halaman maksimum yang akan di-scrape."
)

st.sidebar.subheader("📊 Kategorisasi PDRB")
do_classification = st.sidebar.toggle(
    'Aktifkan Kategorisasi Otomatis', value=True,
    help="Jika aktif, setiap berita akan diklasifikasikan ke dalam kategori PDRB."
)

# --- Action Button ---
if st.sidebar.button("🚀 Mulai Proses"):
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
                
                # --- New Multi-Label Categorization Logic ---
                if do_classification and all_pdrb_categories:
                    st.info("Melakukan klasifikasi multi-label...")
                    
                    # Terapkan fungsi klasifikasi
                    kategori_list = df['isi'].apply(lambda x: classify_article_multi_label(x, all_pdrb_categories))
                    
                    # Buat kolom baru dari hasil klasifikasi (maksimal 3)
                    kategori_df = pd.DataFrame(kategori_list.tolist(), index=kategori_list.index).fillna('')
                    for i in range(3):
                        col_name = f'Kategori {i+1}'
                        df[col_name] = kategori_df[i] if i in kategori_df.columns else ''

                    # Susun ulang urutan kolom
                    df = df[['Kategori 1', 'Kategori 2', 'Kategori 3', 'tanggal', 'judul', 'isi', 'link']]
                else:
                    df = df[['tanggal', 'judul', 'isi', 'link']]

                st.success(f"✅ Berhasil memproses **{len(df)}** artikel.")
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
    "1. Pilih portal berita & atur filter.\n"
    "2. Pastikan toggle **'Aktifkan Kategorisasi'** menyala jika ingin mengklasifikasikan berita.\n"
    "3. Klik tombol **'Mulai Proses'**."
)