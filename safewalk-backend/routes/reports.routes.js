// routes/reports.routes.js
const express = require('express');
const router  = express.Router();
const multer  = require('multer');
const path    = require('path');
const { createReport, getReports, getReport, voteReport } = require('../controllers/reportsController');
const { protect } = require('../middleware/auth');

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, 'D:\\SAFEWALK\\safewalk-backend\\uploads'),
  filename:    (req, file, cb) => cb(null, `${Date.now()}-${file.originalname}`)
});
const upload = multer({
  storage,
  limits: { fileSize: 5 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    const allowed = ['.jpg', '.jpeg', '.png', '.webp'];
    cb(null, allowed.includes(path.extname(file.originalname).toLowerCase()));
  }
});

router.get('/',           getReports);
router.post('/',          protect, upload.single('photo'), createReport);
router.get('/:id',        getReport);
router.post('/:id/vote',  protect, voteReport);

module.exports = router;
