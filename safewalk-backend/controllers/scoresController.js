// controllers/scoresController.js
const db = require('../config/db');

// GET /api/scores — heatmap data (all streets with scores)
const getHeatmap = async (req, res) => {
  try {
    const [rows] = await db.query(
      `SELECT street_id, street_name, lat, lng, score,
              score_day, score_night, active_report_count,
              trend, escalated, last_updated
       FROM street_safety_scores
       ORDER BY score ASC`
    );
    res.json({ streets: rows, count: rows.length, generated_at: new Date() });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// GET /api/scores/:streetId — single street details
const getStreetScore = async (req, res) => {
  try {
    const [scores] = await db.query(
      'SELECT * FROM street_safety_scores WHERE street_id = ?',
      [req.params.streetId]
    );
    if (!scores.length)
      return res.status(404).json({ error: 'Street not found' });

    // Also fetch recent active reports for this street
    const [reports] = await db.query(
      `SELECT id, incident_type, severity, description, photo_url,
              anonymous, reported_at
       FROM reports
       WHERE street_id = ? AND resolved = 0
       ORDER BY reported_at DESC LIMIT 10`,
      [req.params.streetId]
    );

    // 24-hour history
    const [history] = await db.query(
      `SELECT score, hour_time, recorded_at
       FROM score_history
       WHERE street_id = ?
       ORDER BY recorded_at DESC LIMIT 24`,
      [req.params.streetId]
    );

    res.json({
      street:  scores[0],
      reports,
      history
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// GET /api/scores/nearby?lat=&lng=&radius=500
const getNearbyScores = async (req, res) => {
  try {
    const { lat, lng, radius = 500 } = req.query;
    if (!lat || !lng)
      return res.status(400).json({ error: 'lat and lng are required' });

    // Haversine approximation filter using bounding box first
    const latDelta = parseFloat(radius) / 111320;
    const lngDelta = parseFloat(radius) / (111320 * Math.cos(parseFloat(lat) * Math.PI / 180));

    const [rows] = await db.query(
      `SELECT street_id, street_name, lat, lng, score, trend, escalated
       FROM street_safety_scores
       WHERE lat BETWEEN ? AND ?
         AND lng BETWEEN ? AND ?
       ORDER BY score ASC`,
      [
        parseFloat(lat) - latDelta, parseFloat(lat) + latDelta,
        parseFloat(lng) - lngDelta, parseFloat(lng) + lngDelta
      ]
    );
    res.json({ streets: rows, count: rows.length });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

module.exports = { getHeatmap, getStreetScore, getNearbyScores };
