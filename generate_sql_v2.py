import random
import sys
import json
import urllib.request
import time

def fetch_geometry(lat, lng):
    # Ask OSRM for a foot route from this coordinate to slightly away (to get the road shape)
    end_lat = lat + 0.001
    end_lng = lng + 0.001
    
    try:
        url = f"https://router.project-osrm.org/route/v1/foot/{lng},{lat};{end_lng},{end_lat}?geometries=geojson"
        req = urllib.request.Request(url, headers={'User-Agent': 'SafeWalk/1.0'})
        res = urllib.request.urlopen(req, timeout=3)
        data = json.loads(res.read())
        
        if data.get('routes') and len(data['routes'][0]['geometry']['coordinates']) > 1:
            # OSRM returns [lng, lat], let's store as [lat, lng] for leaflet
            coords = data['routes'][0]['geometry']['coordinates']
            leaflet_coords = [[c[1], c[0]] for c in coords]
            return json.dumps(leaflet_coords)
    except Exception as e:
        print(f"OSRM Error {lat},{lng}: {e}")
        pass
        
    # Fallback to straight line segment over 4 points to simulate a road
    return json.dumps([
        [lat, lng],
        [lat + 0.0003, lng + 0.0003],
        [lat + 0.0006, lng + 0.0006],
        [lat + 0.001, lng + 0.001]
    ])

def get_real_areas():
    return [
        # (Same areas from the original script)
        {"name": "Connaught Place", "lat": 28.630, "lng": 77.218, "score": (70, 85)},
        {"name": "Parliament Street", "lat": 28.625, "lng": 77.208, "score": (80, 95)},
        {"name": "Kashmere Gate", "lat": 28.667, "lng": 77.226, "score": (30, 50)},
        {"name": "Daryaganj", "lat": 28.643, "lng": 77.240, "score": (40, 60)},
        {"name": "Paharganj", "lat": 28.643, "lng": 77.213, "score": (25, 45)},
        {"name": "Karol Bagh", "lat": 28.651, "lng": 77.190, "score": (55, 75)},
        {"name": "Rajendra Nagar", "lat": 28.635, "lng": 77.182, "score": (60, 80)},
        {"name": "Model Town", "lat": 28.704, "lng": 77.191, "score": (60, 80)},
        {"name": "Mukherjee Nagar", "lat": 28.711, "lng": 77.200, "score": (55, 70)},
        {"name": "Rohini Sector", "lat": 28.725, "lng": 77.108, "score": (55, 75)},
        {"name": "Burari", "lat": 28.750, "lng": 77.192, "score": (25, 45)},
        {"name": "Seelampur", "lat": 28.664, "lng": 77.268, "score": (20, 35)},
        {"name": "Laxmi Nagar", "lat": 28.627, "lng": 77.276, "score": (45, 65)},
        {"name": "South Extension", "lat": 28.568, "lng": 77.220, "score": (75, 90)},
        {"name": "Greater Kailash", "lat": 28.535, "lng": 77.240, "score": (80, 95)},
        {"name": "Hauz Khas", "lat": 28.548, "lng": 77.198, "score": (75, 90)},
        {"name": "Vasant Kunj", "lat": 28.528, "lng": 77.156, "score": (80, 95)},
        {"name": "Dwarka Sector", "lat": 28.580, "lng": 77.040, "score": (65, 85)},
        {"name": "Janakpuri", "lat": 28.621, "lng": 77.087, "score": (65, 85)},
        {"name": "Rajouri Garden", "lat": 28.641, "lng": 77.120, "score": (65, 85)},
        {"name": "Punjabi Bagh", "lat": 28.665, "lng": 77.130, "score": (75, 90)},
        {"name": "Jama Masjid", "lat": 28.650, "lng": 77.233, "score": (30, 45)},
        {"name": "India Gate", "lat": 28.612, "lng": 77.229, "score": (80, 95)},
        {"name": "Ring Road", "lat": 28.571, "lng": 77.256, "score": (65, 80)},
        {"name": "Okhla", "lat": 28.562, "lng": 77.284, "score": (40, 60)}
    ]

