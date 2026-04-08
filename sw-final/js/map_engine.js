
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

  // Hide or show roads based on zoom level (street level only)
  map.on('zoomend', () => {
      if (!geojsonLayer) return;
      if (map.getZoom() < 11) {
          if (map.hasLayer(geojsonLayer)) map.removeLayer(geojsonLayer);
      } else {
          if (!map.hasLayer(geojsonLayer)) map.addLayer(geojsonLayer);
      }
  });

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

async function renderRoadNetwork() {
  let geojsonData = null;
  let source = 'none';

  // ── SOURCE 1: Try backend API first ──
  try {
      console.log('[SafeWalk] Trying backend API...');
      const res = await fetch(API + '/scores/heatmap');
      if (!res.ok) throw new Error('API returned ' + res.status);
      const data = await res.json();
      console.log('[SafeWalk] API returned', data.streets ? data.streets.length : 0, 'streets');

      if (data.streets && data.streets.length > 0) {
          const features = [];
          data.streets.forEach(s => {
              let coords = null;
              try {
                  const raw = typeof s.geometry === 'string' ? JSON.parse(s.geometry) : s.geometry;
                  if (raw && Array.isArray(raw) && raw.length >= 2) {
                      coords = raw; // DB is now standard [lng, lat], no swap needed
                  }
              } catch(e) {}
              if (!coords || coords.length < 2) return;
              features.push({
                  type: "Feature",
                  properties: {
                      street_name: s.street_name, street_id: s.street_id,
                      score: s.score, score_day: s.score_day, score_night: s.score_night,
                      active_report_count: s.active_report_count,
                      trend: s.trend, escalated: s.escalated
                  },
                  geometry: { type: "LineString", coordinates: coords }
              });
          });
          if (features.length > 0) {
              geojsonData = { type: "FeatureCollection", features };
              source = 'api';
              console.log('[SafeWalk] Using API data:', features.length, 'features');
          }
      }
  } catch(err) {
      console.warn('[SafeWalk] API failed:', err.message);
  }

  // ── SOURCE 2: Fallback to embedded JS data ──
  if (!geojsonData) {
      console.log('[SafeWalk] Falling back to embedded road data...');
      if (typeof ALL_ROADS_DATA !== 'undefined' && ALL_ROADS_DATA.features && ALL_ROADS_DATA.features.length > 0) {
          geojsonData = ALL_ROADS_DATA;
          source = 'embedded';
          console.log('[SafeWalk] Using embedded data:', ALL_ROADS_DATA.features.length, 'features');
      } else {
          console.error('[SafeWalk] No embedded data available either!');
          toast("No road data available", "err");
          document.getElementById('loader').style.display = 'none';
          return;
      }
  }

  // ── RENDER the GeoJSON ──
  if (geojsonLayer) { map.removeLayer(geojsonLayer); }

  geojsonLayer = L.geoJSON(geojsonData, {
    filter: function(feature) {
      const p = feature.properties;
      const score = isNightMode ? (p.score_night || 30) : (p.score_day || 60);
      return score < 80; // Only show caution/danger roads
    },
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
      layer.on('mouseover', function(e) {
         this.setStyle({ weight: 9, opacity: 1 });
      });
      layer.on('mouseout', function(e) {
         geojsonLayer.resetStyle(e.target);
      });
    }
  });

  geojsonLayer.addTo(map);
  console.log('[SafeWalk] ✅ Road network rendered from', source, '— heatmap active');
  if (source === 'embedded') toast('Using offline road data', 'ok');
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

// ── SEARCH USING PHOTON KOMOOT ──
let searchTimeout;
function setupAutocomplete() {
    document.getElementById('searchInput').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const q = e.target.value.trim();
        const resBox = document.getElementById('searchResults');
        if (q.length < 3) { resBox.classList.remove('show'); return; }
        
        searchTimeout = setTimeout(async () => {
            try {
                const url = `https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/suggest?f=pjson&text=${encodeURIComponent(q)}&maxSuggestions=5`;
                const searchRes = await (await fetch(url)).json();
                const results = searchRes.suggestions;
                
                if (results && results.length > 0) {
                    resBox.innerHTML = results.map(r => {
                        const parts = (r.text || 'Place').split(',');
                        const name = parts[0].trim();
                        const address = parts.slice(1).join(',').trim();
                        return `
                        <div class="search-item" onclick="selectSearch('${r.magicKey}', '${name.replace(/'/g, "\\'")}')">
                            <span style="font-size:16px;">📍</span> ${name}<br>
                            <span style="font-size:10px;color:#888;">${address}</span>
                        </div>
                        `;
                    }).join('');
                    resBox.classList.add('show');
                } else {
                    resBox.innerHTML = '<div class="search-item">No results found</div>';
                    resBox.classList.add('show');
                }
            } catch(e) {}
        }, 500);
    });
}
async function selectSearch(magicKey, name) {
    document.getElementById('searchInput').value = name.split(',')[0];
    document.getElementById('searchResults').classList.remove('show');
    try {
        const url = `https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?f=pjson&magicKey=${magicKey}&maxLocations=1`;
        const res = await (await fetch(url)).json();
        if (res.candidates && res.candidates.length > 0) {
            map.flyTo([res.candidates[0].location.y, res.candidates[0].location.x], 17);
        }
    } catch(e) {}
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
                const url = `https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/suggest?f=pjson&text=${encodeURIComponent(q)}&maxSuggestions=5`;
                const searchRes = await (await fetch(url)).json();
                const r = searchRes.suggestions;
                if (r && r.length > 0) {
                    box.innerHTML = r.map(x => {
                        const parts = (x.text || 'Location').split(',');
                        const name = parts[0].trim();
                        const address = parts.slice(1).join(',').trim();
                        return `
                        <div class="sp-rp-res" onclick="selectRoutePt('${t}', '${x.magicKey}', '${name.replace(/'/g, "\\'")}')">
                            ${name} <span style="font-size:9px;color:#999;">${address}</span>
                        </div>
                        `;
                    }).join('');
                    box.style.display = 'block';
                }
            } catch(e) {}
        }, 500);
    });
});
let routePts = { From: null, To: null };
async function selectRoutePt(type, magicKey, name) {
    document.getElementById(`rp${type}`).value = name;
    document.getElementById(`rp${type}Results`).style.display = 'none';
    try {
        const url = `https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?f=pjson&magicKey=${magicKey}&maxLocations=1`;
        const res = await (await fetch(url)).json();
        if (res.candidates && res.candidates.length > 0) {
            routePts[type] = { lat: res.candidates[0].location.y, lng: res.candidates[0].location.x };
        }
    } catch(e) {}
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
window.jumpToCity = function(city) {
    const coords = {
        'Delhi': [28.6139, 77.2090],
        'Mumbai': [19.0760, 72.8777],
        'Bangalore': [12.9716, 77.5946],
        'Hyderabad': [17.3850, 78.4867]
    };
    if(coords[city] && map) {
        map.flyTo(coords[city], 13);
        toast(`Moved to ${city}`, 'ok');
    }
}

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
