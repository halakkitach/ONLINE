import os
import requests

def get_indonesian_proxies():
    url = os.getenv("PROXY_JSON_URL")
    if not url:
        print("❌ Environment variable 'PROXY_JSON_URL' tidak ditemukan.")
        return []

    try:
        response = requests.get(url)
        response.raise_for_status()
        proxies = response.json()

        indo_proxies = [
            f"{proxy['ip']}:{proxy['port']}"
            for proxy in proxies
            if proxy.get("country", "").startswith("Indonesia")
        ]
        return indo_proxies

    except Exception as e:
        print("❌ Gagal mengambil atau memproses data:", e)
        return []

if __name__ == "__main__":
    proxies = get_indonesian_proxies()
    if proxies:
        with open("indo_proxies.txt", "w") as f:
            f.write("\n".join(proxies))
        print(f"✅ {len(proxies)} proxy dari Indonesia disimpan di indo_proxies.txt")
    else:
        print("⚠️ Tidak ada proxy Indonesia ditemukan.")
