// controllers/sosController.js
const db         = require('../config/db');
const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransport({
  host:   process.env.EMAIL_HOST,
  port:   process.env.EMAIL_PORT,
  secure: false,
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS
  }
});

// POST /api/sos — trigger SOS alert
const triggerSOS = async (req, res) => {
  try {
    const { lat, lng, address } = req.body;
    if (!lat || !lng)
      return res.status(400).json({ error: 'lat and lng are required' });

    // Get user's emergency contacts
    const [userRows] = await db.query(
      'SELECT name, emergency_contacts FROM users WHERE id = ?',
      [req.user.id]
    );
    const user     = userRows[0];
    const contacts = user?.emergency_contacts || [];

    // Save SOS record
    const [result] = await db.query(
      'INSERT INTO sos_alerts (user_id, lat, lng, address, contacts_notified) VALUES (?, ?, ?, ?, ?)',
      [req.user.id, lat, lng, address || null, JSON.stringify(contacts)]
    );

    // Send email/notification to each emergency contact
    const mapsLink = `https://maps.google.com/?q=${lat},${lng}`;
    const notified = [];

    for (const contact of contacts) {
      if (contact.email) {
        try {
          await transporter.sendMail({
            from:    process.env.EMAIL_USER,
            to:      contact.email,
            subject: `URGENT: ${user.name} triggered SOS alert on SafeWalk`,
            html: `
              <h2 style="color:#E24B4A;">SOS Alert from SafeWalk</h2>
              <p><strong>${user.name}</strong> has triggered an emergency SOS alert.</p>
              <p><strong>Location:</strong> ${address || 'See map link below'}</p>
              <p><strong>GPS:</strong> ${lat}, ${lng}</p>
              <p><a href="${mapsLink}" style="background:#E24B4A;color:#fff;padding:10px 20px;text-decoration:none;border-radius:5px;">
                View on Google Maps
              </a></p>
              <p style="color:#999;font-size:12px;">Sent via SafeWalk Safety App</p>
            `
          });
          notified.push(contact.email);
        } catch (mailErr) {
          console.error(`Failed to email ${contact.email}:`, mailErr.message);
        }
      }
    }

    // Create in-app notification for the user
    await db.query(
      `INSERT INTO notifications (user_id, type, message)
       VALUES (?, 'sos_triggered', ?)`,
      [req.user.id, `SOS alert sent. ${notified.length} contact(s) notified.`]
    );

    res.status(201).json({
      message:    'SOS alert triggered',
      alert_id:   result.insertId,
      notified:   notified.length,
      maps_link:  mapsLink
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// GET /api/sos/history — user's SOS history
const getSOSHistory = async (req, res) => {
  try {
    const [rows] = await db.query(
      'SELECT id, lat, lng, address, resolved, triggered_at FROM sos_alerts WHERE user_id = ? ORDER BY triggered_at DESC LIMIT 20',
      [req.user.id]
    );
    res.json({ alerts: rows });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

module.exports = { triggerSOS, getSOSHistory };
