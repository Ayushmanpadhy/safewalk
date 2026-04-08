// cron/scoreEngine.js — Hourly safety score recalculator
const cron = require('node-cron');
const db   = require('../config/db');

const getTimeMultiplier = (hour) => {
  if (hour >= 6  && hour < 18) return 1.0;
  if (hour >= 18 && hour < 21) return 1.3;
  if (hour >= 21 && hour < 24) return 1.6;
  return 2.0;
};

const SEVERITY_WEIGHTS = {
  poor_lighting: 2, suspicious_person: 3, harassment: 4, assault: 5,
  eve_teasing: 4, theft_robbery: 4, drunk_crowd: 2,
  broken_cctv: 1, isolated_road: 2, general_unsafe: 2
};

const getDecayFactor = (reportedAt) => {
  const hoursOld = (Date.now() - new Date(reportedAt).getTime()) / 3600000;
  return Math.max(0.01, Math.exp(-0.1 * hoursOld));
};

const calculateScore = (reports, hour) => {
  if (!reports.length) return 100;
  const timeMultiplier = getTimeMultiplier(hour);
  let totalPenalty = 0;
  for (const r of reports) {
    const sw = SEVERITY_WEIGHTS[r.incident_type] || 2;
    const df = getDecayFactor(r.reported_at);
    const tf = Math.min(2.0, Math.max(0.5, r.trust_score || 1.0));
    totalPenalty += sw * df * tf * timeMultiplier;
  }
  return Math.min(100, Math.round(Math.max(0, 100 - totalPenalty * 4)));
};

const getTrend = (oldScore, newScore) => {
  const diff = newScore - oldScore;
  if (diff >= 5)  return 'improving';
  if (diff <= -5) return 'worsening';
  return 'stable';
};

const runScoreEngine = async () => {
  const startTime = Date.now();
  const hour = new Date().getHours();
  console.log(`[ScoreEngine] Running at hour ${hour}`);

  try {
    const [allReports] = await db.query(
      `SELECT r.street_id, r.incident_type, r.severity, r.reported_at, u.trust_score
       FROM reports r JOIN users u ON r.user_id = u.id
       WHERE r.resolved = 0 AND r.reported_at >= DATE_SUB(NOW(), INTERVAL 48 HOUR)`
    );

    const byStreet = {};
    for (const report of allReports) {
      if (!byStreet[report.street_id]) byStreet[report.street_id] = [];
      byStreet[report.street_id].push(report);
    }

    const [currentScores] = await db.query('SELECT street_id, score FROM street_safety_scores');
    const scoreMap = {};
    for (const row of currentScores) scoreMap[row.street_id] = row.score;

    const [allStreets] = await db.query('SELECT street_id FROM street_safety_scores');
    if (!allStreets || allStreets.length === 0) {
      console.log('[ScoreEngine] No streets found. Skipping cycle silently.');
      return;
    }

    let updated = 0, escalated = 0;

    for (const { street_id } of allStreets) {
      const reports = byStreet[street_id] || [];
      
      // Skip streets with no reports — preserve seeded/imported scores
      if (reports.length === 0) continue;
      
      const newScore    = calculateScore(reports, hour);
      const oldScore    = scoreMap[street_id] ?? 100;
      const trend       = getTrend(oldScore, newScore);
      const dayScore    = calculateScore(reports, 12);
      const nightScore  = calculateScore(reports, 23);
      const shouldEscalate = newScore < 30;

      await db.query(
        `UPDATE street_safety_scores
         SET score=?, score_day=?, score_night=?, active_report_count=?,
             trend=?, escalated=?, last_updated=NOW()
         WHERE street_id=?`,
        [newScore, dayScore, nightScore, reports.length, trend, shouldEscalate, street_id]
      );

      await db.query(
        'INSERT INTO score_history (street_id, score, hour_time) VALUES (?, ?, ?)',
        [street_id, newScore, hour]
      );

      updated++;
      if (shouldEscalate) escalated++;
    }

    // Escalation alerts for 72h+ danger zones
    const [chronicDanger] = await db.query(
      `SELECT s.street_id, s.street_name, s.score,
              TIMESTAMPDIFF(HOUR, MIN(h.recorded_at), NOW()) AS hours_in_danger
       FROM street_safety_scores s
       JOIN score_history h ON s.street_id = h.street_id
       WHERE s.score < 30 AND h.score < 30
       GROUP BY s.street_id HAVING hours_in_danger >= 72`
    );

    for (const zone of chronicDanger) {
      const [auths] = await db.query(
        `SELECT id FROM users WHERE role IN ('authority','admin') AND is_active=1`
      );
      for (const auth of auths) {
        const [exists] = await db.query(
          `SELECT id FROM notifications WHERE user_id=? AND type='escalation_alert'
           AND message LIKE ? AND DATE(created_at)=CURDATE()`,
          [auth.id, `%${zone.street_name}%`]
        );
        if (!exists.length) {
          await db.query(
            `INSERT INTO notifications (user_id, type, message) VALUES (?, 'escalation_alert', ?)`,
            [auth.id, `ESCALATION: "${zone.street_name}" danger for ${zone.hours_in_danger}h. Action required.`]
          );
        }
      }
    }

    // Clean old history
    await db.query(`DELETE FROM score_history WHERE recorded_at < DATE_SUB(NOW(), INTERVAL 30 DAY)`);

    console.log(`[ScoreEngine] Done in ${((Date.now()-startTime)/1000).toFixed(2)}s | Updated: ${updated} | Escalated: ${escalated}`);
  } catch (err) {
    console.error('[ScoreEngine] ERROR:', err.message);
  }
};

cron.schedule('0 * * * *', runScoreEngine);
setTimeout(runScoreEngine, 3000);
module.exports = { runScoreEngine };
