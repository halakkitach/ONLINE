import asyncio
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from pathlib import Path
import os
import ast

CONFIG_FILE = Path.home() / "steramest2data_file.txt"

OUTPUT_FILE = Path("ngefilm.m3u")
USER_DATA = "/tmp/ngefilm_profile"
USER_DATA_IFRAME = "/tmp/ngefilm_iframe_profile"
os.makedirs(USER_DATA, exist_ok=True)
os.makedirs(USER_DATA_IFRAME, exist_ok=True)

# --- load config ---
config = {}
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key == "UNIVERSAL_DOMAINS":
                val = ast.literal_eval(val)
            config[key] = val

BASE_URL = config["BASE_URL"]
UNIVERSAL_DOMAINS = config["UNIVERSAL_DOMAINS"]
INDEX_URL = f"{BASE_URL}/page/"
ref = config["ref"]

def get_items():
    headers = {"User-Agent": "Mozilla/5.0"}
    all_results = []
    seen = set()
    for page in range(8, 15):
        url = (
            f"{INDEX_URL}{page}/"
            "?s=&search=advanced&post_type=&index=&orderby=&genre="
            "&movieyear=&country=indonesia&quality="
        )
        print("🔎 Scraping:", url, flush=True)

        try:
            r = requests.get(url, headers=headers, timeout=20)
            r.raise_for_status()
        except Exception as e:
            print("❌ Error load page:", e, flush=True)
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        articles = soup.select("div#gmr-main-load article")

        for art in articles:
            a = art.select_one("h2.entry-title a")
            if not a:
                continue
            detail = a["href"]
            slug = detail.rstrip("/").split("/")[-1]

            if slug in seen:
                continue
            seen.add(slug)

            title = a.get_text(strip=True)
            img = art.select_one("img")
            poster = img["src"] if img else ""

            all_results.append({
                "title": title,
                "slug": slug,
                "poster": poster,
                "detail": detail
            })

        print("➕ Total sementara:", len(all_results), flush=True)

    print("\n🎉 TOTAL FINAL:", len(all_results), "\n", flush=True)
    return all_results

def print_m3u(item, m3u8, out):
    title = item["title"]
    poster = item["poster"]
    out.write(f'#EXTINF:-1 tvg-logo="{poster}" group-title="MOVIES FILM INDONESIA",{title}\n')
    out.write("#EXTVLCOPT:http-user-agent=Mozilla/5.0\n")
    out.write(f"#EXTVLCOPT:http-referrer={ref}\n")
    out.write(f"{m3u8}\n\n")

async def process_item(item):
    slug = item["slug"]
    print(f"\n🎬 MEMPROSES: {slug}", flush=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=[
                f"--user-data-dir={USER_DATA_IFRAME}",
                "--disable-gpu-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-infobars",
                "--ignore-certificate-errors",
                "--use-gl=swiftshader",
                "--no-sandbox",
                "--window-size=1280,720",
            ]
        )
        context = await browser.new_context()
        page = await context.new_page()

        # ----------------------------
        # CARI IFRAME
        # ----------------------------
        iframe = None

        for player in range(1, 6):
            urlp = f"{BASE_URL}/{slug}/?player={player}"
            print(f"➡ Membuka player {player}: {urlp}", flush=True)

            try:
                await page.goto(urlp, timeout=0)
                await page.wait_for_timeout(3000)
            except Exception as e:
                print("⚠ Error goto player:", e, flush=True)
                continue

            frames = await page.query_selector_all("iframe")

            print(f"📌 Jumlah iframe ditemukan: {len(frames)}", flush=True)

            for fr in frames:
                src = await fr.get_attribute("src")
                print("   🔍 iframe src:", src, flush=True)

                if src and any(d in src.lower() for d in UNIVERSAL_DOMAINS):
                    iframe = src
                    print(f"✅ IFRAME UNIVERSAL DITEMUKAN: {iframe}", flush=True)
                    break

            if iframe:
                break

        if not iframe:
            print(f"❌ Skip {slug} — tidak ada iframe universal", flush=True)
            await browser.close()
            return (item, None)

        # ----------------------------
        # INTERCEPT M3U8
        # ----------------------------
        found = None

        async def intercept(route, request):
            nonlocal found
            url = request.url

            if ".m3u8" in url:
                if found is None:
                    found = url
                    print(f"🔥 M3U8 TERDETEKSI: {url}", flush=True)

                return await route.continue_(headers={
                    "referer": iframe,
                    "user-agent": "Mozilla/5.0"
                })

            return await route.continue_()

        await page.route("**/*", intercept)

        print(f"➡ Membuka iframe stream: {iframe}", flush=True)

        try:
            await page.goto(iframe, timeout=0)
        except Exception as e:
            print("⚠ Error membuka iframe:", e, flush=True)

        # waktu tunggu diperpanjang supaya lebih stabil
        for i in range(60):
            if found:
                print(f"🎉 M3U8 BERHASIL DIAMBIL UNTUK {slug}", flush=True)
                break
            await asyncio.sleep(1)

        if not found:
            print(f"⏳ TIMEOUT 60s — tidak ada m3u8 untuk {slug}", flush=True)

        await browser.close()
        return (item, found)

async def main():
    items = get_items()
    if not items:
        print("❌ Tidak ada item!", flush=True)
        return

    sem = asyncio.Semaphore(5)

    async def sem_task(item):
        async with sem:
            return await process_item(item)

    tasks = [sem_task(item) for item in items]
    results = await asyncio.gather(*tasks)

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        for item, m3u8 in results:
            if m3u8:
                print(f"🔥 STREAM FINAL: {m3u8} ({item['slug']})", flush=True)
                print_m3u(item, m3u8, f)

asyncio.run(main())
