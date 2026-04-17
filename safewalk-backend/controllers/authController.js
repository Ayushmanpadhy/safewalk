// controllers/authController.js
const bcrypt = require('bcryptjs');
const jwt    = require('jsonwebtoken');
const db     = require('../config/db');

// POST /api/auth/register
const register = async (req, res) => {
  try {
    const { name, email, password, phone } = req.body;
    if (!name || !email || !password)
      return res.status(400).json({ error: 'name, email and password are required' });

    const [existing] = await db.query('SELECT id FROM users WHERE email = ?', [email]);
    if (existing.length)
      return res.status(409).json({ error: 'Email already registered' });

    const hashed = await bcrypt.hash(password, 10);
    const [result] = await db.query(
      'INSERT INTO users (name, email, password, phone) VALUES (?, ?, ?, ?)',
      [name, email, hashed, phone || null]
    );

    const token = jwt.sign({ id: result.insertId }, process.env.JWT_SECRET || 'fallback_safewalk_secret_123', {
      expiresIn: process.env.JWT_EXPIRES_IN || '7d'
    });

    res.status(201).json({
      message: 'Registration successful',
      token,
      user: { id: result.insertId, name, email, role: 'user' }
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// POST /api/auth/login
const login = async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !password)
      return res.status(400).json({ error: 'email and password are required' });

    const [rows] = await db.query(
      'SELECT * FROM users WHERE email = ? AND is_active = 1',
      [email]
    );
    if (!rows.length)
      return res.status(401).json({ error: 'Invalid credentials' });

    const user  = rows[0];
    const match = await bcrypt.compare(password, user.password);
    if (!match)
      return res.status(401).json({ error: 'Invalid credentials' });

    const token = jwt.sign({ id: user.id }, process.env.JWT_SECRET || 'fallback_safewalk_secret_123', {
      expiresIn: process.env.JWT_EXPIRES_IN || '7d'
    });

    res.json({
      message: 'Login successful',
      token,
      user: {
        id:           user.id,
        name:         user.name,
        email:        user.email,
        role:         user.role,
        trust_score:  user.trust_score,
        is_verified:  user.is_verified
      }
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// GET /api/auth/me
const getMe = async (req, res) => {
  res.json({ user: req.user });
};

// PUT /api/auth/emergency-contacts
const updateEmergencyContacts = async (req, res) => {
  try {
    const { contacts } = req.body; // [{name, phone, email}]
    if (!Array.isArray(contacts))
      return res.status(400).json({ error: 'contacts must be an array' });

    await db.query(
      'UPDATE users SET emergency_contacts = ? WHERE id = ?',
      [JSON.stringify(contacts), req.user.id]
    );
    res.json({ message: 'Emergency contacts updated' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

module.exports = { register, login, getMe, updateEmergencyContacts };
