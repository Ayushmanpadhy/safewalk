import random
import sys
import json
import urllib.request
import time
import math

def fetch_geometry(lat, lng):
    # Generate an organic, mathematically curved road shape to simulate a curved natural road instantly.
    coords = []
    points = 12
    length = random.uniform(0.003, 0.008)
    angle = random.uniform(0, 2 * math.pi)
    curve = random.uniform(-0.001, 0.001)
    
    cur_lat = lat
    cur_lng = lng
    
    for i in range(points):
        coords.append([cur_lat, cur_lng])
        cur_lat += (math.cos(angle) * (length/points)) + (math.sin(angle) * curve)
        cur_lng += (math.sin(angle) * (length/points)) - (math.cos(angle) * curve)
        angle += random.uniform(-0.2, 0.2)
        
    return json.dumps(coords)

def get_real_areas():
    return {
        "Delhi": [
            {"name": "Connaught Place", "lat": 28.630, "lng": 77.218, "score": (70, 85)},
            {"name": "Parliament Street", "lat": 28.625, "lng": 77.208, "score": (80, 95)},
            {"name": "Kashmere Gate", "lat": 28.667, "lng": 77.226, "score": (30, 50)},
            {"name": "Daryaganj", "lat": 28.643, "lng": 77.240, "score": (40, 60)},
            {"name": "Paharganj", "lat": 28.643, "lng": 77.213, "score": (25, 45)},
            {"name": "Hauz Khas", "lat": 28.548, "lng": 77.198, "score": (75, 90)},
            {"name": "Vasant Kunj", "lat": 28.528, "lng": 77.156, "score": (80, 95)},
            {"name": "Jama Masjid", "lat": 28.650, "lng": 77.233, "score": (30, 45)}
        ],
        "Mumbai": [
            {"name": "Bandra West", "lat": 19.0544, "lng": 72.8402, "score": (65, 85)},
            {"name": "Colaba", "lat": 18.9067, "lng": 72.8147, "score": (75, 95)},
            {"name": "Andheri West", "lat": 19.1136, "lng": 72.8697, "score": (50, 75)},
            {"name": "Juhu", "lat": 19.1075, "lng": 72.8263, "score": (70, 90)},
            {"name": "Dharavi", "lat": 19.0402, "lng": 72.8553, "score": (20, 45)},
            {"name": "Lower Parel", "lat": 18.9953, "lng": 72.8256, "score": (60, 80)},
            {"name": "Marine Drive", "lat": 18.9419, "lng": 72.8242, "score": (80, 95)},
            {"name": "Kurla", "lat": 19.0728, "lng": 72.8826, "score": (30, 50)}
        ],
        "Bangalore": [
            {"name": "Indiranagar", "lat": 12.9784, "lng": 77.6408, "score": (70, 90)},
            {"name": "Koramangala", "lat": 12.9279, "lng": 77.6271, "score": (65, 85)},
            {"name": "Whitefield", "lat": 12.9698, "lng": 77.7499, "score": (60, 80)},
            {"name": "MG Road", "lat": 12.9716, "lng": 77.6011, "score": (75, 95)},
            {"name": "Majestic", "lat": 12.9766, "lng": 77.5713, "score": (35, 55)},
            {"name": "Shivajinagar", "lat": 12.9857, "lng": 77.6057, "score": (25, 45)},
            {"name": "Jayanagar", "lat": 12.9299, "lng": 77.5826, "score": (70, 90)},
            {"name": "KR Market", "lat": 12.9655, "lng": 77.5746, "score": (20, 40)}
        ],
        "Hyderabad": [
            {"name": "Banjara Hills", "lat": 17.4116, "lng": 78.4357, "score": (75, 95)},
            {"name": "Jubilee Hills", "lat": 17.4325, "lng": 78.4070, "score": (80, 95)},
            {"name": "HITEC City", "lat": 17.4435, "lng": 78.3772, "score": (70, 85)},
            {"name": "Charminar", "lat": 17.3616, "lng": 78.4747, "score": (30, 50)},
            {"name": "Gachibowli", "lat": 17.4401, "lng": 78.3489, "score": (65, 85)},
            {"name": "Secunderabad", "lat": 17.4399, "lng": 78.4983, "score": (55, 75)},
            {"name": "Begumpet", "lat": 17.4448, "lng": 78.4664, "score": (60, 80)},
            {"name": "Old City", "lat": 17.3500, "lng": 78.4800, "score": (20, 40)}
        ]
    }

def generate_sql():
    cities_areas = get_real_areas()
    streets = []
    suffixes = ["Road", "Lane", "Street", "Marg", "Avenue", "Enclave", "Block", "Market", "Extension"]
    
    print("Generating geometry maps across 4 cities...")
    
    target_count_per_city = 100 # 400 total streets
    
    for city, areas in cities_areas.items():
        city_streets_count = 0
        for i in range(250):
            if city_streets_count >= target_count_per_city:
                break
                
            area = random.choice(areas)
            lat = area["lat"] + random.uniform(-0.015, 0.015)
            lng = area["lng"] + random.uniform(-0.015, 0.015)
            
            street_id = f"{city}_{round(lat, 3)}_{round(lng, 3)}"
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
            
            # No sleep needed for math generation
            sys.stdout.write(f"\rFetching streets for {city}: {city_streets_count+1}/{target_count_per_city}        ")
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
            city_streets_count += 1
        print("") # new line for next city
            
    print("\nWriting SQL File...")
            
    sql = []
    sql.append("USE safewalk;\n")
    sql.append("SET FOREIGN_KEY_CHECKS = 0;")
    sql.append("TRUNCATE TABLE score_history;")
    sql.append("TRUNCATE TABLE street_safety_scores;")
    sql.append("TRUNCATE TABLE reports;\n")
    
    # Add geometry column — simple approach that won't error if column already exists
    # We'll use a simple SET + error suppression approach
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

    with open("d:/SAFEWALK/indian_safewalk_data.sql", "w", encoding="utf-8") as f:
        f.write("\n".join(sql))

if __name__ == "__main__":
    generate_sql()
    print("Generated d:/SAFEWALK/indian_safewalk_data.sql")
