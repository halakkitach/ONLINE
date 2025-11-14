import asyncio
import os
import sys
import json
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

TARGET_URL = "https://embednow.top/embed/wc/2025-11-14/lux-ger"
OUTPUT_FILE = "map7.json"

IN_GITHUB = os.getenv("GITHUB_ACTIONS") == "true"


def detect_browser():
    if IN_GITHUB:
        return None

    if sys.platform.startswith("win"):
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            shutil.which("chrome"),
            shutil.which("chromium"),
        ]
    else:
        candidates = [
            shutil.which("google-chrome"),
            shutil.which("google-chrome-stable"),
            shutil.which("chrome"),
            shutil.which("chromium"),
            shutil.which("chromium-browser"),
        ]

    for c in candidates:
        if c:
            return c

    return None


async def run():
    chrome_path = detect_browser()
    m3u8_list = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=chrome_path,
            headless=True if IN_GITHUB else False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--no-sandbox",
                "--disable-infobars",
                "--window-size=1280,720",
            ]
        )

        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        page = await context.new_page()

        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US','en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4] });
        """)

        def on_request(req):
            url = req.url
            if ".m3u8" in url:
                print("🔥 M3U8 FOUND:", url)
                m3u8_list.append(url)

        page.on("request", on_request)

        print("🌐 Opening:", TARGET_URL)
        await page.goto(TARGET_URL, timeout=0)

        # wait 10 seconds
        for _ in range(20):
            await asyncio.sleep(0.5)
            if m3u8_list:
                break

        await browser.close()

    # Write JSON
    if m3u8_list:
        final_url = m3u8_list[0]
    else:
        final_url = None

    data = {TARGET_URL: final_url}

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"📁 Saved to {OUTPUT_FILE}")
    print(json.dumps(data, indent=2))


asyncio.run(run())
