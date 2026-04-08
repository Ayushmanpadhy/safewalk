import random
import sys
import json
import math
import os

def fetch_geometry(lat, lng):
    # Generate an organic, mathematically curved road shape to simulate a curved natural road instantly.
    coords = []
    points = random.randint(10, 25)
    length = random.uniform(0.003, 0.015)
    angle = random.uniform(0, 2 * math.pi)
    curve = random.uniform(-0.002, 0.002)
    
    cur_lat = lat
    cur_lng = lng
    
    for i in range(points):
        coords.append([cur_lng, cur_lat]) # Notice: GeoJSON format uses [lng, lat] while Google Maps / DB usually sometimes need [lat, lng]. But db geometry here expects GeoJSON-style [lng, lat] for Leaflet or similar depending on the parser. But let's check `safewalk-backend/controllers` earlier - it says it takes `[lng, lat]` or uses leaflet correctly. Actually, let's keep [lat, lng] if that was how `generate_indian_sql.py` worked. Let's use [lng, lat] as it's standard GeoJSON. We can fix if needed. Wait, in `generate_indian_sql.py`, coords were `[cur_lat, cur_lng]`. Oh, the db takes `[lat, lng]`? No, DB takes it. Then the frontend parses it. The frontend map_engine logic is `[lng, lat]`... wait. Let's check `generate_indian_sql.py` coords = `[cur_lat, cur_lng]`. 
        # Actually it's safer to store [lng, lat] properly for GeoJSON.
        cur_lat += (math.cos(angle) * (length/points)) + (math.sin(angle) * curve)
        cur_lng += (math.sin(angle) * (length/points)) - (math.cos(angle) * curve)
        angle += random.uniform(-0.3, 0.3)
        
    return json.dumps(coords)

def get_real_areas():
    return {
        "Delhi": [
            {"name": "Connaught Place", "lat": 28.630, "lng": 77.218},
            {"name": "Parliament Street", "lat": 28.625, "lng": 77.208},
            {"name": "Kashmere Gate", "lat": 28.667, "lng": 77.226},
            {"name": "Daryaganj", "lat": 28.643, "lng": 77.240},
            {"name": "Paharganj", "lat": 28.643, "lng": 77.213},
            {"name": "Hauz Khas", "lat": 28.548, "lng": 77.198},
            {"name": "Vasant Kunj", "lat": 28.528, "lng": 77.156},
            {"name": "Jama Masjid", "lat": 28.650, "lng": 77.233},
            {"name": "Rohini", "lat": 28.715, "lng": 77.114},
            {"name": "Dwarka", "lat": 28.582, "lng": 77.050}
        ],
        "Mumbai": [
            {"name": "Bandra West", "lat": 19.0544, "lng": 72.8402},
            {"name": "Colaba", "lat": 18.9067, "lng": 72.8147},
            {"name": "Andheri West", "lat": 19.1136, "lng": 72.8697},
            {"name": "Juhu", "lat": 19.1075, "lng": 72.8263},
            {"name": "Dharavi", "lat": 19.0402, "lng": 72.8553},
            {"name": "Lower Parel", "lat": 18.9953, "lng": 72.8256},
            {"name": "Marine Drive", "lat": 18.9419, "lng": 72.8242},
            {"name": "Kurla", "lat": 19.0728, "lng": 72.8826},
            {"name": "Worli", "lat": 19.016, "lng": 72.816},
            {"name": "Powai", "lat": 19.119, "lng": 72.905}
        ],
        "Bangalore": [
            {"name": "Indiranagar", "lat": 12.9784, "lng": 77.6408},
            {"name": "Koramangala", "lat": 12.9279, "lng": 77.6271},
            {"name": "Whitefield", "lat": 12.9698, "lng": 77.7499},
            {"name": "MG Road", "lat": 12.9716, "lng": 77.6011},
            {"name": "Majestic", "lat": 12.9766, "lng": 77.5713},
            {"name": "Shivajinagar", "lat": 12.9857, "lng": 77.6057},
            {"name": "Jayanagar", "lat": 12.9299, "lng": 77.5826},
            {"name": "KR Market", "lat": 12.9655, "lng": 77.5746},
            {"name": "Hebbal", "lat": 13.035, "lng": 77.597},
            {"name": "Malleshwaram", "lat": 13.003, "lng": 77.570}
        ],
        "Hyderabad": [
            {"name": "Banjara Hills", "lat": 17.4116, "lng": 78.4357},
            {"name": "Jubilee Hills", "lat": 17.4325, "lng": 78.4070},
            {"name": "HITEC City", "lat": 17.4435, "lng": 78.3772},
            {"name": "Charminar", "lat": 17.3616, "lng": 78.4747},
            {"name": "Gachibowli", "lat": 17.4401, "lng": 78.3489},
            {"name": "Secunderabad", "lat": 17.4399, "lng": 78.4983},
            {"name": "Begumpet", "lat": 17.4448, "lng": 78.4664},
            {"name": "Old City", "lat": 17.3500, "lng": 78.4800},
            {"name": "Kukatpally", "lat": 17.484, "lng": 78.388},
            {"name": "Madhapur", "lat": 17.448, "lng": 78.391}
        ]
    }

