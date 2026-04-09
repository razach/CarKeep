import json
from pathlib import Path
from datetime import datetime

def update_inventory():
    project_root = Path(__file__).resolve().parent.parent.parent
    data_dir = project_root / 'Module2_Prospecting' / 'data'
    
    raw_file = data_dir / 'raw_scrape.json'
    db_file = data_dir / 'prospects_db.json'
    
    # Load today's raw scrape
    if not raw_file.exists():
        print(f"Error: {raw_file} not found. Run scraper first.")
        return
        
    with open(raw_file, 'r') as f:
        daily_scrape = json.load(f)
        
    print(f"Loaded {len(daily_scrape)} vehicles from daily scrape.")
    
    # Load existing or initialize new database
    if db_file.exists():
        try:
            with open(db_file, 'r') as f:
                db_data = json.load(f)
                prospects = db_data.get('prospects', {})
        except json.JSONDecodeError:
            print("Warning: existing DB is corrupt. Starting fresh.")
            prospects = {}
    else:
        prospects = {}
        
    today = datetime.now().strftime("%Y-%m-%d")
    scraped_vins = set()
    
    new_cars = 0
    price_drops = 0
    
    # Process scraped cars
    for car in daily_scrape:
        vin = car['vin']
        scraped_vins.add(vin)
        current_price = car['price']
        
        # New vehicle found!
        if vin not in prospects:
            car['first_seen'] = today
            car['last_seen'] = today
            car['status'] = 'active'
            car['original_price'] = current_price
            car['price_history'] = [{"date": today, "price": current_price}]
            prospects[vin] = car
            new_cars += 1
            print(f"[NEW] Added {vin}: ${current_price} ({car['dealer']})")
            
        # Existing vehicle update!
        else:
            old_car = prospects[vin]
            old_car['last_seen'] = today
            old_car['status'] = 'active'
            
            # Check for price changes
            if current_price != old_car['price']:
                diff = current_price - old_car['price']
                if diff < 0:
                    print(f"[PRICE DROP] {vin} dropped from ${old_car['price']} to ${current_price} ({-diff} drop)")
                    price_drops += 1
                else:
                    print(f"[PRICE INCREASE] {vin} increased from ${old_car['price']} to ${current_price}")
                
                old_car['price'] = current_price
                
                # Append to history if it's a new day
                if old_car['price_history'][-1]['date'] == today:
                    old_car['price_history'][-1]['price'] = current_price
                else:
                    old_car['price_history'].append({"date": today, "price": current_price})
                
            # Keep other attributes fresh
            old_car['miles'] = car['miles']
            old_car['url'] = car['url']
            old_car['raw_text'] = car['raw_text']

    # Mark cars that disappeared as sold/removed
    removed_cars = 0
    for vin, car_data in prospects.items():
        if vin not in scraped_vins and car_data['status'] == 'active':
            car_data['status'] = 'sold_or_removed'
            # We DONT update last_seen, so we know exactly when it disappeared
            removed_cars += 1
            print(f"[REMOVED] {vin} is no longer listed. Last seen {car_data['last_seen']}.")
            
    # Save the database
    output_db = {
        "_description": "Automated inventory database tracking all previously and currently scraped prospects.",
        "last_updated": datetime.now().isoformat(),
        "stats": {
            "total_tracked": len(prospects),
            "active_listings": len([c for c in prospects.values() if c['status'] == 'active']),
            "sold_or_removed": len([c for c in prospects.values() if c['status'] == 'sold_or_removed'])
        },
        "prospects": prospects
    }
    
    with open(db_file, 'w') as f:
        json.dump(output_db, f, indent=2)
        
    print("\n--- INVENTORY UPDATE COMPLETE ---")
    print(f"Total Scraped: {len(scraped_vins)}")
    print(f"New Cars Added: {new_cars}")
    print(f"Price Changes: {price_drops}")
    print(f"Cars Removed: {removed_cars}")
    print(f"DB Total: {output_db['stats']['total_tracked']} ({output_db['stats']['active_listings']} active)")
    print(f"Saved to {db_file.name}")

if __name__ == "__main__":
    update_inventory()
