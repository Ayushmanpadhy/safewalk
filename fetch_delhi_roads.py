import urllib.request
import json
import random
import os

# Define Bounding Box covering central/south Delhi
bbox = "28.50,77.10,28.68,77.30"

overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = f"""
[out:json][timeout:25];
(
  way["highway"~"primary"]({bbox});
);
out geom;
"""

def generate():
    print("Fetching road network from Overpass API (this may take 15 seconds)...")
    req = urllib.request.Request(overpass_url, data=overpass_query.encode('utf-8'))
    
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode('utf-8'))
    
    print(f"Downloaded {len(data['elements'])} road segments! Processing into GeoJSON...")

    features = []
    
    for element in data['elements']:
        if element['type'] == 'way' and 'geometry' in element:
            coords = []
            for point in element['geometry']:
                coords.append([point['lon'], point['lat']])
                
            tags = element.get('tags', {})
            name = tags.get('name', 'Unnamed Road')
            
            # Generate random safety scores based on logic
            # Central/South Delhi generally safer, but let's just make it random between 20 and 95
            base_score = random.randint(30, 95)
            
            # 10% chance to be a very dangerous road
            if random.random() < 0.1:
                base_score = random.randint(10, 30)
                
            score_day = min(100, base_score + random.randint(5, 15))
            score_night = max(0, base_score - random.randint(20, 35))
            
            # Assign trend
            trend = "stable"
            if base_score < 40: trend = random.choice(["worsening", "stable"])
            elif base_score > 75: trend = random.choice(["improving", "stable"])

            feature = {
                "type": "Feature",
                "properties": {
                    "name": name,
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
            features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    # Write as a JS file so it can be easily loaded locally without CORS issues
    output_path = os.path.join(os.path.dirname(__file__), "sw-final", "js", "delhi_roads.js")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("const DELHI_ROAD_NETWORK = ")
        json.dump(geojson, f, ensure_ascii=False)
        f.write(";\n")
        
    print(f"Successfully generated full geometric road network: {output_path}")

if __name__ == "__main__":
    generate()
