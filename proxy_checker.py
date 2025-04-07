import requests

def get_proxies():
    url = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
    print("📦 Mengambil daftar proxy...")
    res = requests.get(url)
    proxies = res.text.strip().split('\n')
    return proxies

def is_valid_proxy(proxy):
    try:
        print(f"🌐 Coba proxy: {proxy}")
        r = requests.get("https://www.dailymotion.com", proxies={
            "http": proxy,
            "https": proxy
        }, timeout=5)
        return r.status_code == 200
    except:
        return False

def main():
    proxies = get_proxies()
    for p in proxies:
        if is_valid_proxy(p.strip()):
            print(p.strip())
            return
    print("❌ Tidak ada proxy valid ditemukan")

if __name__ == "__main__":
    main()
