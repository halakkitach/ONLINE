import requests
from bs4 import BeautifulSoup
import concurrent.futures
import subprocess

PROXY_SOURCE_URL = "https://free-proxy-list.net/"
TEST_URL = "https://www.dailymotion.com/video/x8qckyq"
OUTPUT_FILE = "valid_proxies.txt"
USE_IN_SCRIPT = True  # ← ubah ke False kalau gak mau auto-jalan scriptdaily.py

def scrape_proxies():
    print("🔍 Mengambil proxy dari free-proxy-list.net...")
    res = requests.get(PROXY_SOURCE_URL)
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", {"id": "proxylisttable"})

    proxies = []
    for row in table.tbody.find_all("tr"):
        cols = row.find_all("td")
        ip = cols[0].text.strip()
        port = cols[1].text.strip()
        code = cols[2].text.strip()

        if code == "ID":  # Proxy dari Indonesia
            proxy_url = f"http://{ip}:{port}"
            proxies.append(proxy_url)
    return proxies

def check_proxy(proxy_url):
    try:
        print(f"[🔧] Menguji proxy: {proxy_url}")
        res = requests.get(TEST_URL, proxies={
            "http": proxy_url,
            "https": proxy_url
        }, timeout=10)

        if res.status_code == 200 and "geo-restricted" not in res.text.lower():
            print(f"[✅] Proxy OK: {proxy_url}")
            return proxy_url
        else:
            print(f"[❌] Proxy ditolak: {proxy_url}")
    except Exception as e:
        print(f"[❌] Gagal: {proxy_url} → {e}")
    return None

def main():
    proxies = scrape_proxies()
    print(f"\n🔎 Total proxy ID ditemukan: {len(proxies)}\n")

    valid = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_proxy, proxy) for proxy in proxies]
        for f in futures:
            result = f.result()
            if result:
                valid.append(result)

    if valid:
        print("\n✅ Proxy Indonesia yang valid:")
        for p in valid:
            print(p)

        # Simpan ke file
        with open(OUTPUT_FILE, "w") as f:
            for p in valid:
                f.write(p + "\n")
        print(f"\n📁 Disimpan ke {OUTPUT_FILE}")

        if USE_IN_SCRIPT:
            print("\n🚀 Menjalankan scriptdaily.py dengan proxy pertama:")
            try:
                subprocess.run(["python3", "scriptdaily.py", valid[0], TEST_URL], check=True)
            except subprocess.CalledProcessError as e:
                print(f"[❌] scriptdaily.py gagal: {e}")

    else:
        print("\n⚠️ Tidak ada proxy valid ditemukan.")

if __name__ == "__main__":
    main()
