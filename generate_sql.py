import random
import math
import sys
import json
import urllib.request
import time
from datetime import datetime, timedelta

def fetch_geometry(lat, lng):
    end_lat = lat + 0.001
    end_lng = lng + 0.001
    try:
        url = f"https://router.project-osrm.org/route/v1/foot/{lng},{lat};{end_lng},{end_lat}?geometries=geojson"
        req = urllib.request.Request(url, headers={'User-Agent': 'SafeWalk/1.0'})
        res = urllib.request.urlopen(req, timeout=3)
        data = json.loads(res.read())
        if data.get('routes') and len(data['routes'][0]['geometry']['coordinates']) > 1:
            coords = data['routes'][0]['geometry']['coordinates']
            return json.dumps([[c[1], c[0]] for c in coords])
    except Exception as e:
        pass
    return json.dumps([[lat, lng], [lat + 0.0003, lng + 0.0003], [lat + 0.0006, lng + 0.0006], [lat + 0.001, lng + 0.001]])

def get_real_areas():
    return [
        # CENTRAL DELHI
        {"name": "Connaught Place", "lat": 28.630, "lng": 77.218, "score": (70, 85)},
        {"name": "Janpath", "lat": 28.625, "lng": 77.218, "score": (60, 75)},
        {"name": "Parliament Street", "lat": 28.625, "lng": 77.208, "score": (80, 95)},
        {"name": "Barakhamba Road", "lat": 28.630, "lng": 77.227, "score": (70, 85)},
        {"name": "Kashmere Gate", "lat": 28.667, "lng": 77.226, "score": (30, 50)},
        {"name": "Chandni Chowk", "lat": 28.656, "lng": 77.230, "score": (30, 45)},
        {"name": "Daryaganj", "lat": 28.643, "lng": 77.240, "score": (40, 60)},
        {"name": "ITO", "lat": 28.628, "lng": 77.243, "score": (55, 75)},
        {"name": "Minto Road", "lat": 28.635, "lng": 77.226, "score": (45, 60)},
        {"name": "Asaf Ali Road", "lat": 28.641, "lng": 77.234, "score": (40, 55)},
        {"name": "Paharganj", "lat": 28.643, "lng": 77.213, "score": (25, 45)},
        {"name": "Karol Bagh", "lat": 28.651, "lng": 77.190, "score": (55, 75)},
        {"name": "Patel Nagar", "lat": 28.651, "lng": 77.165, "score": (55, 75)},
        {"name": "Rajendra Nagar", "lat": 28.635, "lng": 77.182, "score": (60, 80)},
        {"name": "Shadipur", "lat": 28.651, "lng": 77.155, "score": (45, 65)},
        {"name": "Kirti Nagar", "lat": 28.641, "lng": 77.143, "score": (55, 75)},

        # NORTH DELHI
        {"name": "Civil Lines", "lat": 28.678, "lng": 77.224, "score": (65, 85)},
        {"name": "Model Town", "lat": 28.704, "lng": 77.191, "score": (60, 80)},
        {"name": "GTB Nagar", "lat": 28.698, "lng": 77.202, "score": (55, 70)},
        {"name": "Mukherjee Nagar", "lat": 28.711, "lng": 77.200, "score": (55, 70)},
        {"name": "Ashok Vihar", "lat": 28.694, "lng": 77.172, "score": (60, 80)},
        {"name": "Pitampura", "lat": 28.698, "lng": 77.135, "score": (65, 85)},
        {"name": "Rohini Sector", "lat": 28.725, "lng": 77.108, "score": (55, 75)},
        {"name": "Shalimar Bagh", "lat": 28.704, "lng": 77.156, "score": (60, 80)},
        {"name": "Bhalaswa", "lat": 28.736, "lng": 77.170, "score": (20, 35)},
        {"name": "Burari", "lat": 28.750, "lng": 77.192, "score": (25, 45)},
        {"name": "Timarpur", "lat": 28.693, "lng": 77.221, "score": (45, 60)},
        {"name": "Roop Nagar", "lat": 28.683, "lng": 77.199, "score": (50, 70)},
        {"name": "Shakti Nagar", "lat": 28.679, "lng": 77.195, "score": (55, 75)},
        {"name": "Kamla Nagar", "lat": 28.680, "lng": 77.201, "score": (55, 75)},

        # NORTH EAST DELHI
        {"name": "Yamuna Vihar", "lat": 28.705, "lng": 77.271, "score": (40, 60)},
        {"name": "Bhajanpura", "lat": 28.705, "lng": 77.262, "score": (35, 50)},
        {"name": "Mustafabad", "lat": 28.713, "lng": 77.275, "score": (25, 40)},
        {"name": "Karawal Nagar", "lat": 28.734, "lng": 77.273, "score": (25, 40)},
        {"name": "Seelampur", "lat": 28.664, "lng": 77.268, "score": (20, 35)},
        {"name": "Welcome Colony", "lat": 28.671, "lng": 77.274, "score": (30, 45)},
        {"name": "Maujpur", "lat": 28.686, "lng": 77.272, "score": (30, 45)},
        {"name": "Gokulpuri", "lat": 28.703, "lng": 77.288, "score": (25, 40)},
        {"name": "Shahdara", "lat": 28.679, "lng": 77.289, "score": (35, 55)},
        {"name": "Vivek Vihar", "lat": 28.667, "lng": 77.316, "score": (55, 75)},
        {"name": "Preet Vihar", "lat": 28.638, "lng": 77.295, "score": (65, 80)},
        {"name": "Karkarduma", "lat": 28.647, "lng": 77.302, "score": (60, 75)},
        {"name": "Anand Vihar", "lat": 28.650, "lng": 77.315, "score": (60, 75)},

        # EAST DELHI
        {"name": "Laxmi Nagar", "lat": 28.627, "lng": 77.276, "score": (45, 65)},
        {"name": "Nirman Vihar", "lat": 28.636, "lng": 77.287, "score": (55, 75)},
        {"name": "Patparganj", "lat": 28.624, "lng": 77.302, "score": (55, 75)},
        {"name": "Mayur Vihar Phase", "lat": 28.605, "lng": 77.294, "score": (60, 80)},
        {"name": "Kondli", "lat": 28.608, "lng": 77.327, "score": (35, 55)},
        {"name": "Vasundhara Enclave", "lat": 28.603, "lng": 77.318, "score": (60, 80)},
        {"name": "Mandawali", "lat": 28.627, "lng": 77.299, "score": (35, 50)},
        {"name": "Krishna Nagar", "lat": 28.653, "lng": 77.283, "score": (45, 60)},
        {"name": "Geeta Colony", "lat": 28.650, "lng": 77.270, "score": (45, 60)},
        {"name": "Gandhi Nagar", "lat": 28.660, "lng": 77.262, "score": (30, 45)},
        {"name": "IP Extension", "lat": 28.631, "lng": 77.310, "score": (60, 80)},

        # SOUTH DELHI
        {"name": "South Extension", "lat": 28.568, "lng": 77.220, "score": (75, 90)},
        {"name": "Greater Kailash", "lat": 28.535, "lng": 77.240, "score": (80, 95)},
        {"name": "Lajpat Nagar", "lat": 28.567, "lng": 77.243, "score": (65, 80)},
        {"name": "Defence Colony", "lat": 28.572, "lng": 77.230, "score": (85, 95)},
        {"name": "Hauz Khas", "lat": 28.548, "lng": 77.198, "score": (75, 90)},
        {"name": "Safdarjung Enclave", "lat": 28.561, "lng": 77.196, "score": (80, 95)},
        {"name": "Malviya Nagar", "lat": 28.534, "lng": 77.208, "score": (65, 80)},
        {"name": "Saket", "lat": 28.520, "lng": 77.200, "score": (75, 90)},
        {"name": "Sainik Farm", "lat": 28.498, "lng": 77.215, "score": (60, 80)},
        {"name": "Mehrauli", "lat": 28.518, "lng": 77.181, "score": (45, 65)},
        {"name": "Chattarpur", "lat": 28.502, "lng": 77.178, "score": (55, 75)},
        {"name": "Pushp Vihar", "lat": 28.527, "lng": 77.226, "score": (60, 75)},
        {"name": "Sheikh Sarai", "lat": 28.532, "lng": 77.222, "score": (60, 75)},
        {"name": "Chirag Delhi", "lat": 28.538, "lng": 77.220, "score": (45, 60)},
        {"name": "Munirka", "lat": 28.556, "lng": 77.172, "score": (55, 70)},
        {"name": "RK Puram", "lat": 28.566, "lng": 77.175, "score": (70, 85)},
        {"name": "Vasant Kunj", "lat": 28.528, "lng": 77.156, "score": (80, 95)},
        {"name": "Vasant Vihar", "lat": 28.560, "lng": 77.160, "score": (80, 95)},
        {"name": "Palam", "lat": 28.586, "lng": 77.086, "score": (45, 60)},
        {"name": "Dwarka Sector", "lat": 28.580, "lng": 77.040, "score": (65, 85)},

        # SOUTH WEST DELHI
        {"name": "Uttam Nagar", "lat": 28.621, "lng": 77.056, "score": (35, 55)},
        {"name": "Janakpuri", "lat": 28.621, "lng": 77.087, "score": (65, 85)},
        {"name": "Vikaspuri", "lat": 28.638, "lng": 77.072, "score": (60, 80)},
        {"name": "Nawada", "lat": 28.618, "lng": 77.047, "score": (35, 50)},
        {"name": "Bindapur", "lat": 28.611, "lng": 77.062, "score": (40, 55)},
        {"name": "Dashrath Puri", "lat": 28.601, "lng": 77.079, "score": (45, 60)},
        {"name": "Rajouri Garden", "lat": 28.641, "lng": 77.120, "score": (65, 85)},
        {"name": "Tagore Garden", "lat": 28.643, "lng": 77.112, "score": (60, 75)},
        {"name": "Subhash Nagar", "lat": 28.641, "lng": 77.106, "score": (55, 70)},
        {"name": "Tilak Nagar", "lat": 28.636, "lng": 77.096, "score": (50, 70)},
        {"name": "Punjabi Bagh", "lat": 28.665, "lng": 77.130, "score": (75, 90)},
        {"name": "Paschim Vihar", "lat": 28.668, "lng": 77.094, "score": (65, 80)},
        {"name": "Peera Garhi", "lat": 28.676, "lng": 77.086, "score": (40, 55)},
        {"name": "Nangloi", "lat": 28.683, "lng": 77.065, "score": (30, 45)},

        # WEST DELHI
        {"name": "Moti Nagar", "lat": 28.658, "lng": 77.142, "score": (55, 75)},
        {"name": "Ramesh Nagar", "lat": 28.648, "lng": 77.135, "score": (55, 70)},
        {"name": "Raja Garden", "lat": 28.645, "lng": 77.126, "score": (60, 75)},
        {"name": "Inderpuri", "lat": 28.632, "lng": 77.157, "score": (60, 75)},
        {"name": "Naraina", "lat": 28.625, "lng": 77.136, "score": (50, 65)},
        {"name": "Mayapuri", "lat": 28.624, "lng": 77.126, "score": (45, 60)},
        {"name": "Khyala", "lat": 28.646, "lng": 77.093, "score": (35, 50)},
        {"name": "Madipur", "lat": 28.664, "lng": 77.123, "score": (40, 55)},
        {"name": "Mongolpuri", "lat": 28.694, "lng": 77.084, "score": (25, 40)},
        {"name": "Nilothi", "lat": 28.654, "lng": 77.054, "score": (30, 45)},
        {"name": "Mundka", "lat": 28.681, "lng": 77.030, "score": (25, 40)},
        {"name": "Bahadurgarh Road", "lat": 28.665, "lng": 77.195, "score": (35, 50)},
        {"name": "Peeragarhi", "lat": 28.675, "lng": 77.085, "score": (40, 60)},

        # OLD DELHI / WALLED CITY
        {"name": "Lal Quila", "lat": 28.655, "lng": 77.240, "score": (40, 60)},
        {"name": "Jama Masjid", "lat": 28.650, "lng": 77.233, "score": (30, 45)},
        {"name": "Chawri Bazar", "lat": 28.648, "lng": 77.228, "score": (30, 45)},
        {"name": "Ballimaran", "lat": 28.653, "lng": 77.226, "score": (25, 40)},
        {"name": "Nai Sarak", "lat": 28.651, "lng": 77.229, "score": (35, 50)},
        {"name": "Khari Baoli", "lat": 28.657, "lng": 77.222, "score": (30, 45)},
        {"name": "Sadar Bazar", "lat": 28.653, "lng": 77.210, "score": (25, 45)},
        {"name": "Ajmeri Gate", "lat": 28.642, "lng": 77.224, "score": (30, 45)},
        {"name": "Turkman Gate", "lat": 28.639, "lng": 77.231, "score": (25, 40)},
        {"name": "Hauz Qazi", "lat": 28.645, "lng": 77.228, "score": (30, 45)},
        {"name": "Matia Mahal", "lat": 28.648, "lng": 77.234, "score": (30, 45)},
        {"name": "Chitli Qabar", "lat": 28.644, "lng": 77.236, "score": (25, 40)},

        # NEW DELHI LANDMARKS AND ROADS
        {"name": "India Gate", "lat": 28.612, "lng": 77.229, "score": (80, 95)},
        {"name": "Rajpath", "lat": 28.613, "lng": 77.218, "score": (85, 95)},
        {"name": "Akbar Road", "lat": 28.601, "lng": 77.213, "score": (85, 95)},
        {"name": "Race Course Road", "lat": 28.599, "lng": 77.202, "score": (85, 95)},
        {"name": "Shantipath", "lat": 28.587, "lng": 77.169, "score": (85, 95)},
        {"name": "Aurangzeb Road", "lat": 28.596, "lng": 77.212, "score": (85, 95)},
        {"name": "Lodhi Road", "lat": 28.588, "lng": 77.225, "score": (80, 90)},
        {"name": "Mathura Road", "lat": 28.607, "lng": 77.240, "score": (65, 80)},
        {"name": "Ring Road", "lat": 28.571, "lng": 77.256, "score": (65, 80)},
        {"name": "NH48", "lat": 28.541, "lng": 77.108, "score": (60, 75)},
        {"name": "NH44", "lat": 28.718, "lng": 77.154, "score": (55, 70)},
        {"name": "Outer Ring Road", "lat": 28.694, "lng": 77.126, "score": (65, 80)},
        {"name": "Inner Ring Road", "lat": 28.641, "lng": 77.248, "score": (65, 80)},
        {"name": "Mehrauli Gurgaon Road", "lat": 28.490, "lng": 77.140, "score": (60, 75)},
        {"name": "Noida Link Road", "lat": 28.617, "lng": 77.284, "score": (60, 75)},
    ]

