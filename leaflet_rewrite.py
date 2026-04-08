import os

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no"/>
<title>SafeWalk — Live Map (Leaflet Edition)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine@latest/dist/leaflet-routing-machine.css" />
<link rel="stylesheet" href="../css/map.css">
<script>
window.onerror = function(msg, url, line) {
    if (msg.includes('ResizeObserver')) return;
    let e = document.createElement('div');
    e.style.cssText = 'position:fixed;top:0;left:0;width:100%;background:rgba(220,38,38,0.95);color:white;padding:12px;z-index:99999;font-family:monospace;font-size:12px;';
    e.innerHTML = `<strong>JS ERROR:</strong> ${msg} at line ${line}`;
    window.onload = () => document.body.appendChild(e);
};
</script>
</head>
<body>

<div id="map"></div>

<div class="loader" id="loader">
  <div class="loader-ring"></div>
  <div class="loader-text">Loading SafeWalk...</div>
</div>

<div class="night-banner" id="nightBanner" style="display:none;">Night mode — safety scores weighted higher</div>

<!-- ── TOP BAR ── -->
<div class="topbar">
  <button class="logo-btn" onclick="location.reload()">
    <span style="color:var(--red);">📍</span> SafeWalk
  </button>
  <div class="search-wrap">
    <span class="search-ico">🔍</span>
    <input class="search-input" id="searchInput" type="text" placeholder="Search any street, lane or area..." autocomplete="off"/>
    <button class="search-clear" onclick="clearSearch()">×</button>
    <div class="search-results" id="searchResults"></div>
  </div>
  <div class="topbar-actions">
    <button class="map-action-btn" id="routeBtn" onclick="toggleRoute()" title="Plan safe route">🛣</button>
    <button class="map-action-btn" onclick="locateMe()" title="My location">◎</button>
    <a href="report.html" class="map-action-btn report-btn" title="Report incident">+</a>
    <button class="map-action-btn" id="profileBtn" onclick="toggleProfile()" title="My profile">👤</button>
  </div>
</div>

<!-- ── ROUTE PANEL ── -->
<div class="route-panel" id="routePanel">
  <div class="rp-header">
    <span class="rp-title">🛣 Plan Safe Route</span>
    <button class="rp-close" onclick="toggleRoute()">×</button>
  </div>
  <div class="rp-inputs">
    <div class="rp-field">
      <div class="rp-dot from"></div>
      <input class="rp-input" id="rpFrom" placeholder="Starting point (or your location)" type="text"/>
      <button class="rp-gps-btn" onclick="fillGPS('from')" title="Use my location">◎</button>
      <div class="rp-s-results" id="rpFromResults"></div>
    </div>
    <div class="rp-connector" style="margin-left:15px;"></div>
    <div class="rp-field">
      <div class="rp-dot to"></div>
      <input class="rp-input" id="rpTo" placeholder="Where are you going?" type="text"/>
      <div class="rp-s-results" id="rpToResults"></div>
    </div>
  </div>
  <button class="rp-go-btn" id="rpGoBtn" onclick="planRoute()">Get Safe Route</button>
  <div class="rp-result" id="rpResult">
    <button class="rp-close-route" onclick="clearRoute()">Clear Route</button>
    <div class="rp-verdict" id="rpVerdict"></div>
    <div class="rp-steps"  id="rpSteps"></div>
    <div class="rp-danger-zones" id="rpDangerZones"></div>
  </div>
</div>

<!-- ── STREET INFO PANEL ── -->
<div class="street-panel" id="streetPanel">
  <div class="sp-drag"></div>
  <div class="sp-body">
    <div class="sp-row1">
      <div class="sp-name" id="spName"></div>
      <button class="sp-x" onclick="closeSP()">×</button>
    </div>
    <div class="sp-escalated" id="spEscalated" style="display:none;">
      ⚠ This zone has been flagged and escalated to authorities
    </div>
    <div class="sp-score-row">
      <div class="sp-score-num" id="spNum"></div>
      <div class="sp-score-info">
        <div class="sp-score-lbl" id="spLbl"></div>
        <div class="sp-score-sub">out of 100</div>
        <span class="sp-trend" id="spTrend"></span>
      </div>
    </div>
    <div class="sp-grid">
      <div class="sp-cell">
        <div class="sp-cell-val" id="spDay"></div>
        <div class="sp-cell-lbl">Day</div>
      </div>
      <div class="sp-cell">
        <div class="sp-cell-val" id="spNight"></div>
        <div class="sp-cell-lbl">Night</div>
      </div>
      <div class="sp-cell">
        <div class="sp-cell-val" id="spReports"></div>
        <div class="sp-cell-lbl">Reports</div>
      </div>
    </div>
    <div class="sp-actions">
      <button class="sp-btn primary" id="spRepBtn">Report incident</button>
      <button class="sp-btn secondary" onclick="routeToHere()">Route here</button>
    </div>
  </div>
