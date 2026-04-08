// middleware/auth.js — JWT verification + role guard
const jwt = require('jsonwebtoken');
const db  = require('../config/db');

// Verify JWT token
const protect = async (req, res, next) => {
  try {
    const header = req.headers.authorization;
    if (!header || !header.startsWith('Bearer '))
      return res.status(401).json({ error: 'No token provided' });

    const token   = header.split(' ')[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    const [rows] = await db.query(
      'SELECT id, name, email, role, trust_score, is_active FROM users WHERE id = ?',
      [decoded.id]
    );
    if (!rows.length || !rows[0].is_active)
      return res.status(401).json({ error: 'User not found or inactive' });

    req.user = rows[0];
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
};

// Role-based access control
const requireRole = (...roles) => (req, res, next) => {
  if (!roles.includes(req.user.role))
    return res.status(403).json({ error: 'Access denied — insufficient role' });
  next();
};

module.exports = { protect, requireRole };