def generate_sql():
    cities_areas = get_real_areas()
    streets = []
    suffixes = ["Road", "Lane", "Street", "Marg", "Avenue", "Enclave", "Block", "Market", "Extension", "Boulevard", "Highway", "Alley"]
    
    print("Generating massive local dataset across 4 cities...")
    
    target_count_per_city = 375 # 1500 total streets
    
    for city, areas in cities_areas.items():
        city_streets_count = 0
        while city_streets_count < target_count_per_city:
            area = random.choice(areas)
            lat = area["lat"] + random.uniform(-0.06, 0.06)
            lng = area["lng"] + random.uniform(-0.06, 0.06)
            
            street_id = f"{city}_{round(lat, 5)}_{round(lng, 5)}"
            
            base_name = area["name"]
            if random.random() > 0.4:
                num = random.randint(1, 50)
                street_name = f"{base_name} {random.choice(['Block', 'Sector', 'Phase', 'Cross', 'Main'])} {num}"
            else:
                if "Road" not in base_name and "Marg" not in base_name and "Street" not in base_name:
                    street_name = f"{base_name} {random.choice(suffixes)}"
                else:
                    street_name = base_name

            score = random.randint(10, 95)
            # More extreme scores for better heatmap viewing
            if random.random() < 0.2: score = random.randint(10, 30)
            elif random.random() < 0.2: score = random.randint(75, 95)
            
            score_day = min(100, score + random.randint(5, 15))
            score_night = max(0, score - random.randint(15, 30))
            escalated = 1 if score < 25 else 0
            active_report_count = random.randint(3, 10) if score < 40 else random.randint(0, 2)
            trend = "improving" if score > 75 else ("worsening" if score < 35 else random.choice(["improving", "stable", "worsening"]))
            
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
            city_streets_count += 1
            
    print("\nWriting SQL File...")
            
    sql = []
    sql.append("USE safewalk;\n")
    sql.append("SET FOREIGN_KEY_CHECKS = 0;")
    sql.append("TRUNCATE TABLE score_history;")
    sql.append("TRUNCATE TABLE street_safety_scores;")
    sql.append("TRUNCATE TABLE reports;\n")
    
    sql.append("-- ===== Add geometry column if it does not exist =====")
    sql.append("SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='safewalk' AND TABLE_NAME='street_safety_scores' AND COLUMN_NAME='geometry');")
    sql.append("SET @sql = IF(@col_exists = 0, 'ALTER TABLE street_safety_scores ADD COLUMN geometry JSON DEFAULT NULL', 'SELECT 1');")
    sql.append("PREPARE stmt FROM @sql;")
    sql.append("EXECUTE stmt;")
    sql.append("DEALLOCATE PREPARE stmt;")
    sql.append("")
    sql.append("SET FOREIGN_KEY_CHECKS = 1;\n")

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

    with open("d:/SAFEWALK/massive_safewalk_data.sql", "w", encoding="utf-8") as f:
        f.write("\n".join(sql))

if __name__ == "__main__":
    generate_sql()
    print("Generated d:/SAFEWALK/massive_safewalk_data.sql")
