import re
import os

def split_map_html():
    with open('sw-final/pages/map.html', 'r', encoding='utf-8') as f:
        html = f.read()
        
    style_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
    css_content = style_match.group(1).strip() if style_match else ""
    
    script_match = re.search(r'<script>\nredirectIfNotAuth\(\);\n(.*?)console\.log\(''\[SafeWalk\] Time mode changed! Re-rendering\.\.\.''\);\n    toast\(nowNight \? ''🌙 Switching to Night Safety Scores'' : ''☀️ Switching to Day Safety Scores'', ''ok''\);\n    renderRoadNetwork\(\);\n  }\n\}, 60000 \* 5\);\n</script>', html, re.DOTALL)
    
    # Simpler regex logic to grab javascript if exact match fails
    if not script_match:
        script_match = re.search(r'<script>\s*redirectIfNotAuth\(\);(.*?)</script>', html, re.DOTALL)
        
    js_content = script_match.group(1).strip() if script_match else ""
    js_content = "redirectIfNotAuth();\n" + js_content

    # Clean HTML
    clean_html = re.sub(r'<style>.*?</style>', '<link rel="stylesheet" href="../css/map.css">', html, flags=re.DOTALL)
    clean_html = re.sub(r'<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>', '<!-- Map Scripts -->', clean_html)
    clean_html = re.sub(r'<script>\s*redirectIfNotAuth\(\);.*?</script>', '<script src="../js/map_engine.js"></script>', clean_html, flags=re.DOTALL)
    
    # Setup directories
    os.makedirs('sw-final/css', exist_ok=True)
    os.makedirs('sw-final/js', exist_ok=True)
    
    # Write components
    with open('sw-final/css/map.css', 'w', encoding='utf-8') as f: f.write(css_content)
    with open('sw-final/js/map_engine.js', 'w', encoding='utf-8') as f: f.write(js_content)
    with open('sw-final/pages/map.html', 'w', encoding='utf-8') as f: f.write(clean_html)
    print("Successfully split map.html into css, html, and js!")

if __name__ == '__main__':
    split_map_html()
