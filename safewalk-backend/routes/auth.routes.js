// routes/auth.routes.js
const express = require('express');
const router  = express.Router();
const { register, login, getMe, updateEmergencyContacts } = require('../controllers/authController');
const { protect } = require('../middleware/auth');

router.post('/register',           register);
router.post('/login',              login);
router.get('/me',                  protect, getMe);
router.put('/emergency-contacts',  protect, updateEmergencyContacts);

module.exports = router;