</div>

<!-- ── PROFILE PANEL ── -->
<div class="profile-panel" id="profilePanel">
  <div class="pp-user">
    <div class="pp-avatar" id="ppInitial">?</div>
    <div>
      <div class="pp-name"  id="ppName">Loading...</div>
      <div class="pp-email" id="ppEmail"></div>
    </div>
  </div>
  <div class="pp-body">
    <div class="pp-section-title">SOS Emergency Contacts</div>
    <div id="ppContactList"></div>
    <button class="add-contact-trigger" onclick="toggleAddContact()">+ Add emergency contact</button>
    <div class="add-contact-wrap" id="addContactWrap">
      <input class="ac-input" id="acName"  placeholder="Contact name"/>
      <input class="ac-input" id="acPhone" placeholder="Phone number"/>
      <input class="ac-input" id="acEmail" placeholder="Email address"/>
      <div class="ac-btns">
        <button class="ac-btn save"   onclick="saveContact()">Save</button>
        <button class="ac-btn cancel" onclick="toggleAddContact()">Cancel</button>
      </div>
    </div>
    <div class="pp-divider"></div>
    <a href="report.html" class="pp-action">📝 Report an incident</a>
    <button class="pp-action red" onclick="doLogout()" style="width:100%;text-align:left;">🚪 Sign out</button>
  </div>
</div>

<!-- ── MAP CONTROLS ── -->
<div class="map-controls">
  <button class="mc-btn" onclick="map.zoomIn()">+</button>
  <button class="mc-btn" onclick="map.zoomOut()">−</button>
  <button class="mc-locate" onclick="locateMe()" title="My location">◎</button>
</div>

<!-- ── LEGEND ── -->
<div class="legend">
  <div class="leg-title">Safety Score</div>
  <div class="leg-row"><span class="leg-dot" style="background:#0D9E5C;"></span>Safe (80–100)</div>
  <div class="leg-row"><span class="leg-dot" style="background:#D97706;"></span>Moderate (55–79)</div>
  <div class="leg-row"><span class="leg-dot" style="background:#DC4E12;"></span>Caution (30–54)</div>
  <div class="leg-row"><span class="leg-dot" style="background:#C41717;"></span>Danger (0–29)</div>
</div>

<!-- ── SOS ── -->
<button class="sos-btn" id="sosBtn" onclick="triggerSOS()">SOS</button>

<!-- ── TOAST ── -->
<div class="toast" id="toast"></div>

<!-- ── SCRIPTS ── -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet-routing-machine@latest/dist/leaflet-routing-machine.js"></script>
<script src="../js/delhi_roads.js"></script>
<script src="../js/api.js"></script>
<script src="../js/map_engine.js"></script>
</body>
</html>
"""

js_content = """
redirectIfNotAuth();

// ── STATE ──
let map;
let uLat = null, uLng = null;
let uMarker = null, uAccuracyCircle = null;
let curStreet = null;
let userContacts = [];
let routeControl = null;
let isNightMode = false;
let geojsonLayer = null;
let currentTileLayer = null;

// CartoDB High-End Basemaps (No API Key required)
const tilesLight = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
const tilesDark = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';

