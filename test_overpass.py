import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json][timeout:25];
area["name"="Delhi"]->.searchArea;
(
  way["highway"~"primary|secondary"](area.searchArea);
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
