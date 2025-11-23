import asyncio 
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from pathlib import Path
import os
import ast
import json

CONFIG_FILE = Path.home() / "steramest2data_file.txt"

OUTPUT_FILE = Path("ngefilm.json")
USER_DATA_IFRAME = "/tmp/ngefilm_iframe_profile"
os.makedirs(USER_DATA_IFRAME, exist_ok=True)

# --- Load config ---
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

# ============================================================
# Ambil daftar film
# ============================================================
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
        print("🔎 Scraping:", url)

        try:
            r = requests.get(url, headers=headers, timeout=20)
            r.raise_for_status()
        except:
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
                "detail": detail,
                "year": ""
            })

        print("➕ Total sementara:", len(all_results))

    print("\n🎉 TOTAL FINAL:", len(all_results), "\n")
    return all_results

# ============================================================
# Tambah entry JSON
# ============================================================
def add_json_entry(data_list, item, iframe):
    data_list.append({
        "title": item["title"],
        "slug": item["slug"],
        "poster": item["poster"],
        "year": item["year"],
        "detail": item["detail"],
        "iframe": iframe,
        "user_agent": "Mozilla/5.0"
    })

# ============================================================
# Playwright – ambil iframe
# ============================================================
async def process_item(item):
    slug = item["slug"]

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
                "--no-sandbox",
                "--window-size=1280,720",
            ]
        )

        context = await browser.new_context()
        page = await context.new_page()
        iframe = None

        for player in range(1, 6):
            urlp = f"{BASE_URL}/{slug}/?player={player}"
            try:
                await page.goto(urlp, timeout=0)
                await page.wait_for_timeout(2500)
            except:
                continue

            frames = await page.query_selector_all("iframe")
            for fr in frames:
                src = await fr.get_attribute("src")
                if src and any(d in src.lower() for d in UNIVERSAL_DOMAINS):
                    iframe = src
                    break

            if iframe:
                break

        await browser.close()
        return (item, iframe)

# ============================================================
# RUN ALL + SIMPAN JSON
# ============================================================
async def run_all():
    items = get_items()
    result_json = []

    tasks = [process_item(item) for item in items]
    for coro in asyncio.as_completed(tasks):
        item, iframe = await coro

        if not iframe:
            print(f"❌ {item['slug']} -> iframe TIDAK ditemukan")
            continue

        print(f"✅ {item['slug']} -> OK")

        add_json_entry(result_json, item, iframe)

    # simpan JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result_json, f, indent=4, ensure_ascii=False)

    print("\n📦 JSON berhasil disimpan:", OUTPUT_FILE)


if __name__ == "__main__":
    asyncio.run(run_all())
