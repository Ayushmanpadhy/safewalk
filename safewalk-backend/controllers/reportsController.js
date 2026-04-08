// controllers/reportsController.js
const db = require('../config/db');

// Helper — derive a street_id from lat/lng (rounded to ~100m grid)
const makeStreetId = (lat, lng) => {
  const rLat = Math.round(parseFloat(lat) * 1000) / 1000;
  const rLng = Math.round(parseFloat(lng) * 1000) / 1000;
  return `${rLat}_${rLng}`;
};

// Severity map per incident type
const SEVERITY_MAP = {
  poor_lighting:     2,
  suspicious_person: 3,
  harassment:        4,
  assault:           5,
  eve_teasing:       4,
  theft_robbery:     4,
  drunk_crowd:       2,
  broken_cctv:       1,
  isolated_road:     2,
  general_unsafe:    2
};

// POST /api/reports — submit an incident
const createReport = async (req, res) => {
  try {
    const { lat, lng, street_name, incident_type, description, anonymous } = req.body;
    if (!lat || !lng || !street_name || !incident_type)
      return res.status(400).json({ error: 'lat, lng, street_name, incident_type are required' });

    const street_id = makeStreetId(lat, lng);
    const severity  = SEVERITY_MAP[incident_type] || 2;
    const photo_url = req.file ? `/uploads/${req.file.filename}` : null;

    const [result] = await db.query(
      `INSERT INTO reports
        (user_id, lat, lng, street_name, street_id, incident_type, severity, description, photo_url, anonymous)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [req.user.id, lat, lng, street_name, street_id, incident_type,
       severity, description || null, photo_url, anonymous === 'true' ? 1 : 0]
    );

    // Upsert street into street_safety_scores if not exists
    await db.query(
      `INSERT INTO street_safety_scores (street_id, street_name, lat, lng)
       VALUES (?, ?, ?, ?)
       ON DUPLICATE KEY UPDATE street_name = VALUES(street_name)`,
      [street_id, street_name, lat, lng]
    );

    res.status(201).json({
      message: 'Report submitted. Score will update in next hourly cycle.',
      report_id: result.insertId,
      street_id
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// GET /api/reports — get recent reports (public, with filters)
const getReports = async (req, res) => {
  try {
    const { street_id, incident_type, limit = 50, resolved } = req.query;
    let query  = `SELECT r.id, r.street_name, r.street_id, r.lat, r.lng,
                         r.incident_type, r.severity, r.description, r.photo_url,
                         r.anonymous, r.resolved, r.reported_at,
                         IF(r.anonymous, 'Anonymous', u.name) AS reporter_name
                  FROM reports r
                  JOIN users u ON r.user_id = u.id
                  WHERE 1=1`;
    const params = [];

    if (street_id)     { query += ' AND r.street_id = ?';      params.push(street_id); }
    if (incident_type) { query += ' AND r.incident_type = ?';  params.push(incident_type); }
    if (resolved !== undefined) {
      query += ' AND r.resolved = ?';
      params.push(resolved === 'true' ? 1 : 0);
    }

    query += ' ORDER BY r.reported_at DESC LIMIT ?';
    params.push(parseInt(limit));

    const [rows] = await db.query(query, params);
    res.json({ reports: rows, count: rows.length });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// GET /api/reports/:id
const getReport = async (req, res) => {
  try {
    const [rows] = await db.query(
      `SELECT r.*, IF(r.anonymous, 'Anonymous', u.name) AS reporter_name
       FROM reports r JOIN users u ON r.user_id = u.id WHERE r.id = ?`,
      [req.params.id]
    );
    if (!rows.length) return res.status(404).json({ error: 'Report not found' });
    res.json({ report: rows[0] });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// POST /api/reports/:id/vote
const voteReport = async (req, res) => {
  try {
    const { vote } = req.body; // 'up' or 'down'
    if (!['up', 'down'].includes(vote))
      return res.status(400).json({ error: 'vote must be "up" or "down"' });

    await db.query(
      `INSERT INTO report_votes (report_id, voter_id, vote)
       VALUES (?, ?, ?)
       ON DUPLICATE KEY UPDATE vote = VALUES(vote)`,
      [req.params.id, req.user.id, vote]
    );

    // Update reporter trust score
    const [report] = await db.query('SELECT user_id FROM reports WHERE id = ?', [req.params.id]);
    if (report.length) {
      const delta = vote === 'up' ? 0.05 : -0.05;
      await db.query(
        'UPDATE users SET trust_score = GREATEST(0, LEAST(2.0, trust_score + ?)) WHERE id = ?',
        [delta, report[0].user_id]
      );
    }

    res.json({ message: `Vote "${vote}" recorded` });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

module.exports = { createReport, getReports, getReport, voteReport };
