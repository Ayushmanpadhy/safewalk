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
        features.append({
            "type": "Feature",
            "properties": {
                "street_name": r['street_name'],
                "street_id": r['street_id'],
                "score": r['score'],
                "score_day": r['score_day'],
                "score_night": r['score_night'],
                "active_report_count": r['active_report_count'],
                "trend": r['trend'],
                "escalated": r['escalated']
            },
            "geometry": {
                "type": "LineString",
                "coordinates": geom # It's [lng, lat]
            }
        })

geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open("d:/SAFEWALK/sw-final/js/indian_roads.js", "w", encoding="utf-8") as f:
    f.write("const ALL_ROADS_DATA = ")
    json.dump(geojson, f, ensure_ascii=False)
    f.write(";\n")

print(f"Dumped {len(features)} rows to indian_roads.js")
