#!/usr/bin/python3
import requests
import sys
import json
import traceback

def grab(url, proxies=None):
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    })

    try:
        # Ekstrak video ID dengan lebih aman
        if '/video/' not in url:
            print("[❌] URL tidak valid, harus mengandung '/video/'")
            return False
            
        video_id = url.split('/video/')[1].split('_')[0].split('?')[0]
        if not video_id:
            print("[❌] Tidak dapat mengekstrak video ID dari URL")
            return False

        meta_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}"

        print(f"[+] Fetching metadata from: {meta_url}")
        res = s.get(meta_url, proxies=proxies, timeout=15)
        print(f"[DEBUG] Status code: {res.status_code}")
        
        try:
            metadata = res.json()
        except json.JSONDecodeError:
            print(f"[DEBUG] Raw response: {res.text[:500]}")
            print("[❌] Gagal mengurai respons JSON")
            return False

        # Periksa struktur metadata yang diterima
        if not isinstance(metadata, dict):
            print("[❌] Format metadata tidak valid")
            return False

        print("[+] Metadata fetched successfully")
        
        # Periksa ketersediaan kualitas video dengan lebih hati-hati
        if 'qualities' not in metadata:
            print("[!] Error: 'qualities' not found in metadata")
            print("[DEBUG] Metadata keys:", metadata.keys())
            
            # Coba alternatif lokasi HLS
            if 'hls_url' in metadata:
                hls_url = metadata['hls_url']
                print(f"[+] Found HLS URL directly: {hls_url}")
            else:
                print("[❌] Tidak dapat menemukan informasi kualitas video")
                return False
        else:
            print("[+] Available qualities:")
            for q in metadata['qualities']:
                if isinstance(metadata['qualities'][q], list):
                    urls = [item.get('url') for item in metadata['qualities'][q] if 'url' in item]
                    print(f" - {q}: {urls}")
                else:
                    print(f" - {q}: (unexpected format)")

            if 'auto' not in metadata['qualities']:
                print("[!] Warning: 'auto' quality not available, trying other qualities")
                # Coba kualitas tertinggi yang tersedia
                available_qualities = [q for q in metadata['qualities'] if isinstance(metadata['qualities'][q], list)]
                if not available_qualities:
                    print("[❌] Tidak ada kualitas video yang valid ditemukan")
                    return False
                
                best_quality = sorted(available_qualities, reverse=True)[0]
                print(f"[+] Using {best_quality} quality instead of auto")
                hls_url = metadata['qualities'][best_quality][0]['url']
            else:
                hls_url = metadata['qualities']['auto'][0]['url']

        print(f"[+] HLS URL: {hls_url}")

        # Ambil playlist HLS
        hls_res = s.get(hls_url, proxies=proxies, timeout=15)
        if hls_res.status_code != 200:
            print(f"[❌] Gagal mengambil HLS playlist (Status: {hls_res.status_code})")
            return False

        m3u = hls_res.text
        if not m3u or "#EXTM3U" not in m3u:
            print("[⚠️] Warning: File M3U8 tidak valid atau kosong")
            print(f"[DEBUG] HLS content preview:\n{m3u[:500]}")
            return False

        # Simpan file dengan nama berdasarkan video ID
        output_file = f"dailymotion_{video_id}.m3u8"
        with open(output_file, "w") as f:
            f.write(m3u)

        print(f"[✅] File {output_file} berhasil disimpan.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"[❌] Network error: {str(e)}")
        return False
    except Exception as e:
        traceback.print_exc()
        print(f"[❌] Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: scriptdaily.py [dailymotion_url]")
        print("   or: scriptdaily.py [proxy_url] [dailymotion_url]")
        sys.exit(1)

    if len(sys.argv) >= 3:
        proxy_arg = sys.argv[1]
        url = sys.argv[2]
        proxy = {'http': proxy_arg, 'https': proxy_arg} if proxy_arg else None
    else:
        url = sys.argv[1]
        proxy = None

    if proxy:
        print(f"🌐 Mencoba dengan proxy: {proxy['http']}")
    
    success = grab(url, proxy)
    if not success and proxy:
        print("🔁 Gagal dengan proxy, mencoba tanpa proxy...")
        grab(url, None)
    
    sys.exit(0 if success else 1)
