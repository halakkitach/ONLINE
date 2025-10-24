import os 
import requests

def fetch_proxies_from_json_api(url, target_country=None):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        proxies = response.json()

        collected = []
        for proxy in proxies:
            country = proxy.get("country", "")
            ip = proxy.get("ip")
            port = proxy.get("port")
            if not ip or not port:
                continue
            proxy_str = f"{ip}:{port}"

            # Filter berdasarkan target_country
            if target_country:
                if country.lower().startswith(target_country.lower()):
                    collected.append(proxy_str)
            else:
                collected.append(proxy_str)
        return collected

    except Exception as e:
        print(f"⚠️ Gagal fetch dari JSON API {url} -> {e}")
        return []

def fetch_proxies_from_plain_text(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        lines = response.text.splitlines()
        return [line.strip() for line in lines if line.strip()]
    except Exception as e:
        print(f"⚠️ Gagal fetch dari plain text URL {url} -> {e}")
        return []

def get_all_proxies_by_country():
    """
    Ambil proxy untuk beberapa country sekaligus.
    Country yang didukung: Indonesia, Hong Kong, Singapore
    """
    country_map = {
        "indonesia": [],
        "hong kong": [],
        "singapore": []
    }

    # Ambil semua variabel env yang diawali dengan PROXY_
    for key, url in os.environ.items():
        if not key.startswith("PROXY_") or not url:
            continue
        # Tentukan target country dari nama env
        if "INDONESIA" in key.upper():
            target_country = "indonesia"
        elif "HONG_KONG" in key.upper():
            target_country = "hong kong"
        elif "SINGAPORE" in key.upper():
            target_country = "singapore"
        else:
            continue  # skip country lain

        # Ambil proxy
        if url.endswith(".txt"):
            proxies = fetch_proxies_from_plain_text(url)
        else:
            proxies = fetch_proxies_from_json_api(url, target_country=target_country)

        country_map[target_country].extend(proxies)

    # Hapus duplikat & sort
    for c in country_map:
        country_map[c] = sorted(set(country_map[c]))

    return country_map

if __name__ == "__main__":
    all_proxies = get_all_proxies_by_country()

    # Simpan ke file sesuai country
    if all_proxies["indonesia"]:
        with open("UTTUT_DOOR.txt", "w") as f:
            f.write("\n".join(all_proxies["indonesia"]))
        print(f"✅ {len(all_proxies['indonesia'])} proxy dari Indonesia disimpan di UTTUT_DOOR.txt")
    if all_proxies["hong kong"]:
        with open("UTTUTHONGKONG_DOOR.txt", "w") as f:
            f.write("\n".join(all_proxies["hong kong"]))
        print(f"✅ {len(all_proxies['hong kong'])} proxy dari Hong Kong disimpan di UTTUTHONGKONG_DOOR.txt")
    if all_proxies["singapore"]:
        with open("UTTUTSINGAPORE_DOOR.txt", "w") as f:
            f.write("\n".join(all_proxies["singapore"]))
        print(f"✅ {len(all_proxies['singapore'])} proxy dari Singapore disimpan di UTTUTSINGAPORE_DOOR.txt")

    # Jika semua kosong
    if not any(all_proxies.values()):
        print("⚠️ Tidak ada proxy ditemukan.")
