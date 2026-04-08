import urllib.request
import json
import random
import os
import ssl

CITIES = {
    "Delhi": "28.58,77.18,28.64,77.24",
    "Mumbai": "19.03,72.80,19.08,72.85",
    "Bangalore": "12.94,77.56,13.00,77.63",
    "Hyderabad": "17.36,78.44,17.42,78.50"
}

queries = []
for city, bbox in CITIES.items():
    query = f"""
    [out:json][timeout:90];
    (
      way["highway"~"primary|secondary|tertiary|residential"]({bbox});
    );
    out geom;
    """
    queries.append((city, query))

all_features = []

print("Starting giant fetch. This might take 1-3 minutes...")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for city, query in queries:
    print(f"Fetching {city} road network from Overpass API...")
    req = urllib.request.Request("http://overpass-api.de/api/interpreter", data=query.encode('utf-8'))
    try:
        with urllib.request.urlopen(req, timeout=120, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"Downloaded {len(data['elements'])} road segments for {city}. Generating scores...")

            for element in data['elements']:
                if element['type'] == 'way' and 'geometry' in element:
                    coords = []
                    for point in element['geometry']:
                        coords.append([point['lon'], point['lat']])
                        
                    tags = element.get('tags', {})
                    name = tags.get('name', 'Unnamed Road')
                    base_score = random.randint(30, 95)
                    if random.random() < 0.1:
                        base_score = random.randint(10, 30)
                        
                    score_day = min(100, base_score + random.randint(5, 15))
                    score_night = max(0, base_score - random.randint(20, 35))
                    
                    trend = "stable"
                    if base_score < 40: trend = random.choice(["worsening", "stable"])
                    elif base_score > 75: trend = random.choice(["improving", "stable"])

                    feature = {
                        "type": "Feature",
                        "properties": {
                            "street_name": name,
                            "city": city,
                            "score_day": score_day,
                            "score_night": score_night,
                            "active_report_count": random.randint(0, 5) if base_score < 50 else random.randint(0, 1),
                            "trend": trend,
                            "escalated": base_score < 25
                        },
                        "geometry": {
                            "type": "LineString",
                            "coordinates": coords
                        }
                    }
                    all_features.append(feature)
    except Exception as e:
        print(f"Failed to fetch {city}: {str(e)}. Generating synthetic grid for {city}...")
        
        try:
            bbox_parts = bbox.split(',')
            min_lat, min_lon, max_lat, max_lon = float(bbox_parts[0]), float(bbox_parts[1]), float(bbox_parts[2]), float(bbox_parts[3])
            
            # Simple grid generator to mock OSM if server fails
            for lat_step in range(15):
                cur_lat = min_lat + (max_lat - min_lat) * (lat_step / 15)
                coords = [[min_lon, cur_lat], [max_lon, cur_lat]]
                base_score = random.randint(30, 95)
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
                
            for lon_step in range(15):
                cur_lon = min_lon + (max_lon - min_lon) * (lon_step / 15)
                coords = [[cur_lon, min_lat], [cur_lon, max_lat]]
                base_score = random.randint(30, 95)
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
        except Exception as mock_e:
            print("Failed generating mock data:", mock_e)

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
