from dotenv import load_dotenv
load_dotenv()
import asyncio
from playwright.async_api import async_playwright
import re
import os
import sys

BASE_URL = os.getenv("BASE_URL")
if not BASE_URL:
    print("❌ BASE_URL tidak ditemukan di environment variable.")
    sys.exit(1)

async def get_oembed_json_url(page):
    await page.goto(f"{BASE_URL}/index.html", timeout=60000)
    await page.wait_for_timeout(2000)
    link = await page.query_selector('link[rel="alternate"][type="application/json+oembed"]')
    if link:
        href = await link.get_attribute("href")
        if href:
            return BASE_URL + "/" + href
    return None

async def fetch_player_html_from_oembed(page, json_url):
    response = await page.request.get(json_url)
    if response.status != 200:
        return None
    data = await response.json()
    if "html" in data and 'src="' in data["html"]:
        start = data["html"].find('src="') + 5
        end = data["html"].find('"', start)
        return data["html"][start:end]
    return None

async def extract_m3u8_from_player(page, player_url):
    m3u8_urls = set()
    match = re.search(r"/([a-f0-9\-]{36})\.html", player_url)
    if not match:
        print("❌ Gagal ekstrak UUID dari player URL.")
        return []

    uuid = match.group(1)
    config_js_url = f"{BASE_URL}/channels/{uuid}/config.js"
    print(f"📦 Ambil config.js: {config_js_url}")
    response = await page.request.get(config_js_url)
    if response.status != 200:
        print(f"❌ Gagal ambil config.js: status {response.status}")
        return []

    config_text = await response.text()
    match = re.search(r'"source"\s*:\s*"([^"]+\.m3u8)"', config_text)
    if match:
        relative_path = match.group(1)
        m3u8_url = f"{BASE_URL}/{relative_path}"
        print("📡 M3U8 ditemukan:", m3u8_url)
        m3u8_urls.add(m3u8_url)
    else:
        print("⚠️ Tidak ditemukan .m3u8 dalam config.js.")

    return list(m3u8_urls)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("🔍 Mencari oEmbed JSON...")
        oembed_url = await get_oembed_json_url(page)
        if not oembed_url:
            print("❌ Tidak ditemukan oEmbed URL.")
            return

        print(f"✅ oEmbed URL: {oembed_url}")
        player_url = await fetch_player_html_from_oembed(page, oembed_url)
        if not player_url:
            print("❌ Tidak bisa ambil player HTML.")
            return

        print(f"🎥 Player URL: {player_url}")
        m3u8_links = await extract_m3u8_from_player(page, player_url)
        await browser.close()

        if m3u8_links:
            print("✅ M3U8 berhasil diambil:", m3u8_links[0])
            with open("RRILIVE.m3u8", "w") as f:
                f.write(m3u8_links[0] + "\n")
            print("💾 Disimpan ke RRILIVE.m3u8")
        else:
            print("⚠️ Tidak ditemukan M3U8.")

if __name__ == "__main__":
    asyncio.run(main())
