#!/usr/bin/env python3
import requests
import time

# Sumber proxy alternatif yang mungkin menyediakan proxy Indonesia
PROXY_SOURCES = [
    "https://www.proxy-list.download/api/v1/get?type=https&country=ID",  # Proxy Indonesia
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=3000&country=ID",  # Proxy Indonesia
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
]

TEST_URL = "https://www.dailymotion.com"
TIMEOUT = 5
MAX_TRY = 30

def get_proxies():
    proxy_list = []
    for source in PROXY_SOURCES:
        print(f"📦 Mengambil daftar proxy dari {source}...")
        try:
            res = requests.get(source, timeout=10)
            res.raise_for_status()
            proxies = res.text.strip().split("\n")
            proxy_list.extend([p.strip() for p in proxies if p.strip()])
            print(f"✅ {len(proxies)} proxy ditemukan dari {source}")
        except Exception as e:
            print(f"❌ Gagal mengambil proxy dari {source}: {e}")
    
    # Hapus duplikat
    proxy_list = list(set(proxy_list))
    print(f"🔍 Total {len(proxy_list)} proxy unik ditemukan.")
    return proxy_list

def is_proxy_working(proxy):
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}",
    }
    try:
        # Tambahkan header untuk meniru browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        
        res = requests.get(
            TEST_URL, 
            proxies=proxies, 
            timeout=TIMEOUT,
            headers=headers
        )
        
        # Periksa apakah konten Indonesia ada di response (contoh sederhana)
        if res.status_code == 200 and "dailymotion" in res.text.lower():
            print(f"✅ Proxy valid dan mungkin Indonesia: {proxy}")
            return True
    except Exception as e:
        pass
    print(f"⚠️ Proxy gagal: {proxy}")
    return False

def main():
    proxies = get_proxies()
    if not proxies:
        print("❌ Tidak ada proxy yang ditemukan.")
        return
    
    print("🔍 Mencoba validasi proxy...")
    working_proxies = []
    
    for i, proxy in enumerate(proxies[:MAX_TRY], 1):
        print(f"🔎 Menguji proxy {i}/{MAX_TRY}: {proxy}")
        if is_proxy_working(proxy):
            working_proxies.append(proxy)
            print(f"🎉 Proxy yang bekerja: {proxy}")
            # Jika Anda hanya butuh satu proxy, bisa langsung return
            # return
        
        time.sleep(1)  # Jeda untuk menghindari banned
    
    if working_proxies:
        print("\n🎉 Daftar proxy yang bekerja:")
        for proxy in working_proxies:
            print(proxy)
    else:
        print("❌ Tidak ada proxy yang valid.")

if __name__ == "__main__":
    main()
