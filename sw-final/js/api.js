// js/api.js — SafeWalk shared helpers
const isFile = window.location.protocol === 'file:';
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const BACKEND_URL = window.swEnv?.API_URL || (isFile || isLocal ? 'http://localhost:5000' : '');
const API = `${BACKEND_URL}/api`;
window.API_BASE = BACKEND_URL;

const getToken     = ()     => localStorage.getItem('sw_token');
const getUser = () => { try { return JSON.parse(localStorage.getItem('sw_user') || 'null'); } catch(e) { return null; } };
const saveSession  = (d)    => { localStorage.setItem('sw_token', d.token); localStorage.setItem('sw_user', JSON.stringify(d.user)); };
const clearSession = ()     => { localStorage.removeItem('sw_token'); localStorage.removeItem('sw_user'); };
const isLoggedIn   = ()     => !!getToken();
const redirectIfNotAuth = () => { if (!isLoggedIn()) window.location.href = 'login.html'; };

async function apiFetch(path, opts = {}) {
  const headers = { ...(opts.headers || {}) };
  if (getToken()) headers['Authorization'] = 'Bearer ' + getToken();
  if (!(opts.body instanceof FormData)) headers['Content-Type'] = 'application/json';
  const res  = await fetch(API + path, { ...opts, headers });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Request failed');
  return data;
}

function scoreColor(s) {
  if (s >= 80) return '#0D9E5C';
  if (s >= 55) return '#D97706';
  if (s >= 30) return '#DC4E12';
  return '#C41717';
}
function scoreBg(s) {
  if (s >= 80) return 'rgba(13,158,92,.1)';
  if (s >= 55) return 'rgba(217,119,6,.1)';
  if (s >= 30) return 'rgba(220,78,18,.1)';
  return 'rgba(196,23,23,.1)';
}
function scoreLabel(s) {
  if (s >= 80) return 'Very Safe';
  if (s >= 55) return 'Moderate';
  if (s >= 30) return 'Caution';
  return 'Danger Zone';
}

function showToast(msg, type = '') {
  let t = document.getElementById('sw-toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'sw-toast';
    document.body.appendChild(t);
    Object.assign(t.style, {
      position: 'fixed', bottom: '80px', left: '50%',
      transform: 'translateX(-50%) translateY(12px)',
      padding: '10px 20px', borderRadius: '10px',
      fontSize: '13px', fontWeight: '500', zIndex: '9999',
      opacity: '0', transition: 'all .22s', pointerEvents: 'none',
      whiteSpace: 'nowrap', fontFamily: 'Inter, sans-serif',
      boxShadow: '0 4px 20px rgba(0,0,0,.15)'
    });
  }
  t.textContent = msg;
  t.style.background = type === 'ok'  ? '#0D9E5C' :
                        type === 'err' ? '#C41717' : '#1f2937';
  t.style.color = '#fff';
  requestAnimationFrame(() => { t.style.opacity = '1'; t.style.transform = 'translateX(-50%) translateY(0)'; });
  clearTimeout(t._t);
  t._t = setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(-50%) translateY(12px)'; }, 3200);
}

async function geocodePlace(q) {
  try {
    const r = await fetch(
      `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(q)}&format=json&limit=1`,
      { headers: { 'Accept-Language': 'en' } }
    );
    const d = await r.json();
    if (d.length) return { lat: parseFloat(d[0].lat), lng: parseFloat(d[0].lon), name: d[0].display_name.split(',')[0] };
  } catch (e) {}
  return null;
}
