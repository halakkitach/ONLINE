import asyncio
import json
import os
import sys
import shutil
from playwright.async_api import async_playwright

TARGET_URL = "https://embednow.top/embed/wc/2025-11-14/lux-ger"
OUTPUT_FILE = "map7.json"

IN_GITHUB = os.getenv("GITHUB_ACTIONS") == "true"

def detect_browser():
    if IN_GITHUB:
        return None
    if sys.platform.startswith("win"):
        candidates = [
            r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            shutil.which("chrome"),
            shutil.which("chromium"),
        ]
    else:
        candidates = [
            shutil.which("google-chrome"),
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
    print(f"Using browser: {chrome_path or 'Playwright Chromium'}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=chrome_path,
            headless=False,        # NON HEADLESS because Xvfb
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-infobars",
                "--no-sandbox",
                "--window-size=1280,720",
            ]
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US']});
            WebGLRenderingContext.prototype.getParameter = function() { 
                return "Intel Open Source Technology Center";
            };
        """)

        m3u8_list = []

        def on_request(req):
            url = req.url
            if ".m3u8" in url:
                print("🔥 M3U8 FOUND:", url)
                m3u8_list.append(url)

        page.on("request", on_request)

        print("Opening:", TARGET_URL)
        await page.goto(TARGET_URL, timeout=0)

        # wait 15 seconds (embednow lambat)
        for _ in range(30):
            await asyncio.sleep(0.5)
            if m3u8_list:
                break

        await browser.close()

    found = m3u8_list[0] if m3u8_list else None

    with open(OUTPUT_FILE, "w") as f:
        json.dump({TARGET_URL: found}, f, indent=2)

    print("Saved to map7.json:")
    print(json.dumps({TARGET_URL: found}, indent=2))


asyncio.run(run())
