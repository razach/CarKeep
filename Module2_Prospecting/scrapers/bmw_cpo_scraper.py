import sys
import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# Setup output dir
project_root = Path(__file__).parent.parent.parent
data_dir = project_root / 'Module2_Prospecting' / 'data'
data_dir.mkdir(parents=True, exist_ok=True)
output_file = data_dir / 'raw_scrape.json'

URL = "https://www.bmwusa.com/certified-preowned-search/results?ZipCode=22015&Radius=100&Type=CPO&Series=iX&Year=2024%7C2025%7C2026&Price=$40,000+-+$49,999|$50,000+-+$59,999"
MAX_PRICE = 55000

scraped_vehicles = []
seen_vins = set()

async def handle_response(response):
    # Print a trace of JSON endpoints for discovery
    if "json" in response.url or "api" in response.url or "graphql" in response.url or "vehicle" in response.url or "inventory" in response.url:
        print(f"API Trace: {response.url}")
        
    # Intercept the specific API. We check for 'vehicle' or 'inventory' in the url just in case
    if "inventoryservices" in response.url or "graphql" in response.url:
        try:
            # Try to parse the API JSON
            data = await response.json()
            # BMW API usually returns { "results": [...] } or similar
            # Let's handle both "results" and direct array to be safe
            vehicles = []
            if isinstance(data, dict):
                if "results" in data:
                    vehicles = data["results"]
                elif "vehicles" in data:
                    vehicles = data["vehicles"]
                elif "data" in data and "results" in data["data"]:
                    vehicles = data["data"]["results"]
            elif isinstance(data, list):
                vehicles = data
                
            if vehicles:
                print(f"Captured {len(vehicles)} vehicles in this payload from {response.url}")
                for vehicle in vehicles:
                    # Get VIN to avoid duplicates from multiple API calls
                    vin = vehicle.get("vin", "Unknown")
                    if vin in seen_vins:
                        continue
                        
                    # basic safety for price/cpo
                    # price could be nested or string
                    price_val = vehicle.get("price", vehicle.get("internetPrice", vehicle.get("sellingPrice", 999999)))
                    # try convert to int if it's string
                    if isinstance(price_val, str):
                        price_val = int(price_val.replace("$","").replace(",","").split(".")[0])
                    
                    # cpo could be boolean or string
                    cpo_status = vehicle.get("certified", vehicle.get("cpo", False))
                    is_cpo = str(cpo_status).lower() in ["true", "1", "yes"]
                    
                    if price_val <= MAX_PRICE and is_cpo:
                        scraped_vehicles.append(vehicle)
                        seen_vins.add(vin)
        except Exception as e:
            # We silently ignore non-json responses or parsing errors for unrelated URLs
            pass

async def run_scraper():
    print(f"Starting scraper. Targeted zip 22015, radius 100mi, max price ${MAX_PRICE}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        
        # Listen for API responses
        page.on("response", handle_response)
        
        print(f"Navigating to: {URL}")
        # Use wait_until="load" to avoid timeout if networkidle never fires due to tracking scripts
        await page.goto(URL, wait_until="load")
        
        # Wait a chunk of time for React/SPA to load initial API data
        print("Waiting for page and initial APIs to settle...")
        await page.wait_for_timeout(8000)
        await page.screenshot(path="debug_start.png")
            
        # Try interacting with zip code if it's there
        try:
            print("Looking for generic zip code inputs...")
            inputs = await page.locator("input[name*='zip'], input[id*='zip'], input[placeholder*='ZIP']").all()
            for inp in inputs:
                if await inp.is_visible():
                    print("Found ZIP input, filling 22015...")
                    await inp.fill("22015")
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(3000)
                    
                    # Also need to select a dealer!
                    select_btns = await page.locator("button:has-text('Select')").all()
                    for btn in select_btns:
                        if await btn.is_visible():
                            print("Selecting dealer...")
                            await btn.click()
                            await page.wait_for_timeout(5000)
                            break
                    print("Waiting 10 seconds for Firestore data to load...")
                    await page.wait_for_timeout(10000)
                    
                    print("Extracting vehicle cards via JS evaluate...")
                    
                    # Since Shadow DOMs or complex nesting might be hiding text from simple locators, 
                    # we will evaluate a script that walks the DOM and finds all blocks containing money and miles.
                    # As a brute-force approach for Phase 1, we just return the full inner text of elements matching vehicle card patterns.
                    
                    cards_data = await page.evaluate('''() => {
                        let elements = Array.from(document.querySelectorAll('*'));
                        let cards = [];
                        
                        elements.forEach(el => {
                            let text = el.innerText;
                            if (text && text.includes('DEALER PRICE') && text.includes('MILES')) {
                                // Only push elements that seem to be the direct container (not the body or app root)
                                if (text.length < 500) {
                                    let href = "";
                                    if (el.tagName === 'A') {
                                        href = el.href;
                                    } else {
                                        let a = el.querySelector('a');
                                        if (a) href = a.href;
                                    }
                                    
                                    cards.push({
                                        url: href || "",
                                        text: text
                                    });
                                }
                            }
                        });
                        return cards;
                    }''')
                    
                    print(f"Found {len(cards_data)} potential vehicle containers via JS evaluation.")
                    
                    seen_vins = set()
                    
                    for raw in cards_data:
                        text = raw['text']
                        href = raw['url']
                        vin = href.split("/")[-1] if href else "Unknown"
                        
                        if vin in seen_vins or 'BMW' not in text:
                            continue
                        seen_vins.add(vin)
                        
                        lines = [L.strip() for L in text.split('\n') if L.strip() and L.strip() != 'Contact Dealer for Images']
                        
                        price = 999999
                        miles = 0
                        year_make_model = ""
                        trim = ""
                        dealer = ""
                        
                        for line in lines:
                            clean_line = line.replace(",", "").strip()
                            if not year_make_model and "BMW iX" in line:
                                year_make_model = line
                            elif not trim and "xDrive" in line or "M60" in line:
                                trim = line
                            elif line.startswith("$"):
                                try: price = int(clean_line.replace("$", ""))
                                except: pass
                            elif clean_line.isdigit() and len(clean_line) > 2:
                                # Likely mileage if it's just a number
                                miles = int(clean_line)
                            elif "BMW of" in line or ("BMW" in line and "-" in line):
                                dealer = line.split("-")[0].strip()
                        
                        if price <= MAX_PRICE:
                            scraped_vehicles.append({
                                "vin": vin,
                                "year_make_model": year_make_model,
                                "trim": trim,
                                "price": price,
                                "miles": miles,
                                "dealer": dealer,
                                "url": href,
                                "raw_text": text
                            })
                    break
        except Exception as e:
            print(f"Zip handler failed: {e}")

        await browser.close()
        
    print(f"\nScraping complete. Found {len(scraped_vehicles)} CPO iX's under $55k!")
    print(f"Saving to {output_file}...")
    
    with open(output_file, 'w') as f:
        json.dump(scraped_vehicles, f, indent=2)

if __name__ == "__main__":
    asyncio.run(run_scraper())
