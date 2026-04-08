// controllers/routeController.js
const db = require('../config/db');

// Haversine distance between two GPS points (in metres)
const haversine = (lat1, lng1, lat2, lng2) => {
  const R   = 6371000;
  const φ1  = lat1 * Math.PI / 180;
  const φ2  = lat2 * Math.PI / 180;
  const Δφ  = (lat2 - lat1) * Math.PI / 180;
  const Δλ  = (lng2 - lng1) * Math.PI / 180;
  const a   = Math.sin(Δφ/2)**2 + Math.cos(φ1)*Math.cos(φ2)*Math.sin(Δλ/2)**2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
};

// GET /api/route?from_lat=&from_lng=&to_lat=&to_lng=
// Returns safe route waypoints avoiding streets below threshold
const getSafeRoute = async (req, res) => {
  try {
    const { from_lat, from_lng, to_lat, to_lng, min_score = 40 } = req.query;
    if (!from_lat || !from_lng || !to_lat || !to_lng)
      return res.status(400).json({ error: 'from_lat, from_lng, to_lat, to_lng are required' });

    // Get all known streets in bounding box between from and to
    const minLat = Math.min(parseFloat(from_lat), parseFloat(to_lat)) - 0.01;
    const maxLat = Math.max(parseFloat(from_lat), parseFloat(to_lat)) + 0.01;
    const minLng = Math.min(parseFloat(from_lng), parseFloat(to_lng)) - 0.01;
    const maxLng = Math.max(parseFloat(from_lng), parseFloat(to_lng)) + 0.01;

    const [allStreets] = await db.query(
      `SELECT street_id, street_name, lat, lng, score
       FROM street_safety_scores
       WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?`,
      [minLat, maxLat, minLng, maxLng]
    );

    // Dangerous streets (avoid)
    const dangerStreets = allStreets.filter(s => s.score < parseInt(min_score));
    const safeStreets   = allStreets.filter(s => s.score >= parseInt(min_score));

    // Simple waypoint list — sort safe streets by proximity to direct line
    // In production this would use a proper routing engine (OSRM/GraphHopper)
    const directDist = haversine(
      parseFloat(from_lat), parseFloat(from_lng),
      parseFloat(to_lat),   parseFloat(to_lng)
    );

    const waypoints = [
      { lat: parseFloat(from_lat), lng: parseFloat(from_lng), label: 'Start', score: 100 },
      ...safeStreets
        .map(s => ({
          ...s,
          dist_from: haversine(parseFloat(from_lat), parseFloat(from_lng), s.lat, s.lng),
          dist_to:   haversine(s.lat, s.lng, parseFloat(to_lat), parseFloat(to_lng))
        }))
        .filter(s => s.dist_from + s.dist_to < directDist * 1.5)
        .sort((a, b) => (a.dist_from + a.dist_to) - (b.dist_from + b.dist_to))
        .slice(0, 8),
      { lat: parseFloat(to_lat), lng: parseFloat(to_lng), label: 'Destination', score: 100 }
    ];

    const avgScore = waypoints.reduce((sum, w) => sum + (w.score || 100), 0) / waypoints.length;

    // Save route to DB
    const [saved] = await db.query(
      `INSERT INTO safe_routes (user_id, from_lat, from_lng, to_lat, to_lng, route_json, avg_score)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [
        req.user.id,
        from_lat, from_lng, to_lat, to_lng,
        JSON.stringify(waypoints),
        Math.round(avgScore)
      ]
    );

    res.json({
      route_id:       saved.insertId,
      waypoints,
      avg_score:      Math.round(avgScore),
      direct_dist_m:  Math.round(directDist),
      danger_streets: dangerStreets.map(s => ({
        street_name: s.street_name, lat: s.lat, lng: s.lng, score: s.score
      })),
      safety_verdict: avgScore >= 70 ? 'safe' : avgScore >= 40 ? 'moderate' : 'dangerous'
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// GET /api/route/history — user's past routes
const getRouteHistory = async (req, res) => {
  try {
    const [rows] = await db.query(
      `SELECT id, from_name, to_name, avg_score, total_dist_m, created_at
       FROM safe_routes WHERE user_id = ? ORDER BY created_at DESC LIMIT 20`,
      [req.user.id]
    );
    res.json({ routes: rows });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

module.exports = { getSafeRoute, getRouteHistory };
