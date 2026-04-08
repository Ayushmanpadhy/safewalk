-- ============================================================
--  SafeWalk — Full MySQL Database Schema
--  Run this file once to set up the entire database
-- ============================================================

CREATE DATABASE IF NOT EXISTS safewalk;
USE safewalk;

-- ============================================================
-- 1. USERS
--    Stores all user accounts (public users, authorities, admins)
-- ============================================================
CREATE TABLE users (
    id                 INT AUTO_INCREMENT PRIMARY KEY,
    name               VARCHAR(100)  NOT NULL,
    email              VARCHAR(150)  NOT NULL UNIQUE,
    password           VARCHAR(255)  NOT NULL,           -- bcrypt hashed
    role               ENUM('user', 'authority', 'admin') DEFAULT 'user',
    trust_score        FLOAT         DEFAULT 1.0,        -- reporter credibility (0.0–2.0)
    phone              VARCHAR(20)   DEFAULT NULL,
    emergency_contacts JSON          DEFAULT NULL,       -- [{name, phone, email}, ...]
    is_verified        BOOLEAN       DEFAULT FALSE,      -- admin-verified reporter
    is_active          BOOLEAN       DEFAULT TRUE,
    created_at         TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. REPORTS
--    Every incident submitted by a user
-- ============================================================
CREATE TABLE reports (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT           NOT NULL,
    lat            DECIMAL(10,7) NOT NULL,
    lng            DECIMAL(10,7) NOT NULL,
    street_name    VARCHAR(200)  NOT NULL,
    street_id      VARCHAR(200)  NOT NULL,               -- derived key: "lat_lng_rounded"
    incident_type  ENUM(
                     'poor_lighting',
                     'suspicious_person',
                     'harassment',
                     'assault',
                     'eve_teasing',
                     'theft_robbery',
                     'drunk_crowd',
                     'broken_cctv',
                     'isolated_road',
                     'general_unsafe'
                   ) NOT NULL,
    severity       INT           NOT NULL DEFAULT 3,     -- 1 (low) to 5 (critical)
    description    TEXT          DEFAULT NULL,
    photo_url      VARCHAR(500)  DEFAULT NULL,
    anonymous      BOOLEAN       DEFAULT FALSE,
    resolved       BOOLEAN       DEFAULT FALSE,
    resolved_by    INT           DEFAULT NULL,           -- authority user_id
    resolved_at    TIMESTAMP     DEFAULT NULL,
    reported_at    TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)     REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_street_id    (street_id),
    INDEX idx_reported_at  (reported_at),
    INDEX idx_resolved     (resolved),
    INDEX idx_lat_lng      (lat, lng)
);

-- ============================================================
-- 3. STREET SAFETY SCORES
--    One row per street — updated every hour by cron job
-- ============================================================
CREATE TABLE street_safety_scores (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    street_id      VARCHAR(200)  NOT NULL UNIQUE,        -- matches reports.street_id
    street_name    VARCHAR(200)  NOT NULL,
    lat            DECIMAL(10,7) NOT NULL,               -- street center point
    lng            DECIMAL(10,7) NOT NULL,
    score          INT           NOT NULL DEFAULT 100,   -- 0 (danger) to 100 (safe)
    score_day      INT           NOT NULL DEFAULT 100,   -- score during 6am–6pm
    score_night    INT           NOT NULL DEFAULT 100,   -- score during 9pm–6am
    active_report_count INT      NOT NULL DEFAULT 0,
    trend          ENUM('improving', 'stable', 'worsening') DEFAULT 'stable',
    escalated      BOOLEAN       DEFAULT FALSE,          -- flagged for 72h danger
    last_updated   TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_score     (score),
    INDEX idx_lat_lng   (lat, lng),
    INDEX idx_escalated (escalated)
);

-- ============================================================
-- 4. SOS ALERTS
--    Panic button triggers stored here
-- ============================================================
CREATE TABLE sos_alerts (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT           NOT NULL,
    lat          DECIMAL(10,7) NOT NULL,
    lng          DECIMAL(10,7) NOT NULL,
    address      VARCHAR(300)  DEFAULT NULL,             -- reverse geocoded
    contacts_notified JSON     DEFAULT NULL,             -- who was alerted
    resolved     BOOLEAN       DEFAULT FALSE,
    triggered_at TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    resolved_at  TIMESTAMP     DEFAULT NULL,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id    (user_id),
    INDEX idx_triggered  (triggered_at)
);

-- ============================================================
-- 5. SAFE ROUTES
--    Stored route queries for history and analytics
-- ============================================================
CREATE TABLE safe_routes (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT           NOT NULL,
    from_lat     DECIMAL(10,7) NOT NULL,
    from_lng     DECIMAL(10,7) NOT NULL,
    to_lat       DECIMAL(10,7) NOT NULL,
    to_lng       DECIMAL(10,7) NOT NULL,
    from_name    VARCHAR(200)  DEFAULT NULL,
    to_name      VARCHAR(200)  DEFAULT NULL,
    route_json   JSON          NOT NULL,                 -- array of {lat,lng,score} waypoints
    total_dist_m INT           DEFAULT NULL,             -- distance in metres
    avg_score    INT           DEFAULT NULL,             -- average safety of route
    created_at   TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id   (user_id)
);

-- ============================================================
-- 6. SCORE HISTORY
--    Archive of hourly scores — powers trend charts
-- ============================================================
CREATE TABLE score_history (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    street_id   VARCHAR(200) NOT NULL,
    score       INT          NOT NULL,
    hour_time   TINYINT      NOT NULL,                   -- 0–23, hour of day
    recorded_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_street_id  (street_id),
    INDEX idx_recorded   (recorded_at)
);

-- ============================================================
-- 7. NOTIFICATIONS
--    In-app alerts for users and authorities
-- ============================================================
CREATE TABLE notifications (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT          NOT NULL,
    type        ENUM(
                  'danger_zone_nearby',
                  'sos_triggered',
                  'report_resolved',
                  'escalation_alert',
                  'trust_score_update'
                ) NOT NULL,
    message     TEXT         NOT NULL,
    is_read     BOOLEAN      DEFAULT FALSE,
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_read (is_read)
);

-- ============================================================
-- 8. REPORT VOTES
--    Community can upvote/downvote reports (affects trust score)
-- ============================================================
CREATE TABLE report_votes (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    report_id  INT  NOT NULL,
    voter_id   INT  NOT NULL,
    vote       ENUM('up', 'down') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_vote (report_id, voter_id),
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
    FOREIGN KEY (voter_id)  REFERENCES users(id)   ON DELETE CASCADE
);

-- ============================================================
-- SEED DATA — Default admin account
-- Password: admin123 (bcrypt hash — change in production)
-- ============================================================
INSERT INTO users (name, email, password, role, trust_score, is_verified) VALUES
('Admin', 'admin@safewalk.com', '$2b$10$examplehashedpassword', 'admin', 2.0, TRUE),
('Police HQ', 'police@safewalk.com', '$2b$10$examplehashedpassword', 'authority', 2.0, TRUE);

-- ============================================================
-- SEVERITY REFERENCE (comment only — used in score engine)
--   poor_lighting      → severity 2
--   suspicious_person  → severity 3
--   harassment         → severity 4
--   assault            → severity 5
--   eve_teasing        → severity 4
--   theft_robbery      → severity 4
--   drunk_crowd        → severity 2
--   broken_cctv        → severity 1
--   isolated_road      → severity 2
--   general_unsafe     → severity 2
-- ============================================================
