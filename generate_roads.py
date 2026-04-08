"""
SafeWalk — Delhi Road Network Generator (Production Quality)
Uses OSRM to trace the EXACT physical geometry of real Delhi roads.
Each road is defined by real waypoints, and OSRM returns the precise
turn-by-turn road-following path between them.
"""
import json
import random
import os
import sys
import time
import urllib.request

OSRM_BASE = "https://router.project-osrm.org/route/v1/driving"

def osrm_trace(waypoints):
    """Given a list of [lat, lng] waypoints, ask OSRM to return the exact road geometry."""
    coords_str = ";".join([f"{wp[1]},{wp[0]}" for wp in waypoints])
    url = f"{OSRM_BASE}/{coords_str}?geometries=geojson&overview=full"
    
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SafeWalk/2.0'})
            with urllib.request.urlopen(req, timeout=10) as res:
                data = json.loads(res.read())
            if data.get('routes') and data['routes'][0]['geometry']['coordinates']:
                return data['routes'][0]['geometry']['coordinates']
        except Exception as e:
            if attempt < 2:
                time.sleep(1)
            else:
                print(f"  OSRM failed after 3 attempts: {e}")
    return None

def get_delhi_roads():
    """
    Define every major Delhi road by its real-world waypoints.
    OSRM will trace the exact path of the road between these points.
    Waypoints are [lat, lng] pairs at actual locations ON the road.
    """
    roads = [
        # ═══════════════════ RING ROAD (split into segments) ═══════════════════
        {"name": "Ring Road (Ashram-Lajpat)", "waypoints": [[28.5695, 77.2585], [28.5720, 77.2430]], "score": (55, 75)},
        {"name": "Ring Road (Lajpat-AIIMS)", "waypoints": [[28.5720, 77.2430], [28.5685, 77.2280], [28.5668, 77.2100]], "score": (60, 80)},
        {"name": "Ring Road (AIIMS-Dhaula Kuan)", "waypoints": [[28.5668, 77.2100], [28.5730, 77.1940], [28.5870, 77.1680]], "score": (65, 80)},
        {"name": "Ring Road (Dhaula Kuan-Punjabi Bagh)", "waypoints": [[28.5870, 77.1680], [28.6180, 77.1520], [28.6500, 77.1340]], "score": (55, 70)},
        {"name": "Ring Road (Punjabi Bagh-Wazirpur)", "waypoints": [[28.6500, 77.1340], [28.6700, 77.1520], [28.6890, 77.1730]], "score": (50, 70)},
        {"name": "Ring Road (Wazirpur-ISBT)", "waypoints": [[28.6890, 77.1730], [28.6800, 77.2050], [28.6670, 77.2280]], "score": (45, 65)},
        {"name": "Ring Road (ISBT-IP Flyover)", "waypoints": [[28.6670, 77.2280], [28.6430, 77.2430], [28.6280, 77.2490]], "score": (50, 70)},
        {"name": "Ring Road (IP-Sarai Kale Khan)", "waypoints": [[28.6280, 77.2490], [28.6050, 77.2620], [28.5850, 77.2690]], "score": (55, 70)},
        {"name": "Ring Road (Sarai Kale Khan-Ashram)", "waypoints": [[28.5850, 77.2690], [28.5760, 77.2640], [28.5695, 77.2585]], "score": (50, 65)},
        
        # ═══════════════════ OUTER RING ROAD ═══════════════════
        {"name": "Outer Ring (Vikaspuri-Mangolpuri)", "waypoints": [[28.6380, 77.0680], [28.6600, 77.0720], [28.6920, 77.0840]], "score": (40, 60)},
        {"name": "Outer Ring (Mangolpuri-Wazirpur)", "waypoints": [[28.6920, 77.0840], [28.6960, 77.1200], [28.6890, 77.1730]], "score": (45, 65)},
        {"name": "Outer Ring (Jahangirpuri-GT Road)", "waypoints": [[28.7250, 77.1700], [28.7100, 77.2000], [28.6950, 77.2300]], "score": (35, 55)},
        
        # ═══════════════════ NH-44 (GT ROAD) ═══════════════════
        {"name": "NH-44 (Kashmere Gate-Model Town)", "waypoints": [[28.6670, 77.2280], [28.6830, 77.2200], [28.7050, 77.1920]], "score": (40, 60)},
        {"name": "NH-44 (Model Town-Azadpur)", "waypoints": [[28.7050, 77.1920], [28.7140, 77.1830], [28.7250, 77.1700]], "score": (45, 65)},
        {"name": "NH-44 (Azadpur-Alipur)", "waypoints": [[28.7250, 77.1700], [28.7400, 77.1600], [28.7600, 77.1500]], "score": (35, 50)},
        
        # ═══════════════════ NH-48 (DELHI-GURGAON) ═══════════════════
        {"name": "NH-48 (Dhaula Kuan-Mahipalpur)", "waypoints": [[28.5870, 77.1680], [28.5700, 77.1400], [28.5530, 77.1150]], "score": (60, 75)},
        {"name": "NH-48 (Mahipalpur-Border)", "waypoints": [[28.5530, 77.1150], [28.5350, 77.0950], [28.5180, 77.0750]], "score": (55, 70)},
        
        # ═══════════════════ MATHURA ROAD ═══════════════════
        {"name": "Mathura Road (India Gate-Nizamuddin)", "waypoints": [[28.6130, 77.2340], [28.5960, 77.2480], [28.5850, 77.2590]], "score": (65, 80)},
        {"name": "Mathura Road (Nizamuddin-Badarpur)", "waypoints": [[28.5850, 77.2590], [28.5600, 77.2750], [28.5350, 77.2900]], "score": (45, 65)},
        
        # ═══════════════════ VIKAS MARG ═══════════════════
        {"name": "Vikas Marg (ITO-Laxmi Nagar)", "waypoints": [[28.6310, 77.2490], [28.6340, 77.2650], [28.6320, 77.2780]], "score": (45, 65)},
        {"name": "Vikas Marg (Laxmi Nagar-Anand Vihar)", "waypoints": [[28.6320, 77.2780], [28.6360, 77.2950], [28.6470, 77.3160]], "score": (40, 60)},
        
        # ═══════════════════ RAJPATH / KARTAVYA PATH ═══════════════════
        {"name": "Kartavya Path", "waypoints": [[28.6125, 77.2090], [28.6135, 77.2200], [28.6130, 77.2340]], "score": (90, 98)},
        
        # ═══════════════════ AUROBINDO MARG ═══════════════════
        {"name": "Sri Aurobindo Marg", "waypoints": [[28.5668, 77.2100], [28.5550, 77.1980], [28.5350, 77.1870], [28.5200, 77.1780]], "score": (70, 85)},
        
        # ═══════════════════ LODHI ROAD ═══════════════════
        {"name": "Lodhi Road", "waypoints": [[28.5910, 77.2200], [28.5860, 77.2350], [28.5830, 77.2460]], "score": (80, 95)},
        
        # ═══════════════════ ASHOKA ROAD / JANPATH ═══════════════════
        {"name": "Janpath", "waypoints": [[28.6310, 77.2180], [28.6250, 77.2190], [28.6130, 77.2200]], "score": (75, 90)},
        {"name": "Parliament Street", "waypoints": [[28.6280, 77.2090], [28.6200, 77.2100], [28.6125, 77.2090]], "score": (85, 95)},
        
        # ═══════════════════ CONNAUGHT PLACE ═══════════════════
        {"name": "Connaught Place Inner", "waypoints": [[28.6340, 77.2180], [28.6330, 77.2230], [28.6300, 77.2210], [28.6310, 77.2170], [28.6340, 77.2180]], "score": (75, 90)},
        
        # ═══════════════════ PUSA ROAD ═══════════════════
        {"name": "Pusa Road", "waypoints": [[28.6400, 77.1900], [28.6450, 77.1980], [28.6500, 77.2080]], "score": (50, 65)},
        
        # ═══════════════════ ROHTAK ROAD ═══════════════════
        {"name": "Rohtak Road", "waypoints": [[28.6590, 77.1550], [28.6550, 77.1300], [28.6530, 77.1050]], "score": (35, 55)},
        
        # ═══════════════════ DB GUPTA ROAD ═══════════════════
        {"name": "DB Gupta Road (Karol Bagh)", "waypoints": [[28.6480, 77.1900], [28.6520, 77.1990], [28.6550, 77.2100]], "score": (40, 60)},
        
        # ═══════════════════ GT KARNAL ROAD ═══════════════════
        {"name": "GT Karnal Road", "waypoints": [[28.6950, 77.2300], [28.7100, 77.2200], [28.7300, 77.2050], [28.7500, 77.1900]], "score": (30, 50)},
        
        # ═══════════════════ CHANDNI CHOWK ═══════════════════
        {"name": "Chandni Chowk Road", "waypoints": [[28.6560, 77.2300], [28.6560, 77.2350], [28.6555, 77.2420]], "score": (25, 45)},
        
        # ═══════════════════ MG ROAD ═══════════════════
        {"name": "MG Road", "waypoints": [[28.6130, 77.2340], [28.5980, 77.2280], [28.5850, 77.2190]], "score": (70, 85)},
        
        # ═══════════════════ BARAKHAMBA ROAD ═══════════════════
        {"name": "Barakhamba Road", "waypoints": [[28.6310, 77.2280], [28.6300, 77.2340], [28.6290, 77.2400]], "score": (65, 80)},
        
        # ═══════════════════ BAHADUR SHAH ZAFAR MARG ═══════════════════
        {"name": "BSZ Marg (ITO)", "waypoints": [[28.6310, 77.2490], [28.6360, 77.2450], [28.6420, 77.2400]], "score": (55, 70)},
        
        # ═══════════════════ NELSON MANDELA MARG ═══════════════════
        {"name": "Nelson Mandela Marg", "waypoints": [[28.5668, 77.2100], [28.5550, 77.1820], [28.5410, 77.1650]], "score": (80, 95)},
        
        # ═══════════════════ NAJAFGARH ROAD ═══════════════════
        {"name": "Najafgarh Road", "waypoints": [[28.6380, 77.1350], [28.6350, 77.1100], [28.6300, 77.0850]], "score": (35, 55)},
        
        # ═══════════════════ DWARKA ROADS ═══════════════════
        {"name": "Dwarka Expressway", "waypoints": [[28.5870, 77.0600], [28.5750, 77.0500], [28.5600, 77.0400]], "score": (65, 85)},
        {"name": "Dwarka Sector Road", "waypoints": [[28.5870, 77.0600], [28.5830, 77.0450], [28.5780, 77.0300]], "score": (60, 80)},
        
        # ═══════════════════ JANAKPURI ROADS ═══════════════════
        {"name": "Janakpuri District Centre Road", "waypoints": [[28.6200, 77.0800], [28.6230, 77.0900], [28.6260, 77.1000]], "score": (60, 75)},
        
        # ═══════════════════ SHAHDARA ROADS ═══════════════════
        {"name": "Shahdara Flyover", "waypoints": [[28.6670, 77.2900], [28.6750, 77.2950], [28.6830, 77.3000]], "score": (35, 50)},
        {"name": "GT Road (Shahdara)", "waypoints": [[28.6670, 77.2800], [28.6700, 77.2860], [28.6750, 77.2950]], "score": (30, 45)},
        
        # ═══════════════════ DND FLYWAY ═══════════════════
        {"name": "DND Flyway", "waypoints": [[28.5850, 77.2690], [28.5790, 77.2900], [28.5750, 77.3100]], "score": (65, 80)},
        
        # ═══════════════════ BARAPULLAH ═══════════════════
        {"name": "Barapullah Elevated Road", "waypoints": [[28.5790, 77.2350], [28.5770, 77.2500], [28.5750, 77.2650]], "score": (70, 85)},
        
        # ═══════════════════ DEFENCE COLONY / SOUTH EXT ═══════════════════
        {"name": "Defence Colony Flyover", "waypoints": [[28.5720, 77.2300], [28.5710, 77.2400], [28.5700, 77.2500]], "score": (80, 95)},
        {"name": "South Extension Road", "waypoints": [[28.5720, 77.2200], [28.5690, 77.2250], [28.5660, 77.2300]], "score": (75, 88)},
        
        # ═══════════════════ HAUZ KHAS / SAKET ═══════════════════
        {"name": "Hauz Khas Road", "waypoints": [[28.5500, 77.2000], [28.5450, 77.2050], [28.5400, 77.2100]], "score": (70, 85)},
        {"name": "Saket Road", "waypoints": [[28.5250, 77.2000], [28.5200, 77.2080], [28.5150, 77.2150]], "score": (70, 85)},
        
        # ═══════════════════ SAFDARJUNG / RACE COURSE ═══════════════════
        {"name": "Safdarjung Road", "waypoints": [[28.5900, 77.2140], [28.5830, 77.2050], [28.5770, 77.1960]], "score": (80, 95)},
        {"name": "Race Course Road", "waypoints": [[28.6020, 77.2010], [28.5970, 77.2080], [28.5910, 77.2140]], "score": (88, 98)},
        {"name": "Akbar Road", "waypoints": [[28.6125, 77.2090], [28.6070, 77.2050], [28.6020, 77.2010]], "score": (88, 98)},
        
        # ═══════════════════ ASHRAM / LAJPAT ═══════════════════
        {"name": "Ashram Chowk Road", "waypoints": [[28.5695, 77.2585], [28.5720, 77.2530], [28.5720, 77.2430]], "score": (40, 60)},
        {"name": "Lajpat Nagar Road", "waypoints": [[28.5680, 77.2380], [28.5700, 77.2430], [28.5720, 77.2500]], "score": (55, 70)},
        
        # ═══════════════════ PITAMPURA / ROHINI ═══════════════════
        {"name": "Pitampura Main Road", "waypoints": [[28.6980, 77.1350], [28.7020, 77.1400], [28.7060, 77.1500]], "score": (60, 78)},
        {"name": "Rohini Main Road", "waypoints": [[28.7200, 77.1100], [28.7250, 77.1200], [28.7300, 77.1350]], "score": (55, 72)},
        
        # ═══════════════════ SEELAMPUR / NE DELHI ═══════════════════
        {"name": "Seelampur Road", "waypoints": [[28.6650, 77.2650], [28.6700, 77.2700], [28.6750, 77.2750]], "score": (15, 35)},
        {"name": "Wazirabad Road", "waypoints": [[28.6800, 77.2400], [28.6900, 77.2450], [28.7000, 77.2500]], "score": (25, 42)},
        {"name": "Yamuna Vihar Road", "waypoints": [[28.7000, 77.2700], [28.7050, 77.2730], [28.7100, 77.2780]], "score": (30, 48)},
        
        # ═══════════════════ PAHARGANJ ═══════════════════
        {"name": "Paharganj Main Bazar", "waypoints": [[28.6430, 77.2100], [28.6450, 77.2130], [28.6460, 77.2170]], "score": (20, 38)},
        
        # ═══════════════════ UTTAM NAGAR ═══════════════════
        {"name": "Uttam Nagar Road", "waypoints": [[28.6200, 77.0550], [28.6220, 77.0620], [28.6250, 77.0700]], "score": (30, 48)},
        
        # ═══════════════════ VASANT KUNJ / VASANT VIHAR ═══════════════════
        {"name": "Vasant Kunj Road", "waypoints": [[28.5300, 77.1550], [28.5350, 77.1600], [28.5400, 77.1650]], "score": (75, 90)},
        {"name": "Vasant Vihar Road", "waypoints": [[28.5600, 77.1600], [28.5630, 77.1650], [28.5670, 77.1700]], "score": (80, 92)},
        
        # ═══════════════════ GREATER KAILASH ═══════════════════
        {"name": "Greater Kailash Road", "waypoints": [[28.5400, 77.2350], [28.5370, 77.2400], [28.5340, 77.2450]], "score": (80, 95)},
        
        # ═══════════════════ OKHLA ═══════════════════
        {"name": "Okhla Industrial Road", "waypoints": [[28.5550, 77.2700], [28.5480, 77.2750], [28.5400, 77.2800]], "score": (40, 58)},
        
        # ═══════════════════ MAYUR VIHAR ═══════════════════
        {"name": "Mayur Vihar Link Road", "waypoints": [[28.6050, 77.2950], [28.6100, 77.3000], [28.6150, 77.3050]], "score": (60, 78)},
        
        # ═══════════════════ MEHRAULI-BADARPUR ═══════════════════
        {"name": "Mehrauli-Badarpur Road (North)", "waypoints": [[28.5200, 77.1780], [28.5100, 77.2000], [28.5000, 77.2200]], "score": (40, 58)},
        {"name": "Mehrauli-Badarpur Road (South)", "waypoints": [[28.5000, 77.2200], [28.4900, 77.2400], [28.4800, 77.2600]], "score": (35, 52)},
        
        # ═══════════════════ PRESS ENCLAVE / INA ═══════════════════
        {"name": "Press Enclave Road", "waypoints": [[28.5700, 77.2100], [28.5650, 77.2050], [28.5600, 77.2000]], "score": (65, 80)},
        {"name": "INA Market Road", "waypoints": [[28.5750, 77.2100], [28.5720, 77.2150], [28.5700, 77.2200]], "score": (60, 75)},
        
        # ═══════════════════ CHATTARPUR ═══════════════════
        {"name": "Chattarpur Road", "waypoints": [[28.5050, 77.1750], [28.4980, 77.1780], [28.4900, 77.1810]], "score": (50, 68)},
        
        # ═══════════════════ MOOLCHAND / BHIKAJI ═══════════════════
        {"name": "Moolchand Flyover", "waypoints": [[28.5720, 77.2350], [28.5700, 77.2400], [28.5690, 77.2450]], "score": (60, 75)},
        {"name": "Bhikaji Cama Place Road", "waypoints": [[28.5730, 77.1900], [28.5700, 77.1950], [28.5680, 77.2000]], "score": (70, 85)},
        
        # ═══════════════════ BURARI ═══════════════════
        {"name": "Burari Road", "waypoints": [[28.7300, 77.1900], [28.7400, 77.1920], [28.7500, 77.1950]], "score": (20, 38)},
        
        # ═══════════════════ MONGOLPURI ═══════════════════
        {"name": "Mongolpuri Road", "waypoints": [[28.6900, 77.0800], [28.6930, 77.0850], [28.6960, 77.0900]], "score": (22, 40)},
    ]
    
    return roads


