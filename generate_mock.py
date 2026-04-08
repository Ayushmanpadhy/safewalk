import os
import json
import random

CITIES = {
    "Delhi": "28.58,77.18,28.64,77.24",
    "Mumbai": "19.03,72.80,19.08,72.85",
    "Bangalore": "12.94,77.56,13.00,77.63",
    "Hyderabad": "17.36,78.44,17.42,78.50"
}

all_features = []

for city, bbox in CITIES.items():
    print(f"Generating synthetic grid for {city}...")
    bbox_parts = bbox.split(',')
    min_lat, min_lon, max_lat, max_lon = float(bbox_parts[0]), float(bbox_parts[1]), float(bbox_parts[2]), float(bbox_parts[3])
    
    # Simple grid generator
    num_steps = 70
    for lat_step in range(num_steps):
        cur_lat = min_lat + (max_lat - min_lat) * (lat_step / float(num_steps))
        coords = [[min_lon, cur_lat], [max_lon, cur_lat]]
        base_score = random.randint(40, 95)
        if random.random() < 0.2: base_score = random.randint(10, 30) # 20% danger routes
        feature = {
            "type": "Feature",
            "properties": {
                "street_name": f"{city} Ave {lat_step}",
                "city": city,
                "score_day": min(100, base_score + random.randint(5, 15)),
                "score_night": max(0, base_score - random.randint(20, 35)),
                "active_report_count": random.randint(0, 5) if base_score < 50 else random.randint(0, 1),
                "trend": "stable",
                "escalated": base_score < 25
            },
            "geometry": { "type": "LineString", "coordinates": coords }
        }
        all_features.append(feature)
        
    for lon_step in range(num_steps):
        cur_lon = min_lon + (max_lon - min_lon) * (lon_step / float(num_steps))
        coords = [[cur_lon, min_lat], [cur_lon, max_lat]]
        base_score = random.randint(40, 95)
        if random.random() < 0.2: base_score = random.randint(10, 30) # 20% danger routes
        feature = {
            "type": "Feature",
            "properties": {
                "street_name": f"{city} St {lon_step}",
                "city": city,
                "score_day": min(100, base_score + random.randint(5, 15)),
                "score_night": max(0, base_score - random.randint(20, 35)),
                "active_report_count": random.randint(0, 5) if base_score < 50 else random.randint(0, 1),
                "trend": "stable",
                "escalated": base_score < 25
            },
            "geometry": { "type": "LineString", "coordinates": coords }
        }
        all_features.append(feature)

print(f"Total processed roads across all cities: {len(all_features)}")

geojson = {
    "type": "FeatureCollection",
    "features": all_features
}

output_path = os.path.join(os.path.dirname(__file__), "sw-final", "js", "indian_roads.js")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("const ALL_ROADS_DATA = ")
    json.dump(geojson, f, ensure_ascii=False)
    f.write(";\n")
    
print(f"Successfully generated {output_path}")