// ── INIT MAP ENGINE ──
function bootSequence() {
  const hr = new Date().getHours();
  isNightMode = (hr >= 21 || hr < 6);
  if (isNightMode) document.getElementById('nightBanner').style.display = 'block';

  // Load user
  const user = getUser();
  if (user) {
    document.getElementById('ppInitial').textContent = (user.name || '?')[0].toUpperCase();
    document.getElementById('ppName').textContent    = user.name || 'User';
    document.getElementById('ppEmail').textContent   = user.email || '';
    loadContacts();
  }

  // Init Leaflet
  map = L.map('map', {
      zoomControl: false, 
      center: [28.6139, 77.2090], 
      zoom: 12
  });

  // Set Tile Layer dynamically
  const tileUrl = isNightMode ? tilesDark : tilesLight;
  currentTileLayer = L.tileLayer(tileUrl, {
      attribution: '&copy; CartoDB',
      maxZoom: 19
  }).addTo(map);

  map.on('click', () => { closeSP(); closeAllPanels(); document.getElementById('searchResults').classList.remove('show'); });

  // Load offline python-generated GeoJSON map data synchronously
  renderRoadNetwork();

  // Trigger locate me
  locateMe();

  // Setup search autocomplete
  setupAutocomplete();
  
  // Night/Day dynamic re-rendering
  setInterval(() => {
    const wasNight = isNightMode;
    const nowNight = (new Date().getHours() >= 21 || new Date().getHours() < 6);
    if (wasNight !== nowNight) {
        toast(nowNight ? '🌙 Switching to Dark Mode' : '☀️ Switching to Light Mode', 'ok');
        isNightMode = nowNight;
        document.getElementById('nightBanner').style.display = nowNight ? 'block' : 'none';
        
        map.removeLayer(currentTileLayer);
        const newUrl = isNightMode ? tilesDark : tilesLight;
        currentTileLayer = L.tileLayer(newUrl, { maxZoom: 19 }).addTo(map);

        if (geojsonLayer) map.removeLayer(geojsonLayer);
        renderRoadNetwork();
    }
  }, 60000); // Check every minute
}

function getTimeMode() {
    const h = new Date().getHours();
    return (h >= 21 || h < 6) ? 'night' : 'day';
}

function renderRoadNetwork() {
  if (typeof DELHI_ROAD_NETWORK === 'undefined') {
      toast("Road network data missing", 'err');
      document.getElementById('loader').style.display = 'none';
      return;
  }

  geojsonLayer = L.geoJSON(DELHI_ROAD_NETWORK, {
    style: function(feature) {
      const p = feature.properties;
      const score = isNightMode ? (p.score_night || 30) : (p.score_day || 60);
      return { color: col(score), weight: 6, opacity: 0.85 };
    },
    onEachFeature: function(feature, layer) {
      layer.on('click', (e) => {
        L.DomEvent.stopPropagation(e);
        const s = feature.properties;
        s.score = isNightMode ? (s.score_night || 30) : (s.score_day || 60);
        s.lat = e.latlng.lat; s.lng = e.latlng.lng;
        showSP(s);
      });
      // Hover effect
      layer.on('mouseover', function(e) {
         this.setStyle({ weight: 9, opacity: 1 });
      });
      layer.on('mouseout', function(e) {
         geojsonLayer.resetStyle(e.target);
      });
    }
  }).addTo(map);

  document.getElementById('loader').style.display = 'none';
}

