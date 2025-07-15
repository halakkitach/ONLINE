import re 
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# ==== LOAD ENV ====
load_dotenv()

JS_URL = os.getenv("JS_URL")
FALLBACK_URL = os.getenv("FALLBACK_URL")
REFERER = os.getenv("REFERER")

USER_AGENT = "Mozilla/5.0 (Linux; Android 14; RMX3393 Build/UKQ1.230924.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/132.0.6834.163 Mobile Safari/537.36 (Sky, EM150UK, )"
LAST_EXP_FILE = Path("last_exp.txt")
OUTPUT_FILE = Path("SANGAR.m3u8")

def load_last_exp():
    if LAST_EXP_FILE.exists():
        return int(LAST_EXP_FILE.read_text().strip())
    return 0

def save_last_exp(exp):
    LAST_EXP_FILE.write_text(str(exp))

def fetch_best_18037_url():
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": REFERER
    }
    response = requests.get(JS_URL, headers=headers)
    js_content = response.text

    pattern = re.compile(r"initializePlayer\('([^']+)',\s*'([^']+19035[^']+)',\s*'([^']+)'\)")
    matches = pattern.findall(js_content)

    best_exp = 0
    best_url = None

    for vid, url, drm in matches:
        exp_match = re.search(r"exp=(\d+)", url)
        if exp_match:
            exp_value = int(exp_match.group(1))
            if exp_value > best_exp:
                best_exp = exp_value
                best_url = url

    return best_url, best_exp

def main():
    last_exp = load_last_exp()
    best_url, best_exp = fetch_best_18037_url()

    with open(OUTPUT_FILE, "w") as f:
        if best_url and best_exp > last_exp:
            print("✅ URL baru ditemukan dengan exp lebih tinggi:")
            print(best_url)
            f.write(best_url + "\n")
            save_last_exp(best_exp)
        else:
            print("⚠️ Data belum berubah atau tidak ditemukan. Gunakan fallback:")
            print(FALLBACK_URL)
            f.write(FALLBACK_URL + "\n")

if __name__ == "__main__":
    main()
