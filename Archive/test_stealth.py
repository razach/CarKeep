import asyncio
from playwright.async_api import async_playwright
try:
    from playwright_stealth import Stealth
except ImportError:
    from playwright_stealth.stealth import Stealth

async def test():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        p = await b.new_page()
        await Stealth().apply_stealth_async(p)
        print("Success")
asyncio.run(test())
