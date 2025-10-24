import os
import requests

def fetch_proxies_from_json_api(url):
    """Mengambil proxy dari API JSON"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        proxies = response.json()
        
        indo_proxies = []
        for proxy in proxies:
            country = proxy.get("country", "")
            if country.lower().startswith("indonesia"):
                ip = proxy.get("ip")
                port = proxy.get("port")
                if ip and port:
                    indo_proxies.append(f"{ip}:{port}")
        
        return indo_proxies
    except Exception as e:
        print(f"⚠️ Gagal fetch dari JSON API {url} -> {e}")
        return []

def fetch_proxies_from_plain_text(url):
    """Mengambil proxy dari plain text URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        lines = response.text.splitlines()
        return [line.strip() for line in lines if line.strip()]
    except Exception as e:
        print(f"⚠️ Gagal fetch dari plain text URL {url} -> {e}")
        return []

def get_all_indonesian_proxies():
    """Mengumpulkan semua proxy Indonesia dari environment variables"""
    all_proxies = []
    
    # Ambil semua variabel env yang diawali dengan PROXY_
    for key, url in os.environ.items():
        if key.startswith("PROXY_") and url:
            if url.endswith(".txt"):
                proxies = fetch_proxies_from_plain_text(url)
            else:
                proxies = fetch_proxies_from_json_api(url)
            
            all_proxies.extend(proxies)
    
    # Hapus duplikat dan urutkan
    return sorted(set(all_proxies))

def main():
    """Fungsi utama"""
    proxies = get_all_indonesian_proxies()
    
    if proxies:
        with open("UTTUT_DOOR.txt", "w") as f:
            f.write("\n".join(proxies))
        print(f"✅ {len(proxies)} proxy dari Indonesia disimpan di UTTUT_DOOR.txt")
    else:
        print("⚠️ Tidak ada proxy Indonesia ditemukan.")

if __name__ == "__main__":
    main()
