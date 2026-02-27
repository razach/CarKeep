import sys
import os

# Add Model directory to path so we can import the analyzer
sys.path.append(os.path.join(os.path.dirname(__file__), 'Model'))
from configuration_analyzer import BMWConfigAnalyzer

def main():
    # Define the configuration for the 2024 BMW iX from Fairfax
    fairfax_config = {
        "name": "2024 BMW iX xDrive50 (Fairfax Stock #BRCN25677)",
        "year": 2024,
        "model": "iX",
        "suspension": "Coil Springs", # We know 50s standard is coil unless explicitly optioned with 2-axle air
        "wheels": "21-inch Aero Dark Black wheels",
        "exterior_color": "Black Sapphire Metallic",
        "interior_color": "Mocha",
        "interior_material": "Perforated SensaTec",
        "packages": [
            "Driving Assistance Pro Package ($2,300)",
            "Premium Package ($3,700)",
            "Sport Package ($2,500)",
            "Luxury Package ($1,150)"
        ]
    }

    # Initialize the analyzer
    analyzer = BMWConfigAnalyzer(fairfax_config)
    
    # Generate the report
    report_markdown = analyzer.analyze()
    
    # Save the report
    output_path = os.path.join(os.path.dirname(__file__), 'Actuals', '2024_BMW_iX_Fairfax_Config_Analysis.md')
    with open(output_path, 'w') as f:
        f.write(report_markdown)
        
    print(f"Configuration analysis report successfully generated and saved to: {output_path}")

if __name__ == "__main__":
    main()
