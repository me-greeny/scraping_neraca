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