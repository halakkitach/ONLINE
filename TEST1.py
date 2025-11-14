import asyncio
import json
from playwright.async_api import async_playwright

TARGET_URL = "https://embednow.top/embed/wc/---"
OUTPUT_FILE = "map7.json"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=False,
            args=[
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

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)

        m3u8 = None

        def on_request(req):
            nonlocal m3u8
            if ".m3u8" in req.url:
                print("🔥 FOUND M3U8:", req.url)
                m3u8 = req.url

        page.on("request", on_request)

        await page.goto(TARGET_URL, timeout=0)

        for _ in range(40):
            if m3u8:
                break
            await asyncio.sleep(0.5)

        await browser.close()

    with open(OUTPUT_FILE, "w") as f:
        json.dump({TARGET_URL: m3u8}, f, indent=2)

asyncio.run(run())
