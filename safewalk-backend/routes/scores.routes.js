// routes/scores.routes.js
const express = require('express');
const router  = express.Router();
const { getHeatmap, getStreetScore, getNearbyScores } = require('../controllers/scoresController');

router.get('/heatmap',    getHeatmap);
router.get('/nearby',     getNearbyScores);
router.get('/:streetId',  getStreetScore);

module.exports = router;

// ---- routes/route.routes.js ----
// (separate file in real project, combined here for brevity)
