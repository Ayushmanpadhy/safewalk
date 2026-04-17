// server.js — SafeWalk API Entry Point
require('dotenv').config();
const express    = require('express');
const cors       = require('cors');
const path       = require('path');
const fs         = require('fs');

// Ensure uploads folder exists
const uploadDir = process.env.UPLOAD_DIR || path.join(__dirname, 'uploads');
fs.mkdirSync(uploadDir, { recursive: true });

// Import routes
const authRoutes    = require('./routes/auth.routes');
const reportRoutes  = require('./routes/reports.routes');
const scoreRoutes   = require('./routes/scores.routes');
const routeRoutes   = require('./routes/route.routes');
const sosRoutes     = require('./routes/sos.routes');
const adminRoutes   = require('./routes/admin.routes');

// Import cron job
require('./cron/scoreEngine');

const app  = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors({
  origin: '*',
  methods: ['GET','POST','PUT','PATCH','DELETE','OPTIONS'],
  allowedHeaders: ['Content-Type','Authorization']
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use('/uploads', express.static(uploadDir));

// API Routes
app.use('/api/auth',    authRoutes);
app.use('/api/reports', reportRoutes);
app.use('/api/scores',  scoreRoutes);
app.use('/api/route',   routeRoutes);
app.use('/api/sos',     sosRoutes);
app.use('/api/admin',   adminRoutes);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', service: 'SafeWalk API', time: new Date().toISOString() });
});

// Serve the frontend static files (MUST come before 404 handler)
const frontendDir = path.join(__dirname, '../sw-final');
app.use(express.static(frontendDir));

// Connect root path to the live map
app.get('/', (req, res) => {
  res.redirect('/pages/map.html');
});

// 404 (catch-all — must be LAST)
app.use((req, res) => {
  res.status(404).json({ error: `Route ${req.originalUrl} not found` });
});

// Global error handler
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error: ' + (err.message || 'Unknown error') });
});

// Start
app.listen(PORT, () => {
  console.log(`SafeWalk API running on http://localhost:${PORT}`);
});

module.exports = app;
