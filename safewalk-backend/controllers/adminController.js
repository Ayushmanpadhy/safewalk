// controllers/adminController.js
const db = require('../config/db');

// GET /api/admin/reports — all unresolved reports
const getAllReports = async (req, res) => {
  try {
    const { resolved = 'false', incident_type, street_id, limit = 100 } = req.query;
    let query  = `SELECT r.*, u.name AS reporter_name, u.trust_score
                  FROM reports r JOIN users u ON r.user_id = u.id WHERE 1=1`;
    const params = [];

    if (resolved !== 'all')  { query += ' AND r.resolved = ?'; params.push(resolved === 'true' ? 1 : 0); }
    if (incident_type)       { query += ' AND r.incident_type = ?'; params.push(incident_type); }
    if (street_id)           { query += ' AND r.street_id = ?'; params.push(street_id); }

    query += ' ORDER BY r.severity DESC, r.reported_at DESC LIMIT ?';
    params.push(parseInt(limit));

    const [rows] = await db.query(query, params);
    res.json({ reports: rows, count: rows.length });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// PATCH /api/admin/reports/:id/resolve — mark a report resolved
const resolveReport = async (req, res) => {
  try {
    await db.query(
      'UPDATE reports SET resolved = 1, resolved_by = ?, resolved_at = NOW() WHERE id = ?',
      [req.user.id, req.params.id]
    );

    // Get the street_id for score recalculation notice
    const [report] = await db.query('SELECT street_id, user_id FROM reports WHERE id = ?', [req.params.id]);
    if (report.length) {
      // Notify the reporter
      await db.query(
        `INSERT INTO notifications (user_id, type, message) VALUES (?, 'report_resolved', ?)`,
        [report[0].user_id, `Your report has been reviewed and marked resolved by authorities.`]
      );
      // Boost reporter trust score slightly
      await db.query(
        'UPDATE users SET trust_score = LEAST(2.0, trust_score + 0.1) WHERE id = ?',
        [report[0].user_id]
      );
    }

    res.json({ message: 'Report marked as resolved. Score will update next cycle.' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// GET /api/admin/hotspots — danger zones needing attention
const getHotspots = async (req, res) => {
  try {
    const [rows] = await db.query(
      `SELECT s.*, COUNT(r.id) AS open_reports
       FROM street_safety_scores s
       LEFT JOIN reports r ON s.street_id = r.street_id AND r.resolved = 0
       WHERE s.score < 40
       GROUP BY s.id
       ORDER BY s.score ASC LIMIT 50`
    );
    res.json({ hotspots: rows, count: rows.length });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// GET /api/admin/analytics — dashboard stats
const getAnalytics = async (req, res) => {
  try {
    const [[totalReports]]   = await db.query('SELECT COUNT(*) AS c FROM reports');
    const [[openReports]]    = await db.query('SELECT COUNT(*) AS c FROM reports WHERE resolved = 0');
    const [[totalUsers]]     = await db.query('SELECT COUNT(*) AS c FROM users WHERE role = "user"');
    const [[dangerStreets]]  = await db.query('SELECT COUNT(*) AS c FROM street_safety_scores WHERE score < 30');
    const [[sosToday]]       = await db.query('SELECT COUNT(*) AS c FROM sos_alerts WHERE DATE(triggered_at) = CURDATE()');
    const [incidentBreakdown] = await db.query(
      'SELECT incident_type, COUNT(*) AS count FROM reports GROUP BY incident_type ORDER BY count DESC'
    );
    const [worstStreets] = await db.query(
      'SELECT street_name, score, active_report_count FROM street_safety_scores ORDER BY score ASC LIMIT 5'
    );

    res.json({
      summary: {
        total_reports:  totalReports.c,
        open_reports:   openReports.c,
        total_users:    totalUsers.c,
        danger_streets: dangerStreets.c,
        sos_today:      sosToday.c
      },
      incident_breakdown: incidentBreakdown,
      worst_streets:      worstStreets
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// PATCH /api/admin/users/:id/verify — verify a reporter
const verifyUser = async (req, res) => {
  try {
    await db.query(
      'UPDATE users SET is_verified = 1, trust_score = LEAST(2.0, trust_score + 0.5) WHERE id = ?',
      [req.params.id]
    );
    res.json({ message: 'User verified as trusted reporter' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

module.exports = { getAllReports, resolveReport, getHotspots, getAnalytics, verifyUser };
