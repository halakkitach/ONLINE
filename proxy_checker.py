#!/usr/bin/env python3
import requests
import time

PROXY_SOURCES = [
    "https://www.proxy-list.download/api/v1/get?type=https&country=ID",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=3000&country=ID",
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
    
    proxy_list = list(set(proxy_list))
    print(f"🔍 Total {len(proxy_list)} proxy unik ditemukan.")
    return proxy_list

def is_proxy_working(proxy):
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}",
    }
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept-Language': 'id-ID,id;q=0.9'
        }
        res = requests.get(TEST_URL, proxies=proxies, timeout=TIMEOUT, headers=headers)
        if res.status_code == 200 and "dailymotion" in res.text.lower():
            print(f"✅ Proxy valid: {proxy}")
            return True
    except:
        pass
    print(f"⚠️ Proxy gagal: {proxy}")
    return False

def main():
    proxies = get_proxies()
    working = []

    for i, proxy in enumerate(proxies[:MAX_TRY], 1):
        print(f"🔎 Uji proxy {i}/{MAX_TRY}: {proxy}")
        if is_proxy_working(proxy):
            working.append(proxy)
            break
        time.sleep(1)

    # Simpan ke file walaupun kosong
    with open("valid_proxy.txt", "w") as f:
        if working:
            f.write(working[0] + "\n")
        else:
            f.write("")

    if working:
        print("🎉 Proxy valid ditemukan.")
    else:
        print("❌ Tidak ada proxy yang valid.")

if __name__ == "__main__":
    main()