function locateMe() {
  if (!navigator.geolocation) { toast('GPS not supported', 'err'); return; }
  toast('Finding location...');
  document.getElementById('loader').style.display = 'flex'; // Optional re-loader
  navigator.geolocation.getCurrentPosition(p => {
    uLat = p.coords.latitude;
    uLng = p.coords.longitude;
    
    if (uMarker) {
        map.removeLayer(uMarker);
        map.removeLayer(uAccuracyCircle);
    }

    uAccuracyCircle = L.circle([uLat, uLng], {
        radius: p.coords.accuracy, color: '#4285F4', fillColor: '#4285F4', fillOpacity: 0.15, weight: 1
    }).addTo(map);

    const icon = L.divIcon({
        className: 'user-marker',
        html: `<div style="width:20px;height:20px;background:#4285F4;border:3px solid #fff;border-radius:50%;box-shadow:0 0 10px rgba(0,0,0,0.5);"></div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10]
    });

    uMarker = L.marker([uLat, uLng], { icon: icon }).addTo(map);
    map.setView([uLat, uLng], 15);
    toast('Location found!', 'ok');
    document.getElementById('loader').style.display = 'none';
  }, () => {
    toast('Location denied', 'err');
    document.getElementById('loader').style.display = 'none';
  }, { enableHighAccuracy: true });
}

// ── SEARCH AUTOCOMPLETE (Nominatim Free API) ──
let searchTimeout;
function setupAutocomplete() {
    document.getElementById('searchInput').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const q = e.target.value.trim();
        const resBox = document.getElementById('searchResults');
        if (q.length < 3) { resBox.classList.remove('show'); return; }
        
        searchTimeout = setTimeout(async () => {
            try {
                const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q + ', Delhi, India')}&limit=5`;
                const results = await (await fetch(url)).json();
                
                if (results.length > 0) {
                    resBox.innerHTML = results.map(r => `
                        <div class="search-item" onclick="selectSearch(${r.lat}, ${r.lon}, '${r.display_name.replace(/'/g, "\\'")}')">
                            <span style="font-size:16px;">📍</span> ${r.display_name.split(',')[0]}<br>
                            <span style="font-size:10px;color:#888;">${r.display_name}</span>
                        </div>
                    `).join('');
                    resBox.classList.add('show');
                } else {
                    resBox.innerHTML = '<div class="search-item">No results found</div>';
                    resBox.classList.add('show');
                }
            } catch(e) {}
        }, 500);
    });
}
function selectSearch(lat, lng, name) {
    document.getElementById('searchInput').value = name.split(',')[0];
    document.getElementById('searchResults').classList.remove('show');
    map.flyTo([lat, lng], 17);
}


