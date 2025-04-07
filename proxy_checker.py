#!/usr/bin/env python3
import requests
import time

PROXY_SOURCE = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=3000&country=all&ssl=all&anonymity=all"

TEST_URL = "https://www.dailymotion.com"
TIMEOUT = 5
MAX_TRY = 20

def get_proxies():
    print("📦 Mengambil daftar proxy dari ProxyScrape...")
    try:
        res = requests.get(PROXY_SOURCE)
        res.raise_for_status()
        proxy_list = res.text.strip().split("\n")
        print(f"✅ {len(proxy_list)} proxy ditemukan.")
        return proxy_list
    except Exception as e:
        print(f"❌ Gagal mengambil proxy: {e}")
        return []

def is_proxy_working(proxy):
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}",
    }
    try:
        res = requests.get(TEST_URL, proxies=proxies, timeout=TIMEOUT)
        if res.status_code == 200:
            print(f"✅ Proxy valid: {proxy}")
            return True
    except Exception:
        pass
    print(f"⚠️ Proxy gagal: {proxy}")
    return False

def main():
    proxies = get_proxies()
    print("🔍 Mencoba validasi proxy...")
    for proxy in proxies:
        if is_proxy_working(proxy):
            print(proxy)
            return  # Keluar setelah dapat 1 proxy valid
        time.sleep(1)  # Hindari diblok

    print("❌ Tidak ada proxy yang valid.")

if __name__ == "__main__":
    main()
