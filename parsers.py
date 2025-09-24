import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

# --- Helper Function ---
def get_content(url, retries=3):
    """
    Fetches and parses content from a URL with retries and a user-agent header.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=15)
            r.raise_for_status()
            return BeautifulSoup(r.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Gagal mengambil URL {url}: {e}")
            if attempt < retries - 1:
                print(f"Mencoba lagi... ({attempt + 1}/{retries})")
                time.sleep(2)
            else:
                print("Gagal setelah beberapa kali percobaan.")
                return None

# --- Parser for Presmedia ---
def parse_presmedia(keyword=None, start_date=None, end_date=None, max_pages=10):
    # Note: This parser uses category pages, so the 'keyword' argument is ignored.
    results = []
    base_url = "https://presmedia.id/kanal/tanjungpinang/page/"

    for page in range(1, max_pages + 1):
        url = f"{base_url}{page}"
        print(f"🔎 Mengambil halaman Presmedia: {url}")
        soup = get_content(url)
        if not soup:
            continue

        articles = soup.find_all('article')
        if not articles:
            print("Tidak ada artikel lagi ditemukan. Berhenti.")
            break

        for i, article in enumerate(articles):
            title_tag = article.find('h2', class_='entry-title').find('a')
            if not title_tag:
                continue

            link = title_tag['href']
            print(f"📄 Artikel ke-{i+1}: {link}")

            detail_soup = get_content(link)
            if not detail_soup:
                continue

            # Extract date
            date_tag = detail_soup.find('time', class_='entry-date')
            tanggal = None
            if date_tag and date_tag.get('datetime'):
                try:
                    date_str = date_tag['datetime'].split('T')[0]
                    tanggal = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError as e:
                    print(f"[TANGGAL ERROR] {e}")
                    continue

            # Date filtering
            if start_date and end_date:
                if tanggal is None or not (start_date <= tanggal <= end_date):
                    print(f"⏩ Lewat (tanggal tidak sesuai): {tanggal}")
                    continue
            
            judul = title_tag.get('title', 'Tanpa Judul').replace("Tautan ke: ", "")
            content_div = detail_soup.find('div', class_='content')
            isi = content_div.get_text(strip=True) if content_div else ""

            print(f"📅 Tanggal: {tanggal}")
            print(f"📛 Judul: {judul}")
            
            results.append({
                "judul": judul,
                "link": link,
                "tanggal": tanggal,
                "isi": isi
            })
            time.sleep(0.5)
            
    print(f"✅ Total artikel Presmedia berhasil diambil: {len(results)}")
    return results

# --- Parser for Sketsa News ---
def parse_sketsanews(keyword=None, start_date=None, end_date=None, max_pages=10):
    # Note: This parser is very similar to Presmedia and also ignores the 'keyword'.
    results = []
    # The URL structure from the notebook seems to be for a specific sub-category.
    base_url = "https://sketsanews.id/category/3/31/page/"

    for page in range(1, max_pages + 1):
        url = f"{base_url}{page}"
        print(f"🔎 Mengambil halaman Sketsa News: {url}")
        soup = get_content(url)
        if not soup:
            continue

        articles = soup.find_all('article')
        if not articles:
            print("Tidak ada artikel lagi ditemukan. Berhenti.")
            break

        for i, article in enumerate(articles):
            title_tag = article.find('h2', class_='entry-title').find('a')
            if not title_tag:
                continue

            link = title_tag['href']
            print(f"📄 Artikel ke-{i+1}: {link}")

            detail_soup = get_content(link)
            if not detail_soup:
                continue

            # Extract date
            date_tag = detail_soup.find('time', class_='entry-date')
            tanggal = None
            if date_tag and date_tag.get('datetime'):
                try:
                    date_str = date_tag['datetime'].split('T')[0]
                    tanggal = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError as e:
                    print(f"[TANGGAL ERROR] {e}")
                    continue
            
            # Date filtering
            if start_date and end_date:
                if tanggal is None or not (start_date <= tanggal <= end_date):
                    print(f"⏩ Lewat (tanggal tidak sesuai): {tanggal}")
                    continue

            judul = title_tag.get('title', 'Tanpa Judul').replace("Tautan ke: ", "")
            content_div = detail_soup.find('div', class_='content')
            isi = content_div.get_text(strip=True) if content_div else ""

            print(f"📅 Tanggal: {tanggal}")
            print(f"📛 Judul: {judul}")

            results.append({
                "judul": judul,
                "link": link,
                "tanggal": tanggal,
                "isi": isi
            })
            time.sleep(0.5)

    print(f"✅ Total artikel Sketsa News berhasil diambil: {len(results)}")
    return results

# --- Parser for Vision News ---
def parse_vnews(keyword=None, start_date=None, end_date=None, max_pages=10):
    results = []
    base_url = "https://www.vnews.click/category/kepri/tanjungpinang/page/"

    for page in range(1, max_pages + 1):
        url = f"{base_url}{page}/"
        print(f"🔎 Mengambil halaman Vision News: {url}")
        soup = get_content(url)
        if not soup:
            continue

        articles = soup.find_all('article')
        if not articles:
            print("Tidak ada artikel lagi ditemukan. Berhenti.")
            break
            
        for i, article in enumerate(articles):
            title_tag = article.find('h4', class_='entry-title').find('a')
            if not title_tag:
                continue
            
            link = title_tag['href']
            
            # Extract date from list page
            date_tag = article.find('span', class_='mg-blog-date')
            tanggal = None
            if date_tag:
                try:
                    # Example: "16 September 2025 7:11 PM"
                    date_str = date_tag.get_text(strip=True)
                    tanggal = datetime.strptime(date_str, "%d %B %Y %I:%M %p").date()
                except ValueError as e:
                    print(f"[TANGGAL ERROR] {e}")
                    continue
            
            # Date filtering
            if start_date and end_date:
                if tanggal is None or not (start_date <= tanggal <= end_date):
                    print(f"⏩ Lewat (tanggal tidak sesuai): {tanggal}")
                    continue

            print(f"📄 Artikel ke-{i+1}: {link}")
            detail_soup = get_content(link)
            if not detail_soup:
                continue

            judul = detail_soup.find('h1', class_='entry-title').get_text(strip=True) if detail_soup.find('h1') else "Tanpa Judul"
            content_div = detail_soup.find('div', class_='entry-content')
            isi = ""
            if content_div:
                paragraphs = content_div.find_all('p')
                isi = " ".join(p.get_text(strip=True) for p in paragraphs)
            
            print(f"📅 Tanggal: {tanggal}")
            print(f"📛 Judul: {judul}")

            results.append({
                "judul": judul,
                "link": link,
                "tanggal": tanggal,
                "isi": isi
            })
            time.sleep(0.5)

    print(f"✅ Total artikel Vision News berhasil diambil: {len(results)}")
    return results

# --- Parser for KepriPedia ---
def parse_kepripedia(keyword=None, start_date=None, end_date=None, max_pages=10):
    results = []
    base_url = "https://kepripedia.com/category/tanjungpinang/page/"

    for page in range(1, max_pages + 1):
        url = f"{base_url}{page}/"
        print(f"🔎 Mengambil halaman KepriPedia: {url}")
        soup = get_content(url)
        if not soup:
            continue

        articles = soup.select('div.td-module-container.td-category-pos-above')
        if not articles:
            print("Tidak ada artikel lagi ditemukan. Berhenti.")
            break
            
        for i, article in enumerate(articles):
            title_tag = article.find('h3', class_='entry-title').find('a')
            if not title_tag:
                continue
            
            link = title_tag['href']
            
            # Extract date from list page
            date_tag = article.find('time', class_='entry-date')
            tanggal = None
            if date_tag and date_tag.get('datetime'):
                try:
                    date_str = date_tag['datetime'].split('T')[0]
                    tanggal = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError as e:
                    print(f"[TANGGAL ERROR] {e}")
                    continue

            # Date filtering
            if start_date and end_date:
                if tanggal is None or not (start_date <= tanggal <= end_date):
                    print(f"⏩ Lewat (tanggal tidak sesuai): {tanggal}")
                    continue
            
            print(f"📄 Artikel ke-{i+1}: {link}")
            detail_soup = get_content(link)
            if not detail_soup:
                continue

            judul = detail_soup.find('h1', class_='tdb-title-text').get_text(strip=True) if detail_soup.find('h1') else "Tanpa Judul"
            content_div = detail_soup.select_one('div.tdb-block-inner.td-fix-index')
            isi = ""
            if content_div:
                paragraphs = content_div.find_all('p')
                isi = " ".join(p.get_text(strip=True) for p in paragraphs)
            
            print(f"📅 Tanggal: {tanggal}")
            print(f"📛 Judul: {judul}")

            results.append({
                "judul": judul,
                "link": link,
                "tanggal": tanggal,
                "isi": isi
            })
            time.sleep(0.5)

    print(f"✅ Total artikel KepriPedia berhasil diambil: {len(results)}")
    return results

# --- Parser for Harian Kepri ---
def parse_hariankepri(keyword=None, start_date=None, end_date=None, max_pages=10):
    results = []
    base_url = "https://www.hariankepri.com/kanal/daerah/tanjungpinang/page/"
    
    for page in range(1, max_pages + 1):
        url = f"{base_url}{page}/"
        print(f"🔎 Mengambil halaman Harian Kepri: {url}")
        soup = get_content(url)
        if not soup:
            continue

        articles = soup.find_all('div', class_='td-module-meta-info')
        if not articles:
            print("Tidak ada artikel lagi ditemukan. Berhenti.")
            break
        
        for i, article in enumerate(articles):
            # Exclusion logic from the notebook to skip ads/featured posts
            if article.find_parent('div', id='tdi_113') or article.find_parent('div', id='tdi_103'):
                continue

            title_tag = article.find('p', class_='entry-title').find('a')
            if not title_tag:
                continue
            
            link = title_tag['href']
            print(f"📄 Artikel ke-{i+1}: {link}")
            
            detail_soup = get_content(link)
            if not detail_soup:
                continue

            # Extract date
            date_tag = detail_soup.find('time', class_='entry-date')
            tanggal = None
            if date_tag and date_tag.get('datetime'):
                try:
                    date_str = date_tag['datetime'].split('T')[0]
                    tanggal = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError as e:
                    print(f"[TANGGAL ERROR] {e}")
                    continue

            # Date filtering
            if start_date and end_date:
                if tanggal is None or not (start_date <= tanggal <= end_date):
                    print(f"⏩ Lewat (tanggal tidak sesuai): {tanggal}")
                    continue
            
            judul = detail_soup.find('h1', class_='tdb-title-text').get_text(strip=True) if detail_soup.find('h1') else "Tanpa Judul"
            content_div = detail_soup.find('div', class_='td-post-content')
            isi = ""
            if content_div:
                paragraphs = content_div.find_all('p')
                isi = " ".join(p.get_text(strip=True) for p in paragraphs)
            
            print(f"📅 Tanggal: {tanggal}")
            print(f"📛 Judul: {judul}")

            results.append({
                "judul": judul,
                "link": link,
                "tanggal": tanggal,
                "isi": isi
            })
            time.sleep(0.5)

    print(f"✅ Total artikel Harian Kepri berhasil diambil: {len(results)}")
    return results

# --- Parser for Seputar Kita (REVISED) ---
def parse_seputarkita(keyword=None, start_date=None, end_date=None, max_pages=10):
    # Note: 'keyword' tidak digunakan karena URL sudah spesifik ke kategori Tanjungpinang.
    results = []
    # FIXED: URL disesuaikan dengan struktur baru dari kode Anda.
    base_url = "https://www.seputarkita.co/category/daerah/tanjungpinang/page/"

    for page in range(1, max_pages + 1):
        url = f"{base_url}{page}/"
        print(f"🔎 Mengambil halaman Seputar Kita: {url}")
        soup = get_content(url)
        if not soup:
            continue

        # FIXED: Selector artikel disesuaikan dengan kode Anda.
        articles = soup.find_all('div', class_='td-module-meta-info')
        if not articles:
            print("Tidak ada artikel lagi ditemukan. Berhenti.")
            break

        for i, article in enumerate(articles):
            # FIXED: Menambahkan logika eksklusi untuk melewati kontainer yang tidak diinginkan.
            # Ganti 'tdi_58' jika ada ID lain yang perlu di-skip.
            if article.find_parent('div', id='tdi_46') or article.find_parent('div', id='tdi_58'):
                print("⏩ Melewati artikel di dalam kontainer yang diabaikan.")
                continue
            
            # FIXED: Selector judul dan link disesuaikan dengan kode Anda.
            title_tag = article.find('h3', class_='entry-title td-module-title').find('a')
            if not title_tag:
                continue

            link = title_tag.get('href')
            # Judul diambil dari atribut 'title' pada tag <a> untuk kepenuhan
            judul = title_tag.get('title')

            if not link or not judul:
                continue
            
            print(f"📄 Artikel ke-{i+1}: {link}")
            detail_soup = get_content(link)
            if not detail_soup:
                continue
            
            # FIXED: Logika pengambilan tanggal dari halaman detail.
            date_tag = detail_soup.find('time', class_='entry-date')
            tanggal = None
            if date_tag and date_tag.get('datetime'):
                try:
                    date_str = date_tag['datetime'].split('T')[0]
                    tanggal = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError as e:
                    print(f"[TANGGAL ERROR] {e}")
                    continue

            # Menerapkan filter tanggal dinamis dari UI Streamlit.
            if start_date and end_date:
                if tanggal is None or not (start_date <= tanggal <= end_date):
                    print(f"⏩ Lewat (tanggal tidak sesuai): {tanggal}")
                    continue
            
            # Mengambil isi lengkap artikel (penting untuk kategorisasi).
            content_div = detail_soup.find('div', class_='td-post-content')
            isi = ""
            if content_div:
                # Membersihkan elemen yang tidak relevan dari isi berita
                for unwanted in content_div.select('script, style, .td-post-sharing, .td-a-rec'):
                    unwanted.decompose()
                isi = " ".join(p.get_text(strip=True) for p in content_div.find_all('p'))

            print(f"📅 Tanggal: {tanggal}")
            print(f"📛 Judul: {judul}")
            
            results.append({
                "judul": judul,
                "link": link,
                "tanggal": tanggal,
                "isi": isi
            })
            time.sleep(0.5)

    print(f"✅ Total artikel Seputar Kita berhasil diambil: {len(results)}")
    return results

# --- Parser for Zona Kepri (REVISED) ---
def parse_zonakepri(keyword=None, start_date=None, end_date=None, max_pages=10):
    results = []
    # FIXED: URL disesuaikan dengan struktur baru dari kode Anda.
    base_url = "https://zonakepri.com/category/zona-kepri/tanjungpinang/page/"

    for page in range(1, max_pages + 1):
        url = f"{base_url}{page}/"
        print(f"🔎 Mengambil halaman Zona Kepri: {url}")
        soup = get_content(url)
        if not soup:
            continue

        # FIXED: Selector artikel utama disesuaikan dengan kode Anda.
        articles = soup.find_all('div', class_='box-content')
        if not articles:
            print("Tidak ada artikel lagi ditemukan. Berhenti.")
            break

        for i, article in enumerate(articles):
            # FIXED: Menambahkan logika untuk melewati artikel di sidebar.
            if article.find_parent('aside', id='secondary'):
                print("⏩ Melewati artikel di dalam sidebar.")
                continue

            # FIXED: Selector judul dan link disesuaikan.
            title_tag = article.find('h2', class_='entry-title').find('a')
            if not title_tag:
                continue
            
            # Judul diambil dari atribut 'title' dan link dari 'href'
            judul = title_tag.get('title')
            link = title_tag.get('href')

            if not link or not judul:
                continue
            
            print(f"📄 Artikel ke-{i+1}: {link}")
            detail_soup = get_content(link)
            if not detail_soup:
                continue

            # Logika pengambilan tanggal dari halaman detail (sudah sesuai).
            date_tag = detail_soup.find('time', class_='entry-date')
            tanggal = None
            if date_tag and date_tag.get('datetime'):
                try:
                    date_str = date_tag['datetime'].split('T')[0]
                    tanggal = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError as e:
                    print(f"[TANGGAL ERROR] {e}")
                    continue

            # Menerapkan filter tanggal dinamis dari UI Streamlit.
            if start_date and end_date:
                if tanggal is None or not (start_date <= tanggal <= end_date):
                    print(f"⏩ Lewat (tanggal tidak sesuai): {tanggal}")
                    continue

            # Mengambil isi lengkap artikel dari halaman detail.
            content_div = detail_soup.find('div', class_='td-post-content')
            isi = ""
            if content_div:
                # Membersihkan elemen yang tidak relevan.
                for unwanted in content_div.select('script, style, .td-post-sharing, .td-a-rec, .essb_links'):
                    unwanted.decompose()
                isi = " ".join(p.get_text(strip=True) for p in content_div.find_all('p'))

            print(f"📅 Tanggal: {tanggal}")
            print(f"📛 Judul: {judul}")

            results.append({
                "judul": judul,
                "link": link,
                "tanggal": tanggal,
                "isi": isi
            })
            time.sleep(0.5)

    print(f"✅ Total artikel Zona Kepri berhasil diambil: {len(results)}")
    return results

# --- Parser for Ulasan (REVISED) ---
# GANTIKAN FUNGSI LAMA DENGAN YANG INI DI DALAM parsers.py

def parse_ulasan(keyword=None, start_date=None, end_date=None, max_pages=10):
    results = []
    # FIXED: URL disesuaikan dengan struktur baru dari kode Anda.
    # Mengarah ke kategori Tanjungpinang yang lebih spesifik.
    base_url = "https://ulasan.co/category/kepri/tanjungpinang/page/"

    for page in range(1, max_pages + 1):
        url = f"{base_url}{page}/"
        print(f"🔎 Mengambil halaman Ulasan.co: {url}")
        soup = get_content(url)
        if not soup:
            continue

        # FIXED: Mencari semua tag <article> di dalam <main id='primary'>.
        main_content = soup.find('main', id='primary')
        if not main_content:
            print("Tidak ada kontainer artikel utama ditemukan. Berhenti.")
            break
        
        articles = main_content.find_all('article')
        if not articles:
            print("Tidak ada artikel lagi ditemukan. Berhenti.")
            break

        for i, article in enumerate(articles):
            title_tag = article.find('h2', class_='entry-title').find('a')
            if not title_tag:
                continue

            # Judul diambil dari atribut 'title' dan link dari 'href'.
            judul = title_tag.get('title')
            link = title_tag.get('href')

            if not link or not judul:
                continue

            print(f"📄 Artikel ke-{i+1}: {link}")
            detail_soup = get_content(link)
            if not detail_soup:
                continue

            # Logika pengambilan tanggal dari halaman detail (sudah sesuai).
            date_tag = detail_soup.find('time', class_='entry-date')
            tanggal = None
            if date_tag and date_tag.get('datetime'):
                try:
                    date_str = date_tag['datetime'].split('T')[0]
                    tanggal = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError as e:
                    print(f"[TANGGAL ERROR] {e}")
                    continue

            # Menerapkan filter tanggal dinamis dari UI Streamlit.
            if start_date and end_date:
                if tanggal is None or not (start_date <= tanggal <= end_date):
                    print(f"⏩ Lewat (tanggal tidak sesuai): {tanggal}")
                    continue
            
            # Mengambil isi lengkap artikel (penting untuk kategorisasi).
            content_div = detail_soup.find('div', class_='entry-content')
            isi = ""
            if content_div:
                for unwanted in content_div.select('script, style, .essb_links'):
                    unwanted.decompose()
                isi = " ".join(p.get_text(strip=True) for p in content_div.find_all('p'))

            print(f"📅 Tanggal: {tanggal}")
            print(f"📛 Judul: {judul}")

            results.append({
                "judul": judul,
                "link": link,
                "tanggal": tanggal,
                "isi": isi
            })
            time.sleep(0.5)

    print(f"✅ Total artikel Ulasan.co berhasil diambil: {len(results)}")
    return results

# --- Parser for Batampos (REVISED) ---
# GANTIKAN FUNGSI LAMA DENGAN YANG INI DI DALAM parsers.py

def parse_batampos(keyword=None, start_date=None, end_date=None, max_pages=10):
    results = []
    # FIXED: URL disesuaikan dengan struktur subdomain baru dari kode Anda.
    base_url = "https://kepri.batampos.co.id/rubrik/tanjungpinang/page/"

    for page in range(1, max_pages + 1):
        url = f"{base_url}{page}/"
        print(f"🔎 Mengambil halaman Batampos: {url}")
        soup = get_content(url)
        if not soup:
            continue

        # FIXED: Selector artikel disesuaikan.
        articles = soup.find_all('div', class_='td-module-meta-info')
        if not articles:
            print("Tidak ada artikel lagi ditemukan. Berhenti.")
            break

        for i, article in enumerate(articles):
            # FIXED: Menambahkan logika eksklusi untuk melewati kontainer 'Update Kepri'.
            if article.find_parent('div', id='tdi_83'):
                print("⏩ Melewati artikel di dalam kontainer yang diabaikan.")
                continue

            # FIXED: Selector judul dan link disesuaikan dengan kode Anda.
            title_tag = article.find('p', class_='entry-title td-module-title').find('a')
            if not title_tag:
                continue

            link = title_tag.get('href')
            judul = title_tag.get('title')

            if not link or not judul:
                continue

            print(f"📄 Artikel ke-{i+1}: {link}")
            detail_soup = get_content(link)
            if not detail_soup:
                continue

            # Logika pengambilan tanggal dari halaman detail.
            date_tag = detail_soup.find('time', class_='entry-date')
            tanggal = None
            if date_tag and date_tag.get('datetime'):
                try:
                    date_str = date_tag['datetime'].split('T')[0]
                    tanggal = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError as e:
                    print(f"[TANGGAL ERROR] {e}")
                    continue

            # Menerapkan filter tanggal dinamis dari UI Streamlit.
            if start_date and end_date:
                if tanggal is None or not (start_date <= tanggal <= end_date):
                    print(f"⏩ Lewat (tanggal tidak sesuai): {tanggal}")
                    continue
            
            # Mengambil isi lengkap artikel (penting untuk kategorisasi).
            content_div = detail_soup.find('div', class_='td-post-content')
            isi = ""
            if content_div:
                for unwanted in content_div.select('script, style, .td-post-sharing, .td-a-rec, .td-post-views, .td-post-comments, .ads-post'):
                    unwanted.decompose()
                isi = " ".join(p.get_text(strip=True) for p in content_div.find_all('p'))

            print(f"📅 Tanggal: {tanggal}")
            print(f"📛 Judul: {judul}")

            results.append({
                "judul": judul,
                "link": link,
                "tanggal": tanggal,
                "isi": isi
            })
            time.sleep(0.5)

    print(f"✅ Total artikel Batampos berhasil diambil: {len(results)}")
    return results