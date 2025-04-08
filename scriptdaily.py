#!/usr/bin/python3
import requests
import os
import json
import re
import sys

# Get environment or fallback
proxy = os.environ.get("PROXY", "")
url = os.environ.get("VIDEO_URL", "")
output_file = os.environ.get("OUTPUT_FILE", "output.m3u8")
fallback_url = "https://example.com/fallback.ts"

if not url:
    print("Error: VIDEO_URL is not set")
    sys.exit(1)

# Configure proxy
proxies = {
    'http': proxy,
    'https': proxy
} if proxy else {}

# Configure session
s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/json'
})

def extract_video_id(url):
    """Extract video ID from various Dailymotion URL formats"""
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

def grab(url):
    try:
        print(f"[+] Processing URL: {url}")
        
        # Extract video ID
        video_id = extract_video_id(url)
        if not video_id:
            raise Exception("Could not extract video ID from URL")
            
        print(f"[+] Extracted Video ID: {video_id}")

        # Get metadata
        meta_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}"
        print(f"[+] Fetching metadata from: {meta_url}")
        
        res = s.get(meta_url, proxies=proxies, timeout=10)
        print(f"[+] Status Code: {res.status_code}")
        
        if res.status_code != 200:
            raise Exception(f"Metadata request failed with status {res.status_code}")

        metadata = res.json()

        # Check if qualities exist
        if 'qualities' not in metadata:
            raise Exception("No quality information found in metadata")

        print("[+] Available qualities:")
        for quality in metadata['qualities']:
            print(f" - {quality}")

        # Try to get HLS URL (prefer higher qualities)
        preferred_qualities = ['1080', '720', '480', '360', '240', '144', 'auto']
        hls_url = None
        
        for quality in preferred_qualities:
            if quality in metadata['qualities']:
                hls_url = metadata['qualities'][quality][0]['url']
                print(f"[+] Selected quality: {quality}")
                break

        if not hls_url:
            raise Exception("No valid HLS URL found in qualities")

        print(f"[+] HLS URL: {hls_url}")

        # Get playlist content
        m3u_res = s.get(hls_url, proxies=proxies, timeout=10)
        m3u_res.raise_for_status()
        m3u_content = m3u_res.text.strip()

        if not m3u_content:
            raise Exception("Empty playlist content")

        # Save to file
        with open(output_file, "w") as f:
            f.write(m3u_content)

        print(f"[+] Successfully saved to {output_file}")
        print(f"[+] First line: {m3u_content.splitlines()[0]}")

    except requests.exceptions.RequestException as e:
        print(f"[!] Network error: {str(e)}")
        write_fallback()
    except Exception as e:
        print(f"[!] Error: {str(e)}")
        write_fallback()

def write_fallback():
    """Write fallback URL to output file"""
    with open(output_file, "w") as f:
        f.write(fallback_url + "\n")
    print(f"[!] Fallback URL written to {output_file}")

# Run main function
if __name__ == "__main__":
    grab(url)
