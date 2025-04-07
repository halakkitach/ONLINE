#!/usr/bin/python3
import requests
import sys
import json

proxies = {}
if len(sys.argv) >= 2 and sys.argv[1] != "":
    proxies = {
        'http': sys.argv[1],
        'https': sys.argv[1]
    }

s = requests.Session()

def grab(url):
    try:
        video_id = url.split('/video/')[1].split('_')[0]
        meta_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}"

        print(f"[+] Fetching metadata from: {meta_url}")
        res = s.get(meta_url, proxies=proxies)
        res.raise_for_status()

        metadata = res.json()
        print("[+] Metadata fetched, available qualities:")

        for q in metadata['qualities']:
            print(f" - {q} : {[item['url'] for item in metadata['qualities'][q]]}")

        # Ambil dari kualitas 'auto'
        hls_url = metadata['qualities']['auto'][0]['url']
        print(f"[+] HLS URL (auto): {hls_url}")

        m3u = s.get(hls_url, proxies=proxies).text

        # Simpan ke file
        with open("trans7.m3u8", "w") as f:
            f.write(m3u)
        print("[+] File trans7.m3u8 berhasil disimpan.")

    except Exception as e:
        print(f"[!] Error: {e}")

if len(sys.argv) >= 3:
    grab(sys.argv[2])
else:
    print("Usage: script.py [proxy or ''] [dailymotion_url]")