def generate_sql():
    areas = get_real_areas()
    streets = []
    suffixes = ["Road", "Lane", "Street", "Marg", "Avenue", "Enclave", "Block", "Market", "Extension"]
    
    print("Generating geometry maps...")
    
    target_count = 150 # Decreased to 150 to keep processing fast (~10-15s) and reduce OSRM load
    
    for i in range(250):
        area = random.choice(areas)
        lat = area["lat"] + random.uniform(-0.015, 0.015)
        lng = area["lng"] + random.uniform(-0.015, 0.015)
        
        street_id = f"{round(lat, 3)}_{round(lng, 3)}"
        if any(s['street_id'] == street_id for s in streets): continue
            
        base_name = area["name"]
        if random.random() > 0.5:
            num = random.randint(1, 15)
            street_name = f"{base_name} {random.choice(['Block', 'Sector', 'Phase'])} {num}"
        else:
            if "Road" not in base_name and "Marg" not in base_name and "Street" not in base_name and "Lane" not in base_name:
                street_name = f"{base_name} {random.choice(suffixes)}"
            else:
                street_name = base_name

        score = random.randint(area["score"][0], area["score"][1])
        score_day = min(100, score + random.randint(5, 10))
        score_night = max(0, score - random.randint(15, 25))
        escalated = 1 if score < 30 else 0
        active_report_count = random.randint(3, 8) if score < 40 else random.randint(0, 3)
        trend = "improving" if score > 75 else ("worsening" if score < 35 else random.choice(["improving", "stable", "worsening"]))
        
        # Add a sleep to prevent getting blocked by public OSRM server
        time.sleep(0.05)
        sys.stdout.write(f"\rFetching streets: {len(streets)+1}/{target_count} ({street_name})")
        sys.stdout.flush()
        
        geom_json = fetch_geometry(lat, lng)
            
        streets.append({
            "street_id": street_id,
            "street_name": street_name,
            "lat": round(lat, 5),
            "lng": round(lng, 5),
            "score": score,
            "score_day": score_day,
            "score_night": score_night,
            "active_report_count": active_report_count,
            "trend": trend,
            "escalated": escalated,
            "geometry": geom_json
        })

        if len(streets) >= target_count:
            break
            
    print("\nWriting SQL File...")
            
    # START WRITING SQL
    sql = []
    sql.append("USE safewalk;\n")
    sql.append("SET FOREIGN_KEY_CHECKS = 0;")
    sql.append("TRUNCATE TABLE score_history;")
    sql.append("TRUNCATE TABLE street_safety_scores;")
    sql.append("TRUNCATE TABLE reports;\n")
    
    # Check if geometry column exists, if not add it safely
    sql.append("ALTER TABLE street_safety_scores ADD COLUMN IF NOT EXISTS geometry JSON;\n")
    
    sql.append("SET FOREIGN_KEY_CHECKS = 1;\n")

    # Batches
    batch_size = 50
    for i in range(0, len(streets), batch_size):
        batch = streets[i:i+batch_size]
        sql.append("INSERT INTO street_safety_scores (street_id, street_name, lat, lng, score, score_day, score_night, active_report_count, trend, escalated, geometry, last_updated) VALUES")
        values = []
        for s in batch:
            g = s['geometry']
            val = f"('{s['street_id']}', '{s['street_name']}', {s['lat']}, {s['lng']}, {s['score']}, {s['score_day']}, {s['score_night']}, {s['active_report_count']}, '{s['trend']}', {s['escalated']}, '{g}', NOW())"
            values.append(val)
        sql.append(",\n".join(values) + ";\n")

    with open("d:/SAFEWALK/delhi_safewalk_data.sql", "w", encoding="utf-8") as f:
        f.write("\n".join(sql))

if __name__ == "__main__":
    generate_sql()
    print("Generated d:/SAFEWALK/delhi_safewalk_data.sql")
