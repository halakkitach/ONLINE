#!/usr/bin/python3
import requests
import sys
import json
import re
import os
from urllib.parse import urlparse

# Proxy configuration
proxies = {}
if len(sys.argv) >= 2 and sys.argv[1].strip():
    proxy_url = sys.argv[1].strip()
    if not proxy_url.startswith(('http://', 'https://')):
        proxy_url = f"http://{proxy_url}"
    
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    print(f"[+] Using proxy: {proxy_url}")

# Validate arguments
if len(sys.argv) < 3:
    print("Usage: scriptdaily.py [proxy or ''] [dailymotion_url] [output_file]")
    sys.exit(1)

# Get URL and output filename
url = sys.argv[2]
output_file = sys.argv[3] if len(sys.argv) >= 4 else "output.m3u8"
fallback_url = "https://example.com/fallback.ts"

# Configure session with timeout and retry
s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
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

def validate_proxy():
    """Check if proxy is working"""
    try:
        test_url = "https://httpbin.org/ip"
        res = s.get(test_url, proxies=proxies, timeout=5)
        print(f"[+] Proxy test successful. Your IP: {res.json().get('origin')}")
        return True
    except Exception as e:
        print(f"[!] Proxy test failed: {str(e)}")
        return False

def grab(url):
    try:
        print(f"[+] Processing URL: {url}")
        
        # Validate proxy first
        if proxies and not validate_proxy():
            print("[!] Switching to direct connection")
            global proxies
            proxies = {}
        
        # Extract video ID
        video_id = extract_video_id(url)
        if not video_id:
            raise Exception("Could not extract video ID from URL")
            
        print(f"[+] Extracted Video ID: {video_id}")

        # Get metadata with retry
        meta_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}"
        print(f"[+] Fetching metadata from: {meta_url}")
        
        for attempt in range(3):
            try:
                res = s.get(meta_url, proxies=proxies, timeout=10)
                print(f"[+] Status Code: {res.status_code}")
                
                if res.status_code != 200:
                    continue

                try:
                    metadata = res.json()
                    break
                except json.JSONDecodeError:
                    continue
            except:
                if attempt == 2:
                    raise Exception("Failed to get metadata after 3 attempts")
                continue

        # Check for multiple metadata structures
        hls_url = None
        
        # Structure 1: Direct 'hls_url'
        if 'hls_url' in metadata:
            hls_url = metadata['hls_url']
            print("[+] Found HLS URL in metadata root")
        
        # Structure 2: Qualities object
        elif 'qualities' in metadata:
            print("[+] Available qualities:")
            for quality in metadata['qualities']:
                print(f" - {quality}")

            preferred_qualities = ['1080', '720', '480', '360', '240', '144', 'auto']
            for quality in preferred_qualities:
                if quality in metadata['qualities'] and metadata['qualities'][quality]:
                    hls_url = metadata['qualities'][quality][0].get('url')
                    if hls_url:
                        print(f"[+] Selected quality: {quality}")
                        break
        
        # Structure 3: Nested in 'data' object
        elif 'data' in metadata and 'hls_url' in metadata['data']:
            hls_url = metadata['data']['hls_url']
            print("[+] Found HLS URL in metadata.data")

        if not hls_url:
            raise Exception("No valid HLS URL found in metadata")

        print(f"[+] Final HLS URL: {hls_url}")

        # Get playlist content with retry
        for attempt in range(3):
            try:
                m3u_res = s.get(hls_url, proxies=proxies, timeout=15)
                m3u_res.raise_for_status()
                m3u_content = m3u_res.text.strip()
                
                if m3u_content and "#EXTM3U" in m3u_content:
                    break
            except:
                if attempt == 2:
                    raise Exception("Failed to get playlist after 3 attempts")
                continue

        # Save to file
        with open(output_file, "w") as f:
            f.write(m3u_content)

        print(f"[+] Successfully saved to {output_file}")
        print(f"[+] File size: {os.path.getsize(output_file)} bytes")

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

if __name__ == "__main__":
    grab(url)