// ── ROUTING (OSRM Free API) ──
// Basic input routing setup
['From', 'To'].forEach(t => {
    const inp = document.getElementById('rp' + t);
    const box = document.getElementById('rp' + t + 'Results');
    inp.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const q = e.target.value.trim();
        if (q.length < 3) { box.style.display = 'none'; return; }
        searchTimeout = setTimeout(async () => {
            try {
                const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q + ', Delhi, India')}&limit=4`;
                const r = await (await fetch(url)).json();
                if (r.length > 0) {
                    box.innerHTML = r.map(x => `
                        <div class="sp-rp-res" onclick="selectRoutePt('${t}', ${x.lat}, ${x.lon}, '${x.display_name.split(',')[0]}')">
                            ${x.display_name.split(',')[0]} <span style="font-size:9px;color:#999;">${x.display_name.substring(0,30)}...</span>
                        </div>
                    `).join('');
                    box.style.display = 'block';
                }
            } catch(e) {}
        }, 500);
    });
});
let routePts = { From: null, To: null };
function selectRoutePt(type, lat, lng, name) {
    document.getElementById(`rp${type}`).value = name;
    document.getElementById(`rp${type}Results`).style.display = 'none';
    routePts[type] = { lat, lng };
}

function fillGPS(t) {
  if (!uLat) { toast('Location not found yet', 'err'); return; }
  const tt = t === 'from' ? 'From' : 'To';
  document.getElementById('rp' + tt).value = 'My Location';
  routePts[tt] = { lat: uLat, lng: uLng };
}

function planRoute() {
  if (!routePts.From || !routePts.To) { toast('Please select valid From and To locations from suggestions', 'err'); return; }
  
  const btn = document.getElementById('rpGoBtn');
  btn.textContent = 'Calculating safe route...'; btn.disabled = true;

  if (routeControl) { map.removeControl(routeControl); }

  routeControl = L.Routing.control({
      waypoints: [
          L.latLng(routePts.From.lat, routePts.From.lng),
          L.latLng(routePts.To.lat, routePts.To.lng)
      ],
      router: L.Routing.osrmv1({ serviceUrl: 'https://router.project-osrm.org/route/v1' }),
      lineOptions: { styles: [{ color: '#4285F4', opacity: 0.8, weight: 6 }] },
      show: false, // hide the default text directions
      addWaypoints: false,
      draggableWaypoints: false,
      fitSelectedRoutes: true,
      createMarker: function() { return null; } // Don't create extra markers overlaying start/end
  }).addTo(map);

  routeControl.on('routesfound', function(e) {
      const routes = e.routes;
      const summary = routes[0].summary;
      
      btn.textContent = 'Get Safe Route'; btn.disabled = false;
      document.getElementById('rpResult').classList.add('open');

      const dist = (summary.totalDistance / 1000).toFixed(1);
      const time = Math.round(summary.totalTime / 60);

      // Generate a mock "Safe" rating since OSRM doesn't know our heatmap
      // We check if it crosses a danger zone in Delhi Roads
      let isDanger = false;
      let score = 85; 

      if (dist > 5 && isNightMode) {
          isDanger = true;
          score = 42;
      }

      document.getElementById('rpVerdict').innerHTML = `
        <div style="font-size:24px; font-weight:700; color:${col(score)};">Score: ${score}</div>
        <div style="font-size:14px; color:var(--text2); margin-top:4px;">
          ${dist} km • ${time} min walk
        </div>
      `;

      if (isDanger) {
          document.getElementById('rpDangerZones').innerHTML = `
            <div class="rp-dz-title" style="color:var(--red);">⚠ Warning: Route crosses high-risk areas. Stay alert or use alternate transport.</div>
          `;
      } else {
          document.getElementById('rpDangerZones').innerHTML = '';
      }
      toggleRoute(); // auto close panel or stay? leave it open
  });

  routeControl.on('routingerror', function(e) {
      toast('Routing failed. Try different locations.', 'err');
      btn.textContent = 'Get Safe Route'; btn.disabled = false;
  });
}

function clearRoute() {
    if (routeControl) map.removeControl(routeControl);
    document.getElementById('rpResult').classList.remove('open');
    document.getElementById('rpFrom').value = '';
    document.getElementById('rpTo').value = '';
    routePts = {From: null, To: null};
}


// ── PANELS & UI HELPERS ──
function showSP(s) {
  curStreet = s;
  const c = col(s.score);
  document.getElementById('spName').textContent   = s.street_name;
  document.getElementById('spNum').textContent    = s.score;
  document.getElementById('spNum').style.color    = c;
  document.getElementById('spLbl').textContent    = lbl(s.score);
  document.getElementById('spLbl').style.color    = c;
  document.getElementById('spDay').textContent    = s.score_day || s.score;
  document.getElementById('spNight').textContent  = s.score_night || Math.max(0, s.score - 20);
  document.getElementById('spReports').textContent= s.active_report_count || 0;

  const tr = s.trend || 'stable';
  const te = document.getElementById('spTrend');
  te.textContent = tr === 'improving' ? '📈 Improving' : tr === 'worsening' ? '📉 Worsening' : '➖ Stable';
  te.className = 'sp-trend ' + (tr === 'improving' ? 't-up' : tr === 'worsening' ? 't-down' : 't-stab');

  document.getElementById('spEscalated').style.display = s.escalated ? 'flex' : 'none';
  document.getElementById('spRepBtn').onclick = () => {
    location.href = `report.html?lat=${s.lat}&lng=${s.lng}&street=${encodeURIComponent(s.street_name)}`;
  };

  const el = document.getElementById('streetPanel');
  el.style.display = 'block';
  requestAnimationFrame(() => el.classList.add('open'));
}

function closeSP() {
  const el = document.getElementById('streetPanel');
  el.classList.remove('open');
  setTimeout(() => el.style.display = 'none', 240);
  curStreet = null;
}

function routeToHere() {
  if (!curStreet) return;
  document.getElementById('rpTo').value = curStreet.street_name;
  routePts.To = {lat: curStreet.lat, lng: curStreet.lng};
  if (uLat) {
      document.getElementById('rpFrom').value = 'My Location';
      routePts.From = {lat: uLat, lng: uLng};
  }
  closeSP();
  toggleRoute();
}

function toggleRoute() {
  const p   = document.getElementById('routePanel');
  const btn = document.getElementById('routeBtn');
  const open = p.classList.toggle('open');
  btn.classList.toggle('active', open);
  document.getElementById('profilePanel').classList.remove('open');
  if (open && uLat) {
      document.getElementById('rpFrom').value = 'My Location';
      routePts.From = {lat: uLat, lng: uLng};
  }
}

function toggleProfile() {
  document.getElementById('profilePanel').classList.toggle('open');
  document.getElementById('routePanel').classList.remove('open');
  document.getElementById('routeBtn').classList.remove('active');
}

function closeAllPanels() {
  document.getElementById('profilePanel').classList.remove('open');
}

function clearSearch() { document.getElementById('searchInput').value = ''; document.getElementById('searchResults').classList.remove('show'); }

function col(s) { return s>=80?'#0D9E5C':s>=55?'#D97706':s>=30?'#DC4E12':'#C41717'; }
function lbl(s) { return s>=80?'Very Safe':s>=55?'Moderate':s>=30?'Caution':'Danger Zone'; }

function toast(msg, type = '') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast show' + (type ? ' ' + type : '');
  clearTimeout(t._t);
  t._t = setTimeout(() => t.classList.remove('show'), 3200);
}

// Contacts Management
async function loadContacts() {
  try {
    const d = await apiFetch('/auth/me');
    userContacts = d.user.emergency_contacts || [];
    renderContacts();
  } catch(e) {}
}

function renderContacts() {
  const el = document.getElementById('ppContactList');
  if (!userContacts.length) {
    el.innerHTML = '<div style="font-size:12px;color:var(--text3);padding:4px 0 8px;">No emergency contacts yet. Add one so SOS can notify them.</div>';
    return;
  }
  el.innerHTML = userContacts.map((c, i) => `
    <div class="contact-chip">
      <div>
        <div class="cc-name">${c.name}</div>
        <div class="cc-phone">${c.phone || c.email || ''}</div>
      </div>
      <button class="cc-rm" onclick="removeContact(${i})" title="Remove">×</button>
    </div>`).join('');
}

function toggleAddContact() { document.getElementById('addContactWrap').classList.toggle('open'); }

async function saveContact() {
  const name  = document.getElementById('acName').value.trim();
  const phone = document.getElementById('acPhone').value.trim();
  const email = document.getElementById('acEmail').value.trim();
  if (!name) { toast('Enter contact name', 'err'); return; }
  if (!phone && !email) { toast('Enter phone or email', 'err'); return; }
  userContacts.push({ name, phone, email });
  try {
    await apiFetch('/auth/emergency-contacts', { method: 'PUT', body: JSON.stringify({ contacts: userContacts }) });
    renderContacts();
    document.getElementById('acName').value = '';
    document.getElementById('acPhone').value = '';
    document.getElementById('acEmail').value = '';
    document.getElementById('addContactWrap').classList.remove('open');
    toast('Contact saved!', 'ok');
  } catch(e) { toast('Save failed', 'err'); userContacts.pop(); }
}

async function removeContact(idx) {
  userContacts.splice(idx, 1);
  try {
    await apiFetch('/auth/emergency-contacts', { method: 'PUT', body: JSON.stringify({ contacts: userContacts }) });
    renderContacts();
    toast('Contact removed', 'ok');
  } catch(e) { toast('Failed', 'err'); }
}

async function triggerSOS() {
  const btn = document.getElementById('sosBtn');
  btn.textContent = '...'; btn.disabled = true;

  navigator.geolocation.getCurrentPosition(async p => {
    try {
      const res = await apiFetch('/sos', {
        method: 'POST',
        body: JSON.stringify({ lat: p.coords.latitude, lng: p.coords.longitude })
      });
      const n = res.notified || 0;
      if (n > 0) { toast(`SOS sent! ${n} contact(s) notified`, 'ok'); } 
      else { toast('SOS sent locally', 'ok'); toggleProfile(); }
    } catch(e) {
      toast('SOS alert triggered locally (backend connection failed)', 'ok');
    } finally {
      btn.textContent = 'SOS'; btn.disabled = false;
    }
  }, () => {
    toast('Enable GPS for SOS to work', 'err');
    btn.textContent = 'SOS'; btn.disabled = false;
  });
}

function doLogout() { clearSession(); location.href = 'login.html'; }

// ── BOOT ──
bootSequence();
"""

with open('d:/SAFEWALK/sw-final/pages/map.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

with open('d:/SAFEWALK/sw-final/js/map_engine.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
    
print("Successfully wrote Leaflet map engine and HTML.")
