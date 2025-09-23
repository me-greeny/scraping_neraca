import streamlit as st
import pandas as pd
from datetime import datetime
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
st.set_page_config(page_title="Scraper Berita Kepri", layout="wide")
st.title("📡 Scraper Berita Kepulauan Riau")
st.markdown("Aplikasi untuk mengambil data berita dari berbagai portal di Kepri berdasarkan rentang tanggal.")

# --- Sidebar Inputs ---
st.sidebar.header("⚙️ Konfigurasi Scraper")

# Choose portal
portal = st.sidebar.selectbox(
    "📰 Pilih Portal Berita:",
    ["Presmedia", "Sketsa News", "Vision News", "KepriPedia", "Harian Kepri"]
)

# Date Range
st.sidebar.subheader("🗓️ Filter Tanggal")
start_date = st.sidebar.date_input("Tanggal Mulai", value=datetime(2025, 8, 1))
end_date = st.sidebar.date_input("Tanggal Akhir", value=datetime(2025, 8, 31))

# Max Pages
max_pages = st.sidebar.slider(
    "Halaman Maksimal:",
    min_value=1,
    max_value=50,
    value=5,
    help="Jumlah halaman maksimum yang akan di-scrape. Semakin banyak, semakin lama prosesnya."
)

# Action Button
if st.sidebar.button("🚀 Mulai Scraping"):
    if start_date > end_date:
        st.error("❌ Error: Tanggal mulai tidak boleh melebihi tanggal akhir.")
    else:
        with st.spinner(f"Mengambil berita dari **{portal}**... Mohon tunggu ⏳"):
            
            # Mapping portal names to their respective parser functions
            parser_map = {
                "Presmedia": parse_presmedia,
                "Sketsa News": parse_sketsanews,
                "Vision News": parse_vnews,
                "KepriPedia": parse_kepripedia,
                "Harian Kepri": parse_hariankepri
            }

            # Get the correct parser function from the map
            parse_function = parser_map.get(portal)
            
            # Execute the function
            # The 'keyword' argument is not used by these category-based parsers, so we pass None.
            hasil = parse_function(keyword=None, start_date=start_date, end_date=end_date, max_pages=max_pages) if parse_function else []

            if not hasil:
                st.warning(f"⚠️ Tidak ada artikel ditemukan di **{portal}** dalam rentang waktu yang ditentukan.")
            else:
                # Convert results to a DataFrame for better display
                df = pd.DataFrame(hasil)
                
                # Reorder columns for better presentation
                df = df[['tanggal', 'judul', 'isi', 'link']]

                st.success(f"✅ Berhasil mengambil **{len(df)}** artikel dari **{portal}**.")
                
                # Display the data in a table
                st.dataframe(df, use_container_width=True)

                # --- Download Button ---
                @st.cache_data
                def convert_df_to_excel(dataframe):
                    return dataframe.to_excel(index=False).encode('utf-8')

                excel_data = convert_df_to_excel(df)
                
                file_name = f"{portal.lower().replace(' ', '_')}_berita_{start_date}_to_{end_date}.xlsx"
                
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
    "1. Pilih portal berita yang diinginkan.\n"
    "2. Atur rentang tanggal pencarian.\n"
    "3. Tentukan jumlah halaman maksimal untuk di-scrape.\n"
    "4. Klik tombol 'Mulai Scraping'."
)

st.markdown("---")
st.write("Hasil scraping akan ditampilkan di tabel di atas setelah proses selesai.")