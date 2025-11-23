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

CHROME_PATH = "/usr/bin/google-chrome"

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

# =====================================================================
# Ambil daftar item
# =====================================================================
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
        except Exception:
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


# =====================================================================
# Print M3U
# =====================================================================
def print_m3u(item, m3u8, out):
    title = item["title"]
    poster = item["poster"]

    out.write(f'#EXTINF:-1 tvg-logo="{poster}" group-title="MOVIES FILM INDONESIA",{title}\n')
    out.write("#EXTVLCOPT:http-user-agent=Mozilla/5.0\n")
    out.write(f"#EXTVLCOPT:http-referrer={ref}\n")
    out.write(f"{m3u8}\n\n")


# =====================================================================
# Cari iframe universal
# =====================================================================
async def find_valid_iframe(page, slug):
    for player in range(1, 6):
        urlp = f"{BASE_URL}/{slug}/?player={player}"
        print("▶ Coba player:", urlp, flush=True)

        try:
            await page.goto(urlp, timeout=0)
        except:
            continue

        await page.wait_for_timeout(3000)
        frames = await page.query_selector_all("iframe")

        print(f"📌 Iframe ditemukan: {len(frames)}", flush=True)

        for fr in frames:
            src = await fr.get_attribute("src")
            print("   🔍 iframe src:", src, flush=True)

            if src and any(d in src.lower() for d in UNIVERSAL_DOMAINS):
                print("✔ Iframe UNIVERSAL:", src, flush=True)
                return src

        print("❌ Tidak ada iframe universal di player", player, flush=True)

    return None


# =====================================================================
# Extract M3U8 (BENAR PAKAI launch_persistent_context)
# =====================================================================
async def extract_m3u8(iframe_url, p):

    iframe_ctx = await p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_IFRAME,
        executable_path=CHROME_PATH,
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
        ]
    )

    page = iframe_ctx.pages[0] if iframe_ctx.pages else await iframe_ctx.new_page()

    print("▶ Memuat iframe:", iframe_url, flush=True)

    found = None

    async def intercept(route, request):
        nonlocal found
        url = request.url

        if ".m3u8" in url and found is None:
            found = url
            print("🔥 STREAM (intercept):", url, flush=True)

        await route.continue_()

    await page.route("**/*", intercept)

    try:
        await page.goto(iframe_url, timeout=0)
    except:
        pass

    print("⏳ Menunggu stream (max 30s)…", flush=True)

    for i in range(30):
        if found:
            print("✔ Stream muncul setelah", i + 1, "detik", flush=True)
            break
        await asyncio.sleep(1)

    await iframe_ctx.close()
    return found


# =====================================================================
# MAIN (BENAR PAKAI launch_persistent_context)
# =====================================================================
async def main():
    items = get_items()
    if not items:
        return

    async with async_playwright() as p:

        main_ctx = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA,
            executable_path=CHROME_PATH,
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
            ]
        )

        page = main_ctx.pages[0] if main_ctx.pages else await main_ctx.new_page()

        with OUTPUT_FILE.open("w", encoding="utf-8") as f:
            f.write("#EXTM3U\n\n")

            for item in items:
                slug = item["slug"]

                print("\n==========================================")
                print("▶ MEMPROSES:", slug)
                print("==========================================\n")

                iframe = await find_valid_iframe(page, slug)
                if not iframe:
                    print("❌ Tidak ada iframe universal — skip", flush=True)
                    continue

                m3u8 = await extract_m3u8(iframe, p)

                if m3u8:
                    print("🔥 STREAM =", m3u8, flush=True)
                    print_m3u(item, m3u8, f)
                else:
                    print("❌ Stream tidak ditemukan", flush=True)

        await main_ctx.close()


asyncio.run(main())
