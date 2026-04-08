import mysql.connector
import json

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root123", # From db.js
    database="safewalk"
)

cursor = db.cursor(dictionary=True)
cursor.execute("SELECT * FROM street_safety_scores")
rows = cursor.fetchall()

features = []
for r in rows:
    if r['geometry']:
        geom = json.loads(r['geometry'])
        
        # If geometry is [lat, lng], parse to [lng, lat] for geojson
        # Wait, the DB stores whatever we gave it. 
        # In my python script, `coords = [[cur_lng, cur_lat]]`... Oh wait!
        # In `generate_massive_sql.py` I did:
        # coords.append([cur_lng, cur_lat])
        # avg_lat = round(lat_sum / len(coords), 6) -> `lat_sum` added `point['lat']`
        # Wait, earlier I decided to put [lng, lat] strictly in DB.
        
        # Let's check `generate_massive_sql.py`.
        # I did: `coords.append([cur_lng, cur_lat])`
        # the frontend `map_engine.js` does:
        # const raw = JSON.parse(s.geometry);
        # coords = raw.map(c => [c[1], c[0]]); // DB [lat,lng] -> GeoJSON [lng,lat]
        # BUT wait! If I stored [lng, lat] in DB, and the frontend swaps it to [lat, lng], leaflet will crash or render in the ocean!

        # Let's verify `generate_massive_sql.py` precisely.
