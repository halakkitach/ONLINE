import os
import requests

def fetch_proxies_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        proxies = response.json()

        indo_proxies = []
        for proxy in proxies:
            country = proxy.get("country", "")
            if country.startswith("Indonesia"):
                ip = proxy.get("ip")
                port = proxy.get("port")
                if ip and port:
                    indo_proxies.append(f"{ip}:{port}")
        return indo_proxies

    except Exception as e:
        print(f"⚠️ Gagal fetch dari {url} -> {e}")
        return []

def get_all_indonesian_proxies():
    urls = {
        "PROXY_JSON_URL": os.getenv("PROXY_JSON_URL"),
        "PROXY_SOCKS4_URL": os.getenv("PROXY_SOCKS4_URL"),
        "PROXY_SOCKS5_URL": os.getenv("PROXY_SOCKS5_URL")
    }

    all_proxies = []
    for env_var, url in urls.items():
        if not url:
            print(f"❌ Environment variable {env_var} tidak ditemukan.")
            continue
        proxies = fetch_proxies_from_url(url)
        all_proxies.extend(proxies)

    return all_proxies

if __name__ == "__main__":
    proxies = get_all_indonesian_proxies()
    if proxies:
        with open("UTTUT_DOOR.txt", "w") as f:
            f.write("\n".join(proxies))
        print(f"✅ {len(proxies)} proxy dari Indonesia disimpan di UTTUT_DOOR.txt")
    else:
        print("⚠️ Tidak ada proxy Indonesia ditemukan.")
