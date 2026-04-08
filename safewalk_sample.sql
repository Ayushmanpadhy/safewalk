USE safewalk;

INSERT INTO street_safety_scores 
(street_id, street_name, lat, lng, score, score_day, score_night, 
 active_report_count, trend, escalated, last_updated)
VALUES
('17.385_78.487', 'MG Road Hyderabad', 17.3850, 78.4867, 72, 85, 55, 3, 'stable', 0, NOW()),
('17.432_78.474', 'Begumpet Road', 17.4322, 78.4742, 45, 60, 28, 7, 'worsening', 0, NOW()),
('17.447_78.498', 'Secunderabad Station Road', 17.4472, 78.4982, 88, 92, 78, 1, 'improving', 0, NOW()),
('17.361_78.474', 'Mehdipatnam Main Road', 17.3614, 78.4742, 28, 40, 12, 12, 'worsening', 1, NOW()),
('17.412_78.456', 'Banjara Hills Road No.12', 17.4127, 78.4564, 91, 95, 82, 0, 'stable', 0, NOW()),
('17.371_78.512', 'Dilsukhnagar Main Road', 17.3712, 78.5124, 38, 52, 20, 9, 'worsening', 1, NOW()),
('17.494_78.390', 'HITEC City Main Road', 17.4947, 78.3906, 95, 97, 90, 0, 'improving', 0, NOW()),
('17.383_78.468', 'Abids Circle', 17.3833, 78.4688, 55, 68, 38, 5, 'stable', 0, NOW()),
('17.426_78.448', 'Punjagutta Cross Road', 17.4267, 78.4487, 67, 78, 48, 4, 'stable', 0, NOW()),
('17.366_78.497', 'LB Nagar X Roads', 17.3664, 78.4974, 31, 45, 15, 11, 'worsening', 1, NOW()),
('17.453_78.381', 'Gachibowli Road', 17.4532, 78.3814, 82, 90, 70, 2, 'improving', 0, NOW()),
('17.397_78.481', 'Nampally Station Road', 17.3972, 78.4814, 48, 62, 30, 8, 'stable', 0, NOW()),
('17.418_78.410', 'Jubilee Hills Road No.36', 17.4182, 78.4105, 76, 84, 62, 3, 'improving', 0, NOW()),
('17.379_78.451', 'Masab Tank Road', 17.3792, 78.4512, 42, 56, 24, 7, 'worsening', 0, NOW()),
('17.467_78.468', 'Paradise Circle Secunderabad', 17.4672, 78.4684, 60, 72, 44, 5, 'stable', 0, NOW());