def main():
    roads = get_delhi_roads()
    features = []
    total = len(roads)
    
    print(f"Tracing {total} Delhi roads via OSRM (exact road geometry)...")
    print("=" * 60)
    
    for i, road in enumerate(roads):
        name = road['name']
        waypoints = road['waypoints']
        score_range = road['score']
        
        sys.stdout.write(f"\r[{i+1}/{total}] Tracing: {name:<45}")
        sys.stdout.flush()
        
        coords = osrm_trace(waypoints)
        time.sleep(0.08)  # Be polite to the public OSRM server
        
        if not coords or len(coords) < 2:
            print(f" — SKIPPED (no geometry)")
            continue
        
        base_score = random.randint(*score_range)
        score_day = min(100, base_score + random.randint(5, 12))
        score_night = max(0, base_score - random.randint(18, 32))
        
        features.append({
            "type": "Feature",
            "properties": {
                "name": name,
                "score_day": score_day,
                "score_night": score_night,
                "trend": "improving" if base_score > 75 else ("worsening" if base_score < 35 else "stable"),
                "active_report_count": random.randint(3, 8) if base_score < 40 else random.randint(0, 2),
                "escalated": base_score < 25
            },
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            }
        })
    
    print(f"\n\nSuccessfully traced {len(features)} / {total} roads!")
    
    geojson = {"type": "FeatureCollection", "features": features}
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sw-final", "js")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "delhi_roads.js")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("const DELHI_ROAD_NETWORK = ")
        json.dump(geojson, f, ensure_ascii=False)
        f.write(";\n")
    
    size_kb = os.path.getsize(output_path) / 1024
    print(f"Saved to: {output_path}")
    print(f"File size: {size_kb:.1f} KB")
    print(f"Total road segments: {len(features)}")


if __name__ == "__main__":
    main()
