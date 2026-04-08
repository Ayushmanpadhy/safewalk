// routes/route.routes.js
const express = require('express');
const router  = express.Router();
const { getSafeRoute, getRouteHistory } = require('../controllers/routeController');
const { protect } = require('../middleware/auth');

router.get('/',        protect, getSafeRoute);
router.get('/history', protect, getRouteHistory);

module.exports = router;
