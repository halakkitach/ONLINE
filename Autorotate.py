#!/usr/bin/env python3
import requests
import os
from dotenv import load_dotenv

# Load env
load_dotenv()

DAILYMOTION_URL = "https://www.dailymotion.com/video/x8qckyq"
FILE_NAME = "testtt7.m3u8"

session = requests.Session()

def get_proxies():
    proxy_url = "https://raw.githubusercontent.com/elliottophellia/proxylist/refs/heads/master/results/http/country/ID/http_ID_checked.txt"
    try:
        res = requests.get(proxy_url, timeout=10)
        res.raise_for_status()
        return res.text.strip().splitlines()
    except Exception as e:
        print(f"[!] Gagal ambil proxy list: {e}")
        return []

def try_with_proxy(proxy):
    proxies = {
        "http": proxy,
        "https": proxy
    }
    try:
        print(f"[•] Coba proxy: {proxy}")

        # Ekstrak video ID
        video_id = DAILYMOTION_URL.split('/video/')[1].split('_')[0]
        meta_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}?embedder=https%3A%2F%2Fsevenhub.id&geo=1"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://sevenhub.id/",
            "Origin": "https://sevenhub.id"
        }

        res = session.get(meta_url, headers=headers, proxies=proxies, timeout=10)
        res.raise_for_status()
        metadata = res.json()

        qualities = metadata.get("qualities", {})
        if not qualities:
            print("[!] Tidak ada kualitas video")
            return False

        best = sorted(qualities.keys(), reverse=True)[0]
        hls_url = qualities[best][0]["url"]
        print(f"[✓] Dapat HLS: {hls_url}")

        m3u_res = session.get(hls_url, headers={
            "User-Agent": headers["User-Agent"],
            "Referer": "https://www.dailymotion.com/"
        }, proxies=proxies, timeout=10)
        m3u_res.raise_for_status()

        with open(FILE_NAME, "w") as f:
            f.write(m3u_res.text)
        print(f"[✓] Tersimpan ke {FILE_NAME}")
        return True

    except Exception as e:
        print(f"[×] Gagal pakai proxy {proxy}: {e}")
        return False

def main():
    proxy_list = get_proxies()
    if not proxy_list:
        print("❌ Tidak ada proxy tersedia")
        return

    for proxy in proxy_list:
        if try_with_proxy(proxy):
            print("✅ Selesai dengan proxy ini")
            return
    print("❌ Gagal dengan semua proxy")

if __name__ == "__main__":
    main()
