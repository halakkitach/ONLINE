import os
import requests

PROXY_URL = os.environ.get("PROXY_SKIDDLE")  # ambil dari secret

def fetch_proxies_from_json(url):
    try:
        resp = requests.get(url, timeout=12)
        resp.raise_for_status()
        data = resp.json()

        # dictionary untuk menyimpan proxy tiap country
        proxies_by_country = {
            "indonesia": [],
            "hong kong": [],
            "singapore": []
        }

        for p in data:
            ip = p.get("ip")
            port = p.get("port")
            country = p.get("country", "").lower()
            if not ip or not port:
                continue
            proxy_str = f"{ip}:{port}"

            if country.startswith("indonesia"):
                proxies_by_country["indonesia"].append(proxy_str)
            elif country.startswith("hong kong"):
                proxies_by_country["hong kong"].append(proxy_str)
            elif country.startswith("singapore"):
                proxies_by_country["singapore"].append(proxy_str)

        return proxies_by_country

    except Exception as e:
        print(f"⚠️ Gagal fetch dari {url} -> {e}")
        return {"indonesia": [], "hong kong": [], "singapore": []}

def write_output_files(proxies_dict):
    for country, proxies in proxies_dict.items():
        if not proxies:
            continue
        if country == "indonesia":
            filename = "UTTUT2_DOOR.txt"
        elif country == "hong kong":
            filename = "UTTUTHONGKONG_DOOR.txt"
        elif country == "singapore":
            filename = "UTTUTSINGAPORE_DOOR.txt"
        else:
            filename = f"UTTUT{country.upper().replace(' ','')}_DOOR.txt"
        with open(filename, "w") as f:
            f.write("\n".join(sorted(set(proxies))))
        print(f"✅ {len(proxies)} proxy untuk {country} disimpan di {filename}")

if __name__ == "__main__":
    if not PROXY_URL:
        print("⚠️ PROXY_SKIDDLE belum di-set di secret!")
    else:
        proxies_dict = fetch_proxies_from_json(PROXY_URL)
        write_output_files(proxies_dict)
