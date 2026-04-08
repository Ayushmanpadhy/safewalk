USE safewalk;
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE score_history;
TRUNCATE TABLE street_safety_scores;
TRUNCATE TABLE reports;
SET FOREIGN_KEY_CHECKS = 1;

-- Ensure geometry column exists
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='safewalk' AND TABLE_NAME='street_safety_scores' AND COLUMN_NAME='geometry');
SET @sql = IF(@col_exists = 0, 'ALTER TABLE street_safety_scores ADD COLUMN geometry JSON DEFAULT NULL', 'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

INSERT INTO street_safety_scores (street_id, street_name, lat, lng, score, score_day, score_night, active_report_count, trend, escalated, geometry, last_updated) VALUES
('Delhi_Rajpath___Kartavya_Path', 'Rajpath / Kartavya Path', 28.61442, 77.18532, 81, 91, 61, 0, 'improving', 0, '[[77.1694, 28.6138], [77.178, 28.6141], [77.1858, 28.6144], [77.1924, 28.6148], [77.201, 28.615]]', NOW()),
('Delhi_Connaught_Place_Outer_Ring', 'Connaught Place Outer Ring', 28.629708, 77.214133, 18, 28, 0, 7, 'worsening', 1, '[[77.2167, 28.6337], [77.2192, 28.6313], [77.2195, 28.6291], [77.2183, 28.627], [77.2155, 28.6254], [77.2123, 28.6251], [77.2099, 28.6262], [77.2087, 28.6283], [77.2089, 28.6306], [77.2106, 28.6325], [77.2133, 28.6336], [77.2167, 28.6337]]', NOW()),
('Delhi_Janpath', 'Janpath', 28.637175, 77.21955, 72, 82, 52, 2, 'stable', 0, '[[77.2192, 28.6454], [77.2196, 28.6393], [77.2198, 28.635], [77.2196, 28.629]]', NOW()),
('Delhi_Mathura_Road', 'Mathura Road', 28.60726, 77.2436, 14, 24, 0, 9, 'worsening', 1, '[[77.2406, 28.5913], [77.2418, 28.5985], [77.2436, 28.607], [77.2452, 28.6155], [77.2468, 28.624]]', NOW()),
('Delhi_Lodi_Road', 'Lodi Road', 28.591375, 77.21775, 40, 50, 20, 0, 'stable', 0, '[[77.21, 28.59], [77.215, 28.5908], [77.22, 28.5917], [77.226, 28.593]]', NOW()),
('Delhi_Ring_Road_(NH-48)_North', 'Ring Road (NH-48) North', 28.68344, 77.1526, 84, 94, 64, 0, 'improving', 0, '[[77.126, 28.69], [77.138, 28.687], [77.151, 28.684], [77.166, 28.6802], [77.182, 28.676]]', NOW()),
('Delhi_Outer_Ring_Road_South', 'Outer Ring Road South', 28.57546, 77.18, 48, 58, 28, 1, 'stable', 0, '[[77.15, 28.579], [77.165, 28.576], [77.18, 28.5745], [77.195, 28.5738], [77.21, 28.574]]', NOW()),
('Delhi_Mehrauli–Badarpur_Road', 'Mehrauli–Badarpur Road', 28.5308, 77.2104, 16, 26, 0, 3, 'worsening', 1, '[[77.205, 28.512], [77.208, 28.521], [77.2105, 28.53], [77.2125, 28.54], [77.216, 28.551]]', NOW()),
('Delhi_NH-44_(GTK_Road)', 'NH-44 (GTK Road)', 28.68408, 77.16844, 81, 91, 61, 1, 'improving', 0, '[[77.1672, 28.6604], [77.168, 28.672], [77.1686, 28.684], [77.169, 28.696], [77.1694, 28.708]]', NOW()),
('Delhi_Rohtak_Road', 'Rohtak Road', 28.64675, 77.10925, 60, 70, 40, 0, 'stable', 0, '[[77.088, 28.652], [77.102, 28.648], [77.116, 28.645], [77.131, 28.642]]', NOW()),
('Delhi_GT_Karnal_Road', 'GT Karnal Road', 28.726, 77.17355, 17, 27, 0, 9, 'worsening', 1, '[[77.1694, 28.708], [77.172, 28.72], [77.1748, 28.732], [77.178, 28.744]]', NOW()),
('Delhi_Shahdara_Main_Road', 'Shahdara Main Road', 28.6602, 77.284, 75, 85, 55, 1, 'stable', 0, '[[77.272, 28.648], [77.278, 28.655], [77.284, 28.661], [77.29, 28.666], [77.296, 28.671]]', NOW()),
('Delhi_Vikas_Marg', 'Vikas Marg', 28.6416, 77.2734, 91, 100, 71, 2, 'improving', 0, '[[77.29, 28.635], [77.282, 28.639], [77.274, 28.643], [77.265, 28.645], [77.256, 28.646]]', NOW()),
('Delhi_Rani_Jhansi_Road', 'Rani Jhansi Road', 28.651, 77.201825, 54, 64, 34, 0, 'stable', 0, '[[77.2013, 28.642], [77.2015, 28.648], [77.202, 28.654], [77.2025, 28.66]]', NOW()),
('Delhi_Patel_Road___Pusa_Road', 'Patel Road / Pusa Road', 28.6445, 77.188, 93, 100, 73, 2, 'improving', 0, '[[77.17, 28.646], [77.182, 28.645], [77.194, 28.644], [77.206, 28.643]]', NOW()),
('Delhi_Parliament_Street', 'Parliament Street', 28.629475, 77.2037, 94, 100, 74, 1, 'improving', 0, '[[77.2034, 28.6246], [77.2036, 28.6289], [77.2038, 28.6307], [77.204, 28.6337]]', NOW()),
('Delhi_Aurobindo_Marg', 'Aurobindo Marg', 28.556, 77.20694, 65, 75, 45, 0, 'stable', 0, '[[77.2072, 28.533], [77.2071, 28.544], [77.207, 28.556], [77.2068, 28.568], [77.2066, 28.579]]', NOW()),
('Delhi_Barakhamba_Road', 'Barakhamba Road', 28.6335, 77.22525, 61, 71, 41, 0, 'stable', 0, '[[77.22, 28.632], [77.223, 28.633], [77.227, 28.634], [77.231, 28.635]]', NOW()),
('Delhi_Deen_Dayal_Upadhyaya_Marg', 'Deen Dayal Upadhyaya Marg', 28.6261, 77.2349, 31, 41, 11, 6, 'worsening', 0, '[[77.2445, 28.622], [77.24, 28.625], [77.235, 28.627], [77.23, 28.628], [77.225, 28.6285]]', NOW()),
('Delhi_Sansad_Marg', 'Sansad Marg', 28.6211, 77.202275, 80, 90, 60, 2, 'improving', 0, '[[77.2019, 28.6131], [77.2021, 28.6186], [77.2024, 28.6237], [77.2027, 28.629]]', NOW()),
('Mumbai_Marine_Drive', 'Marine Drive', 18.92335, 72.825733, 50, 60, 30, 0, 'stable', 0, '[[72.822, 18.932], [72.8237, 18.929], [72.8254, 18.9255], [72.8268, 18.9218], [72.828, 18.9178], [72.8285, 18.914]]', NOW()),
('Mumbai_Western_Express_Highway_N', 'Western Express Highway N', 19.09, 72.8356, 17, 27, 0, 5, 'worsening', 1, '[[72.8368, 19.12], [72.836, 19.105], [72.8354, 19.09], [72.835, 19.075], [72.8348, 19.06]]', NOW()),
('Mumbai_Eastern_Express_Highway', 'Eastern Express Highway', 19.053, 72.89268, 74, 84, 54, 2, 'stable', 0, '[[72.9002, 19.078], [72.896, 19.065], [72.8922, 19.052], [72.889, 19.041], [72.886, 19.029]]', NOW()),
('Mumbai_LBS_Marg', 'LBS Marg', 19.079, 72.895, 88, 98, 68, 1, 'improving', 0, '[[72.921, 19.085], [72.908, 19.082], [72.895, 19.079], [72.882, 19.076], [72.869, 19.073]]', NOW()),
('Mumbai_Linking_Road_Bandra', 'Linking Road Bandra', 19.064, 72.841, 27, 37, 7, 6, 'worsening', 0, '[[72.829, 19.07], [72.835, 19.067], [72.841, 19.064], [72.847, 19.061], [72.853, 19.058]]', NOW()),
('Mumbai_SV_Road', 'SV Road', 19.0764, 72.82846, 83, 93, 63, 1, 'improving', 0, '[[72.8275, 19.05], [72.8278, 19.063], [72.8283, 19.076], [72.829, 19.09], [72.8297, 19.103]]', NOW()),
('Mumbai_Mahim_Causeway', 'Mahim Causeway', 19.0405, 72.843, 63, 73, 43, 2, 'stable', 0, '[[72.84, 19.038], [72.842, 19.04], [72.844, 19.0415], [72.846, 19.0425]]', NOW()),
('Mumbai_Sion–Trombay_Road', 'Sion–Trombay Road', 19.0335, 72.88075, 40, 50, 20, 1, 'stable', 0, '[[72.865, 19.038], [72.875, 19.035], [72.886, 19.032], [72.897, 19.029]]', NOW()),
('Mumbai_Senapati_Bapat_Marg', 'Senapati Bapat Marg', 19.0195, 72.8306, 81, 91, 61, 2, 'improving', 0, '[[72.828, 19.015], [72.8296, 19.018], [72.8314, 19.021], [72.8334, 19.024]]', NOW()),
('Mumbai_P_DMello_Road', 'P D''Mello Road', 18.93375, 72.83815, 91, 100, 71, 0, 'improving', 0, '[[72.838, 18.942], [72.838, 18.936], [72.8382, 18.931], [72.8384, 18.926]]', NOW()),
('Mumbai_Dadabhai_Naoroji_Road', 'Dadabhai Naoroji Road', 18.93975, 72.836925, 70, 80, 50, 2, 'stable', 0, '[[72.8348, 18.938], [72.836, 18.939], [72.8376, 18.9405], [72.8393, 18.9415]]', NOW()),
('Mumbai_Nepean_Sea_Road', 'Nepean Sea Road', 18.964, 72.811325, 25, 35, 5, 7, 'worsening', 0, '[[72.8062, 18.962], [72.8096, 18.9635], [72.813, 18.9648], [72.8165, 18.9657]]', NOW()),
('Mumbai_Worli_Sea_Face', 'Worli Sea Face', 18.99168, 72.82004, 15, 25, 0, 5, 'worsening', 1, '[[72.8152, 18.996], [72.8175, 18.994], [72.82, 18.9918], [72.8225, 18.9894], [72.825, 18.9872]]', NOW()),
('Mumbai_Gokhale_Road_N', 'Gokhale Road N', 19.00895, 72.842325, 32, 42, 12, 8, 'worsening', 0, '[[72.84, 19.006], [72.8415, 19.008], [72.843, 19.01], [72.8448, 19.0118]]', NOW()),
('Mumbai_BKC_Central_Road', 'BKC Central Road', 19.06725, 72.872825, 86, 96, 66, 2, 'improving', 0, '[[72.868, 19.066], [72.871, 19.067], [72.8745, 19.0678], [72.8778, 19.0682]]', NOW()),
('Bangalore_MG_Road', 'MG Road', 12.974125, 77.61275, 84, 94, 64, 0, 'improving', 0, '[[77.604, 12.9716], [77.6107, 12.9739], [77.6155, 12.9754], [77.6208, 12.9756]]', NOW()),
('Bangalore_Brigade_Road', 'Brigade Road', 12.96865, 77.6059, 47, 57, 27, 0, 'stable', 0, '[[77.6041, 12.9716], [77.6053, 12.9696], [77.6065, 12.9676], [77.6077, 12.9658]]', NOW()),
('Bangalore_Residency_Road', 'Residency Road', 12.962475, 77.61165, 17, 27, 0, 5, 'worsening', 1, '[[77.6037, 12.9626], [77.609, 12.9625], [77.6143, 12.9624], [77.6196, 12.9624]]', NOW()),
('Bangalore_Church_Street', 'Church Street', 12.96985, 77.604575, 25, 35, 5, 4, 'worsening', 0, '[[77.6041, 12.9714], [77.6044, 12.9706], [77.6048, 12.9694], [77.605, 12.968]]', NOW()),
('Bangalore_Cubbon_Road', 'Cubbon Road', 12.97415, 77.6018, 24, 34, 4, 8, 'worsening', 1, '[[77.5947, 12.9762], [77.5995, 12.9751], [77.6041, 12.9734], [77.6089, 12.9719]]', NOW()),
('Bangalore_Outer_Ring_Road_(E)', 'Outer Ring Road (E)', 12.96275, 77.655, 45, 55, 25, 2, 'stable', 0, '[[77.64, 12.935], [77.65, 12.954], [77.66, 12.972], [77.67, 12.99]]', NOW()),
('Bangalore_Bannerghatta_Road', 'Bannerghatta Road', 12.901, 77.59845, 93, 100, 73, 2, 'improving', 0, '[[77.597, 12.882], [77.598, 12.895], [77.599, 12.908], [77.5998, 12.919]]', NOW()),
('Bangalore_Old_Airport_Road', 'Old Airport Road', 12.98125, 77.6485, 45, 55, 25, 1, 'stable', 0, '[[77.641, 12.972], [77.646, 12.978], [77.651, 12.984], [77.656, 12.991]]', NOW()),
('Bangalore_Bellary_Road___NH-44', 'Bellary Road / NH-44', 13.0225, 77.58875, 10, 20, 0, 5, 'worsening', 1, '[[77.593, 13.0], [77.59, 13.015], [77.587, 13.03], [77.585, 13.045]]', NOW()),
('Bangalore_Hosur_Road_(NH-44)', 'Hosur Road (NH-44)', 12.94775, 77.61975, 21, 31, 1, 10, 'worsening', 1, '[[77.612, 12.962], [77.617, 12.953], [77.622, 12.943], [77.628, 12.933]]', NOW()),
('Bangalore_Tumkur_Road', 'Tumkur Road', 13.01075, 77.521, 71, 81, 51, 2, 'stable', 0, '[[77.542, 13.0], [77.528, 13.007], [77.514, 13.014], [77.5, 13.022]]', NOW()),
('Bangalore_Mysore_Road', 'Mysore Road', 12.9615, 77.5425, 15, 25, 0, 8, 'worsening', 1, '[[77.562, 12.969], [77.549, 12.964], [77.536, 12.959], [77.523, 12.954]]', NOW()),
('Bangalore_Electronic_City_Flyover', 'Electronic City Flyover', 12.86325, 77.671, 50, 60, 30, 2, 'stable', 0, '[[77.666, 12.842], [77.669, 12.856], [77.673, 12.87], [77.676, 12.885]]', NOW()),
('Bangalore_Sarjapur_Road', 'Sarjapur Road', 12.9065, 77.6515, 64, 74, 44, 2, 'stable', 0, '[[77.638, 12.923], [77.647, 12.912], [77.656, 12.901], [77.665, 12.89]]', NOW()),
('Bangalore_Cunningham_Road', 'Cunningham Road', 12.983175, 77.598325, 41, 51, 21, 0, 'stable', 0, '[[77.593, 12.985], [77.5965, 12.984], [77.6, 12.9828], [77.6038, 12.9809]]', NOW()),
('Hyderabad_Tank_Bund_Road', 'Tank Bund Road', 17.42336, 78.47002, 16, 26, 0, 8, 'worsening', 1, '[[78.4661, 17.4266], [78.468, 17.425], [78.47, 17.4234], [78.472, 17.4218], [78.474, 17.42]]', NOW()),
('Hyderabad_Necklace_Road', 'Necklace Road', 17.4123, 78.463, 86, 96, 66, 0, 'improving', 0, '[[78.455, 17.417], [78.459, 17.414], [78.463, 17.4115], [78.467, 17.41], [78.471, 17.409]]', NOW()),
('Hyderabad_Road_No._1_Banjara_Hills', 'Road No. 1, Banjara Hills', 17.423875, 78.4515, 58, 68, 38, 1, 'stable', 0, '[[78.444, 17.426], [78.449, 17.4245], [78.454, 17.423], [78.459, 17.422]]', NOW()),
('Hyderabad_Jubilee_Hills_Road_No._36', 'Jubilee Hills Road No. 36', 17.4355, 78.4125, 12, 22, 0, 5, 'worsening', 1, '[[78.405, 17.434], [78.41, 17.435], [78.415, 17.436], [78.42, 17.437]]', NOW()),
('Hyderabad_Outer_Ring_Road_(ORR)', 'Outer Ring Road (ORR)', 17.53125, 78.4275, 60, 70, 40, 1, 'stable', 0, '[[78.32, 17.49], [78.39, 17.53], [78.46, 17.555], [78.54, 17.55]]', NOW()),
('Hyderabad_NH-44_(Nagpur_Highway)', 'NH-44 (Nagpur Highway)', 17.514, 78.57, 87, 97, 67, 2, 'improving', 0, '[[78.54, 17.489], [78.56, 17.505], [78.58, 17.522], [78.6, 17.54]]', NOW()),
('Hyderabad_NH-65_(Pune_Highway)', 'NH-65 (Pune Highway)', 17.365, 78.36, 80, 90, 60, 0, 'improving', 0, '[[78.33, 17.38], [78.35, 17.37], [78.37, 17.36], [78.39, 17.35]]', NOW()),
('Hyderabad_Rajiv_Gandhi_International_Air', 'Rajiv Gandhi International Airport Road', 17.35825, 78.4315, 84, 94, 64, 0, 'improving', 0, '[[78.429, 17.338], [78.43, 17.35], [78.432, 17.365], [78.435, 17.38]]', NOW()),
('Hyderabad_HITEC_City_Road', 'HITEC City Road', 17.4445, 78.38425, 23, 33, 3, 4, 'worsening', 1, '[[78.376, 17.4435], [78.382, 17.444], [78.387, 17.445], [78.392, 17.4455]]', NOW()),
('Hyderabad_Gachibowli–Miyapur_Road', 'Gachibowli–Miyapur Road', 17.4505, 78.3575, 22, 32, 2, 7, 'worsening', 1, '[[78.335, 17.458], [78.35, 17.453], [78.365, 17.448], [78.38, 17.443]]', NOW()),
('Hyderabad_Mehdipatnam_Road', 'Mehdipatnam Road', 17.403125, 78.43475, 60, 70, 40, 2, 'stable', 0, '[[78.429, 17.3945], [78.433, 17.4], [78.437, 17.406], [78.44, 17.412]]', NOW()),
('Hyderabad_Abids_Road', 'Abids Road', 17.392625, 78.473375, 20, 30, 0, 9, 'worsening', 1, '[[78.4722, 17.3885], [78.473, 17.391], [78.4738, 17.394], [78.4745, 17.397]]', NOW()),
('Hyderabad_Somajiguda_Circle_Road', 'Somajiguda Circle Road', 17.426275, 78.4611, 18, 28, 0, 9, 'worsening', 1, '[[78.4577, 17.4282], [78.46, 17.4268], [78.4622, 17.4255], [78.4645, 17.4246]]', NOW()),
('Hyderabad_Charminar_Road', 'Charminar Road', 17.3633, 78.472275, 61, 71, 41, 2, 'stable', 0, '[[78.4688, 17.3595], [78.471, 17.362], [78.4735, 17.3647], [78.4758, 17.367]]', NOW()),
('Hyderabad_Begumpet_Road', 'Begumpet Road', 17.44145, 78.4675, 19, 29, 0, 5, 'worsening', 1, '[[78.463, 17.443], [78.466, 17.442], [78.469, 17.441], [78.472, 17.4398]]', NOW());
