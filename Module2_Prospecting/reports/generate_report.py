import json
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def generate_report():
    project_root = Path(__file__).resolve().parent.parent.parent
    data_dir = project_root / 'Module2_Prospecting' / 'data'
    reports_dir = project_root / 'Module2_Prospecting' / 'reports'
    
    # Ensure reports dir exists
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    db_file = data_dir / 'prospects_db.json'
    
    if not db_file.exists():
        print(f"Error: {db_file} not found. Cannot generate report.")
        return
        
    with open(db_file, 'r') as f:
        db_data = json.load(f)
        
    prospects = db_data.get('prospects', {})
    
    # Filter only active listings
    active_cars = [car for car in prospects.values() if car.get('status') == 'active']
    
    if not active_cars:
        print("No active cars found. Skipping report generation.")
        return
        
    # Create DataFrame
    df = pd.DataFrame(active_cars)
    
    # Ensure numerics
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['miles'] = pd.to_numeric(df['miles'], errors='coerce')
    df = df.dropna(subset=['price', 'miles'])
    
    # ---- 1. Generate Scatter Plot with Trendline ----
    
    plt.figure(figsize=(12, 8))
    sns.set_theme(style="whitegrid")
    
    # Plot scatter
    ax = sns.scatterplot(
        data=df, 
        x="miles", 
        y="price", 
        hue="trim", 
        palette="viridis", 
        s=100, 
        alpha=0.8,
        edgecolor="w"
    )
    
    # Calculate trendline (degrees=1 for linear)
    z = np.polyfit(df['miles'], df['price'], 1)
    p = np.poly1d(z)
    
    # Plot trendline
    x_trend = np.linspace(df['miles'].min(), df['miles'].max(), 100)
    plt.plot(x_trend, p(x_trend), "r--", alpha=0.5, label="Market Average Trend")
    
    # Calculate "Value Score" (distance below trendline)
    # Negative value means it's cheaper than expected (good)
    df['expected_price'] = p(df['miles'])
    df['discount_to_trend'] = df['expected_price'] - df['price']
    
    # Annotate the top 5 deals (highest discount to trend)
    top_deals = df.sort_values(by='discount_to_trend', ascending=False).head(5)
    
    for _, row in top_deals.iterrows():
        plt.annotate(
            f"{row['dealer']}\n${row['price']:,.0f}",
            (row['miles'], row['price']),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=9,
            weight='bold'
        )
        
    plt.title("BMW iX CPO Relative Market Value", fontsize=16, pad=15)
    plt.xlabel("Mileage", fontsize=12)
    plt.ylabel("Price ($)", fontsize=12)
    
    # Format axes
    ax.yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    ax.xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    
    # Save plot
    plot_path = reports_dir / 'value_matrix.png'
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300)
    plt.close()
    
    # ---- 2. Generate Markdown Report ----
    
    today = datetime.now().strftime("%B %d, %Y")
    
    md_content = f"""# BMW iX Prospecting Report
*Generated on {today}*

This report analyzes the active CPO market for BMW iX models within 100 miles of 22015 under $55,000.  
Total Active Prospects Tracked: **{len(df)}**

## Relative Market Value Matrix
The chart below maps Price vs. Mileage. The red dashed line represents the average market depreciation trend.
**Vehicles plotted below the red line represent higher relative value.**

![Value Matrix](./value_matrix.png)

## Top 5 Best Value Opportunities
These vehicles are priced the furthest below the expected market average for their mileage.

"""
    
    for idx, row in top_deals.iterrows():
        md_content += f"### {row['year_make_model']} {row['trim']} - {row['dealer']}\n"
        md_content += f"- **Price:** ${row['price']:,.0f} *(Est. ${row['discount_to_trend']:,.0f} below market average)*\n"
        md_content += f"- **Mileage:** {row['miles']:,} miles\n"
        md_content += f"- **First Seen:** {row.get('first_seen', 'Unknown')}\n"
        md_content += f"- [View Vehicle Listing]({row['url']})\n\n"
        
    report_path = reports_dir / 'daily_summary.md'
    with open(report_path, 'w') as f:
        f.write(md_content)
        
    print(f"Report generated successfully: {report_path}")
    print(f"Plot saved: {plot_path}")

if __name__ == "__main__":
    generate_report()
