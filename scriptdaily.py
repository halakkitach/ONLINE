#!/usr/bin/python3
import requests
import sys
import json
import traceback

proxies = {}
if len(sys.argv) >= 2 and sys.argv[1] != "":
    proxies = {
        'http': sys.argv[1],
        'https': sys.argv[1]
    }

s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"  # user-agent biar gak ditolak
})

def grab(url):
    try:
        video_id = url.split('/video/')[1].split('_')[0]
        meta_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}"

        print(f"[+] Fetching metadata from: {meta_url}")
        res = s.get(meta_url, proxies=proxies)
        print(f"[DEBUG] Status code: {res.status_code}")
        print(f"[DEBUG] Raw response: {res.text[:500]}")  # lihat isinya

        res.raise_for_status()
        metadata = res.json()

        print("[+] Metadata fetched, available qualities:")
        for q in metadata.get('qualities', {}):
            urls = [item.get('url') for item in metadata['qualities'][q]]
            print(f" - {q} : {urls}")

        if 'auto' not in metadata['qualities']:
            print("[!] Error: 'auto' quality not available.")
            return

        hls_url = metadata['qualities']['auto'][0]['url']
        print(f"[+] HLS URL (auto): {hls_url}")

        hls_res = s.get(hls_url, proxies=proxies)
        print(f"[DEBUG] HLS response status: {hls_res.status_code}")
        print(f"[DEBUG] HLS content preview:\n{hls_res.text[:500]}")

        m3u = hls_res.text

        if "#EXTM3U" not in m3u:
            print("[⚠️] Warning: Ini mungkin bukan file .m3u8 yang valid!")

        with open("trans7.m3u8", "w") as f:
            f.write(m3u)

        print("[✅] File trans7.m3u8 berhasil disimpan.")

    except Exception as e:
        traceback.print_exc()
        print(f"[❌] Error: {e}")

if len(sys.argv) >= 3:
    grab(sys.argv[2])
else:
    print("Usage: script.py [proxy or ''] [dailymotion_url]")
