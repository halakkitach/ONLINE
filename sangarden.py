import re
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# ==== LOAD ENV ====
load_dotenv()

JS_URL = os.getenv("JS_URL")
FALLBACK_URL = os.getenv("FALLBACK_URL")
REFERER = os.getenv("REFERER")

USER_AGENT = "Mozilla/5.0 (Linux; Android 14; RMX3393 Build/UKQ1.230924.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/132.0.6834.163 Mobile Safari/537.36 (Sky, EM150UK, )"
EXP_FILE = Path("last_exp.json")

# Mapping ID -> Nama file output
OUTPUT_MAP = {
    "18037": "SANGAR.m3u8",
    "19051": "GASPOL.m3u8",
    # Tambahkan di sini sesuai ID yang diinginkan
}

FILTER_IDS = set(OUTPUT_MAP.keys())

def load_last_exp_map():
    if EXP_FILE.exists():
        return json.loads(EXP_FILE.read_text())
    return {}

def save_last_exp_map(exp_map):
    EXP_FILE.write_text(json.dumps(exp_map, indent=2))

def fetch_best_urls():
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": REFERER
    }
    response = requests.get(JS_URL, headers=headers)
    js_content = response.text

    pattern = re.compile(r"initializePlayer\('([^']+)',\s*'([^']+)',\s*'([^']+)'\)")
    matches = pattern.findall(js_content)

    best_by_id = {}

    for vid, url, drm in matches:
        id_match = re.search(r"/(\d{5,})/", url)
        exp_match = re.search(r"exp=(\d+)", url)

        if id_match and exp_match:
            stream_id = id_match.group(1)
            if stream_id not in FILTER_IDS:
                continue

            exp_value = int(exp_match.group(1))
            if stream_id not in best_by_id or exp_value > best_by_id[stream_id]["exp"]:
                best_by_id[stream_id] = {
                    "url": url,
                    "exp": exp_value
                }

    return best_by_id

def main():
    last_exp_map = load_last_exp_map()
    best_urls = fetch_best_urls()

    if not best_urls:
        print("⚠️ Tidak ditemukan URL valid untuk ID yang difilter.")
        for stream_id, output_name in OUTPUT_MAP.items():
            Path(output_name).write_text(FALLBACK_URL + "\n")
        return

    updated = False
    for stream_id, output_name in OUTPUT_MAP.items():
        output_file = Path(output_name)
        data = best_urls.get(stream_id)
        last_exp = int(last_exp_map.get(stream_id, 0))

        if data and data["exp"] > last_exp:
            print(f"✅ ID {stream_id}: URL baru ditemukan")
            output_file.write_text(data["url"] + "\n")
            last_exp_map[stream_id] = data["exp"]
            updated = True
        else:
            print(f"⏸️ ID {stream_id}: Belum ada update exp, tulis fallback")
            output_file.write_text(FALLBACK_URL + "\n")

    if updated:
        save_last_exp_map(last_exp_map)

if __name__ == "__main__":
    main()
