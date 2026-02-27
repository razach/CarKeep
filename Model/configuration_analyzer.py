class BMWConfigAnalyzer:
    """Analyzes a BMW iX configuration for rarity, desirability, and maintenance."""

    def __init__(self, config: dict):
        self.config = config
        self.report = []

    def analyze(self) -> str:
        self.report.append(f"# Configuration Analysis: {self.config.get('name', 'BMW iX')}\n")
        self.report.append("This report evaluates the rarity, desirability, and maintenance implications of the specific vehicle configuration based on community consensus and historical data.\n")

        self._analyze_model_year()
        self._analyze_suspension()
        self._analyze_wheels()
        self._analyze_exterior()
        self._analyze_interior()
        self._analyze_packages()

        return "\n".join(self.report)

    def _analyze_model_year(self):
        year = self.config.get("year")
        model = self.config.get("model")
        
        self.report.append("## 1. Model Year & Core Hardware")
        if year >= 2024 and model == "iX":
            self.report.append("✅ **Highly Desirable:** This is a Model Year 2024+ vehicle. It features the upgraded Head Unit High 5 (MGU5) hardware. This is a critical upgrade as it enables the newer, much faster **iDrive 8.5** operating system and the enhanced **Highway Assistant** (allowing hands-free driving up to 85mph). Older models (2022-2023) lack the processing power for these features.")
        else:
            self.report.append("⚠️ **Older Hardware:** This vehicle predates the March 2023 hardware update. It runs iDrive 8.0 and does not support the advanced hands-free Highway Assistant.")
        self.report.append("")

    def _analyze_suspension(self):
        suspension = self.config.get("suspension", "").lower()
        self.report.append("## 2. Suspension System")
        if "air" in suspension:
            self.report.append("☁️ **Air Suspension:** Known for providing a 'cloud-like' ride, heavily mitigating the harshness of larger wheels or rough roads. However, **Reliability Warning:** Air suspension is complex and historically prone to expensive failures outside of warranty (compressors, airbags).")
        else:
            self.report.append("🛡️ **Coil Springs:** Known to be virtually 'bulletproof' in terms of reliability and significantly cheaper to maintain long-term. While the ride is firmer and less isolating than air suspension, it is the overwhelmingly safer choice for out-of-warranty ownership.")
        self.report.append("")

    def _analyze_wheels(self):
        wheels = self.config.get("wheels", "")
        self.report.append("## 3. Wheel & Tire Selection")
        if "20" in wheels:
            self.report.append("🏆 **20-inch Wheels:** The absolute best choice for ride comfort and sidewall durability. The thickest tire sidewall offers maximum protection against potholes, bent rims, and blowouts. Also generally the cheapest tires to replace.")
        elif "21" in wheels:
            self.report.append("⚖️ **21-inch Wheels (The 'Goldilocks' Choice):** A very common and balanced option. Offers a noticeable aesthetic improvement over the 20s while retaining enough tire sidewall to absorb moderate road impacts without the harshness or extreme fragility of the 22s.")
        elif "22" in wheels:
            self.report.append("🚨 **22-inch Wheels:** Prioritizes aesthetics and handling over comfort. The low-profile rubber results in a noticeably harsher ride, especially on coil springs. Highly susceptible to sidewall bubbling, flats, and cracked rims from potholes. Tires are expensive and wear out quickly.")
        else:
            self.report.append("Unknown wheel size configured.")
        self.report.append("")

    def _analyze_exterior(self):
        color = self.config.get("exterior_color", "").lower()
        self.report.append("## 4. Exterior Paint")
        self.report.append(f"**Color:** {self.config.get('exterior_color')}")
        if "black" in color or "sapphire" in color:
            self.report.append("⚠️ **Black/Dark Metallic Paint:** Black Sapphire Metallic is a classic, highly sought-after, and beautiful color. However, dark metallics are notoriously difficult to maintain. They highlight swirl marks, dust, and specifically **rock chips** on the front fascia more than any other color.")
            self.report.append("*   **Recommendation:** High priority for Paint Protection Film (PPF) on at least the front bumper and hood to prevent chipping if doing extensive highway driving.")
        else:
            self.report.append("Lighter or non-black colors generally hide swirl marks, dust, and rock chips much better, requiring less obsessive maintenance.")
        self.report.append("")

    def _analyze_interior(self):
        color = self.config.get("interior_color", "").lower()
        material = self.config.get("interior_material", "").lower()
        
        self.report.append("## 5. Interior Comfort & Durability")
        
        material_notes = "Unknown material."
        if "sensatec" in material or "sensafin" in material:
             material_notes = "🛡️ **SensaTec (Faux Leather):** Modern BMW SensaTec is exceptionally durable. Many owners prefer it over base leather because it resists creasing, doesn't stretch out, and is incredibly easy to wipe clean. It generally holds up looking 'newer' for much longer than genuine leather."
        elif "leather" in material:
             material_notes = "🐄 **Genuine Leather:** Offers a premium smell and slightly softer feel initially, but requires regular conditioning. Prone to stretching, wear marks on the bolsters, and creasing over time."
             
        color_notes = ""
        if "mocha" in color or "dark" in color or "black" in color:
             color_notes = "✅ **Dark Color (Mocha/Black):** Highly practical. Mocha in particular is considered a premium, rich color that perfectly hides blue jean dye transfer, dirt, and general staining that plagues lighter interiors like Oyster."
             
        self.report.append(f"**Upholstery:** {self.config.get('interior_color')} {self.config.get('interior_material')}")
        self.report.append(material_notes)
        if color_notes:
            self.report.append(color_notes)
        self.report.append("")

    def _analyze_packages(self):
        packages = self.config.get("packages", [])
        self.report.append("## 6. Feature Packages")
        
        has_dapp = any("driving assistance" in p.lower() for p in packages)
        has_premium = any("premium" in p.lower() for p in packages)
        has_luxury = any("luxury" in p.lower() for p in packages)
        
        if has_dapp:
             self.report.append("🌟 **Driving Assistance Professional Package:** Essential. Highly desirable for resale and daily use. Fully unlocks the Highway Assistant capabilities of the 2024 model.")
        if has_premium:
             self.report.append("🌟 **Premium Package:** Very common, almost an expected standard. The HUD, upgraded Harman Kardon audio, and 360-degree cameras are critical creature comforts.")
        if has_luxury:
             self.report.append("💎 **Luxury Package:** A rare and premium touch. The crystal controls and open-pore wood add significant tactile luxury to the cabin, while soft-close doors elevate the experience.")
             
        self.report.append("\n**All Listed Packages:**")
        for pkg in packages:
             self.report.append(f"*   {pkg}")
        self.report.append("")
