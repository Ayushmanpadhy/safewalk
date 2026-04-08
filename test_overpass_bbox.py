import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

overpass_url = "http://overpass-api.de/api/interpreter"
# Bounding box for Central Delhi (South, West, North, East)
# 28.5, 77.1, 28.7, 77.3
overpass_query = """
[out:json][timeout:25];
(
  way["highway"~"primary|secondary"](28.5, 77.1, 28.7, 77.3);
);
out geom;
"""

try:
    req = urllib.request.Request(overpass_url, data=overpass_query.encode('utf-8'))
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode('utf-8'))
        print("Got data! Elements:", len(data['elements']))
except Exception as e:
    print("Failed:", e)
