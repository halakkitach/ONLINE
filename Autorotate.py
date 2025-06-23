#!/usr/bin/env python3
import requests

DAILYMOTION_URL = "https://www.dailymotion.com/video/x8qckyq"
FILE_NAME = "TESSTSS7.m3u8"
FALLBACK_URL = "https://raw.githubusercontent.com/halakkitach/ONLINE/refs/heads/master/erorya/1infoku.m3u8"

session = requests.Session()

def get_proxies():
    url = "https://raw.githubusercontent.com/elliottophellia/proxylist/refs/heads/master/results/http/country/ID/http_ID_checked.txt"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.text.strip().splitlines()
    except Exception as e:
        print(f"[!] Gagal ambil proxy list: {e}")
        return []

def try_proxy(proxy):
    proxies = {"http": proxy, "https": proxy}
    try:
        print(f"[•] Coba proxy: {proxy}")

        video_id = DAILYMOTION_URL.split('/video/')[1].split('_')[0]
        meta_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}?embedder=https%3A%2F%2Fsevenhub.id&geo=1"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://sevenhub.id/",
            "Origin": "https://sevenhub.id"
        }

        res = session.get(meta_url, headers=headers, proxies=proxies, timeout=10)
        res.raise_for_status()
        meta = res.json()

        qualities = meta.get("qualities", {})
        if not qualities:
            print("[!] Tidak ada kualitas video")
            return False

        best = sorted(qualities.keys(), reverse=True)[0]
        hls_url = qualities[best][0]["url"]
        print(f"[✓] HLS: {hls_url}")

        m3u_res = session.get(hls_url, headers={
            "User-Agent": headers["User-Agent"],
            "Referer": "https://www.dailymotion.com/"
        }, proxies=proxies, timeout=10)
        m3u_res.raise_for_status()

        with open(FILE_NAME, "w") as f:
            f.write(m3u_res.text)

        print(f"[✓] Simpan ke {FILE_NAME}")
        return True

    except Exception as e:
        print(f"[×] Gagal proxy {proxy}: {e}")
        return False

def fallback_write():
    try:
        print(f"[!] Menggunakan fallback: {FALLBACK_URL}")
        res = session.get(FALLBACK_URL, timeout=10)
        res.raise_for_status()
        with open(FILE_NAME, "w") as f:
            f.write(res.text)
        print(f"[✓] Fallback disimpan ke {FILE_NAME}")
    except Exception as e:
        print(f"[×] Gagal ambil fallback: {e}")

def main():
    proxies = get_proxies()
    if not proxies:
        print("❌ Tidak ada proxy tersedia")
        fallback_write()
        return

    for proxy in proxies:
        if try_proxy(proxy):
            print("✅ Berhasil ambil m3u8")
            return

    print("❌ Semua proxy gagal")
    fallback_write()

if __name__ == "__main__":
    main()
