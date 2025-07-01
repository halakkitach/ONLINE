import os
import requests

def fetch_proxies_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠️ Gagal mengambil dari {url} -> {e}")
        return []

def get_indonesian_proxies():
    urls = {
        "HTTP": os.getenv("PROXY_JSON_URL"),
        "SOCKS4": os.getenv("PROXY_SOCKS4_URL"),
        "SOCKS5": os.getenv("PROXY_SOCKS5_URL")
    }

    all_proxies = []

    for proxy_type, url in urls.items():
        if not url:
            print(f"❌ URL untuk {proxy_type} tidak ditemukan di environment variable.")
            continue

        proxies = fetch_proxies_from_url(url)
        for proxy in proxies:
            if proxy.get("country", "").startswith("Indonesia"):
                ip_port = f"{proxy['ip']}:{proxy['port']}"
                all_proxies.append(ip_port)

    return all_proxies

if __name__ == "__main__":
    proxies = get_indonesian_proxies()
    if proxies:
        with open("UTTUT_DOOR.txt", "w") as f:
            f.write("\n".join(proxies))
        print(f"✅ {len(proxies)} proxy dari Indonesia disimpan di UTTUT_DOOR.txt")
    else:
        print("⚠️ Tidak ada proxy Indonesia ditemukan.")
