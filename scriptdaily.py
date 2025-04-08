#!/usr/bin/env python3
import requests
import os
import json
import re
import sys

# Baca proxy dari environment variable
proxies = {}
proxy_env = os.environ.get("PROXY", "")
if proxy_env:
    proxies = {
        'http': proxy_env,
        'https': proxy_env
    }

url = os.environ.get("VIDEO_URL", "")
output_file = os.environ.get("OUTPUT_FILE", "output.m3u8")
fallback_url = "https://example.com/fallback.ts"

if not url:
    print("Error: VIDEO_URL is not set")
    sys.exit(1)

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/json'
})

def extract_video_id(url):
    patterns = [
        r'/video/([^_?/]+)',
        r'/([^_?/]+)$',
        r'x([^_?/]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def write_fallback():
    with open(output_file, "w") as f:
        f.write(fallback_url + "\n")
    print(f"[!] Fallback URL written to {output_file}")

def grab(url):
    try:
        print(f"[+] Processing URL: {url}")
        video_id = extract_video_id(url)
        if not video_id:
            raise Exception("Could not extract video ID from URL")
        print(f"[+] Extracted Video ID: {video_id}")

        meta_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}"
        res = s.get(meta_url, proxies=proxies, timeout=10)
        if res.status_code != 200:
            raise Exception(f"Metadata request failed: {res.status_code}")
        metadata = res.json()

        if 'qualities' not in metadata:
            raise Exception("No quality info in metadata")

        preferred_qualities = ['1080', '720', '480', '360', '240', '144', 'auto']
        hls_url = None
        for q in preferred_qualities:
            if q in metadata['qualities']:
                hls_url = metadata['qualities'][q][0]['url']
                print(f"[+] Using quality: {q}")
                break

        if not hls_url:
            raise Exception("No valid HLS URL found")

        m3u = s.get(hls_url, proxies=proxies, timeout=10).text.strip()
        if not m3u:
            raise Exception("Empty playlist")

        with open(output_file, "w") as f:
            f.write(m3u)
        print(f"[+] Saved to {output_file}")
        print(f"[+] First line: {m3u.splitlines()[0]}")

    except Exception as e:
        print(f"[!] Error: {e}")
        write_fallback()

if __name__ == "__main__":
    grab(url)