def generate_sql():
    areas = get_real_areas()
    streets = []
    
    suffixes = ["Road", "Lane", "Street", "Marg", "Avenue", "Enclave", "Block", "Market", "Extension"]
    
    # Generate streets
    target_count = 150 # Processing 150 streets to keep it reasonably fast with API overhead
    for i in range(250):
        area = random.choice(areas)
        lat = area["lat"] + random.uniform(-0.015, 0.015)
        lng = area["lng"] + random.uniform(-0.015, 0.015)
        
        street_id = f"{round(lat, 3)}_{round(lng, 3)}"
        
        # Avoid duplicate street_ids
        if any(s['street_id'] == street_id for s in streets):
            continue
            
        base_name = area["name"]
        
        # 50% chance to just use the area name if it includes a suffix or block
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
        
        trends = ["improving", "stable", "worsening"]
        if score < 35:
            trend = random.choice(["stable", "worsening"])
        elif score > 75:
            trend = random.choice(["stable", "improving"])
        trend = random.choice(trends)
            
        # Add a sleep to prevent getting blocked by public OSRM server
        time.sleep(0.04)
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
            
    print("\n")

    # Generate Reports
    reports = []
    incident_types = [
        "poor_lighting", "suspicious_person", "harassment", "assault", 
        "eve_teasing", "theft_robbery", "drunk_crowd", "broken_cctv", 
        "isolated_road", "general_unsafe"
    ]
    
    for i in range(160):  # More than 150
        street = random.choice(streets)
        # Weight reports towards lower scores
        if street["score"] > 60 and random.random() > 0.3:
            street = random.choice([s for s in streets if s["score"] < 50]) or street
            
        incident = random.choice(incident_types)
        severity = random.randint(3, 5) if incident in ["assault", "harassment", "theft_robbery"] else random.randint(1, 3)
        
        desc_map = {
            "poor_lighting": ["Street lights broken here", "Very dark after 9PM", "No lights at this intersection"],
            "suspicious_person": ["Someone following people", "Group of guys staring at women", "Suspicious vehicle parked"],
            "harassment": ["Catcalling by a group", "Harassment near the metro", "Verbal abuse"],
            "assault": ["Physical altercation seen", "Someone was attacked here", "Fight broke out"],
            "eve_teasing": ["Boys passing comments", "Unsafe for women walking alone", "Eve teasing at bus stop"],
            "theft_robbery": ["Phone snatched here yesterday", "Chain snatching incident", "Purse stolen near the market"],
            "drunk_crowd": ["Drunk men outside the liquor shop", "People drinking in cars", "Rowdy crowd after 10PM"],
            "broken_cctv": ["CCTV is pointing downwards", "Cameras have been damaged", "No CCTV coverage here"],
            "isolated_road": ["Very lonely stretch", "No one around after dark", "Needs police patrolling"],
            "general_unsafe": ["Doesn't feel safe walking here", "Bad vibes in this lane", "Avoid this route at night"]
        }
        
        description = random.choice(desc_map[incident])
        
        photo_url = f"/uploads/demo_report_{i+1}.jpg"
        anonymous = random.choice([True, False])
        
        hours_ago = random.randint(1, 48)
        resolved = 1 if hours_ago > 24 and random.random() > 0.5 else 0
        
        reports.append({
            "user_id": random.randint(1, 5),
            "lat": street["lat"],
            "lng": street["lng"],
            "street_name": street["street_name"],
            "street_id": street["street_id"],
            "incident_type": incident,
            "severity": severity,
            "description": description.replace("'", "\\'"),
            "photo_url": photo_url,
            "anonymous": 1 if anonymous else 0,
            "resolved": resolved,
            "hours_ago": hours_ago
        })

    # START WRITING SQL
    sql = []
    sql.append("USE safewalk;\n")
    sql.append("SET FOREIGN_KEY_CHECKS = 0;")
    sql.append("TRUNCATE TABLE score_history;")
    sql.append("TRUNCATE TABLE street_safety_scores;")
    sql.append("TRUNCATE TABLE reports;")
    sql.append("SET FOREIGN_KEY_CHECKS = 1;\n")
    
    # Try adding geometry column if it doesn't exist
    sql.append("DROP PROCEDURE IF EXISTS upgrade_table;")
    sql.append("DELIMITER //")
    sql.append("CREATE PROCEDURE upgrade_table()")
    sql.append("BEGIN")
    sql.append("  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;")
    sql.append("  ALTER TABLE street_safety_scores ADD COLUMN geometry JSON;")
    sql.append("END //")
    sql.append("DELIMITER ;")
    sql.append("CALL upgrade_table();\n")

    
    sql.append("INSERT IGNORE INTO users (id, name, email, password, role, trust_score, is_verified)")
    sql.append("VALUES")
    sql.append("(1, 'Rahul Sharma', 'rahul@test.com', '$2b$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'user', 1.2, true),")
    sql.append("(2, 'Priya Singh', 'priya@test.com', '$2b$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'user', 1.5, true),")
    sql.append("(3, 'Amit Kumar', 'amit@test.com', '$2b$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'user', 0.9, false),")
    sql.append("(4, 'Neha Gupta', 'neha@test.com', '$2b$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'user', 1.8, true),")
    sql.append("(5, 'Vikram Yadav', 'vikram@test.com', '$2b$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'user', 0.7, false);\n")

    # Generate Street Batches
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

    # Generate Report Batches
    for i in range(0, len(reports), batch_size):
        batch = reports[i:i+batch_size]
        sql.append("INSERT INTO reports (user_id, lat, lng, street_name, street_id, incident_type, severity, description, photo_url, anonymous, resolved, reported_at) VALUES")
        values = []
        for r in batch:
            val = f"({r['user_id']}, {r['lat']}, {r['lng']}, '{r['street_name']}', '{r['street_id']}', '{r['incident_type']}', {r['severity']}, '{r['description']}', '{r['photo_url']}', {r['anonymous']}, {r['resolved']}, DATE_SUB(NOW(), INTERVAL {r['hours_ago']} HOUR))"
            values.append(val)
        sql.append(",\n".join(values) + ";\n")

    sql.append("SELECT COUNT(*) as total_streets FROM street_safety_scores;")
    sql.append("SELECT COUNT(*) as total_reports FROM reports;")
    sql.append("SELECT AVG(score) as avg_safety_score FROM street_safety_scores;")
    sql.append("SELECT street_name, score FROM street_safety_scores ORDER BY score ASC LIMIT 10;\n")

    with open("d:/SAFEWALK/delhi_safewalk_data.sql", "w", encoding="utf-8") as f:
        f.write("\n".join(sql))

if __name__ == "__main__":
    generate_sql()
    print("Generated d:/SAFEWALK/delhi_safewalk_data.sql")
