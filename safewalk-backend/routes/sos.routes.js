// routes/sos.routes.js
const express = require('express');
const router  = express.Router();
const { triggerSOS, getSOSHistory } = require('../controllers/sosController');
const { protect } = require('../middleware/auth');

router.post('/',        protect, triggerSOS);
router.get('/history',  protect, getSOSHistory);

module.exports = router;
