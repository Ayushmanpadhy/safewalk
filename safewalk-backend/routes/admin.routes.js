// routes/admin.routes.js
const express = require('express');
const router  = express.Router();
const { getAllReports, resolveReport, getHotspots, getAnalytics, verifyUser } = require('../controllers/adminController');
const { protect, requireRole } = require('../middleware/auth');

const guard = [protect, requireRole('authority', 'admin')];

router.get('/reports',              ...guard, getAllReports);
router.patch('/reports/:id/resolve',...guard, resolveReport);
router.get('/hotspots',             ...guard, getHotspots);
router.get('/analytics',            ...guard, getAnalytics);
router.patch('/users/:id/verify',   protect, requireRole('admin'), verifyUser);

module.exports = router;
