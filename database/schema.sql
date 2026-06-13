CREATE DATABASE IF NOT EXISTS incident_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE incident_db;

DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS resolutions;
DROP TABLE IF EXISTS verifications;
DROP TABLE IF EXISTS incidents;
DROP TABLE IF EXISTS user_profiles;
DROP TABLE IF EXISTS admins;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id      INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100)  NOT NULL,
    email        VARCHAR(120)  NOT NULL UNIQUE,
    password     VARCHAR(255)  NOT NULL,
    contact_info VARCHAR(50),
    role         VARCHAR(20)   NOT NULL DEFAULT 'Reporter',
    created_at   TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE user_profiles (
    profile_id  INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL UNIQUE,
    department  VARCHAR(80),
    designation VARCHAR(80),
    address     VARCHAR(200),
    CONSTRAINT fk_profile_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE admins (
    admin_id    INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(120) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    designation VARCHAR(50)  NOT NULL DEFAULT 'Administrator',
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE incidents (
    incident_id INT AUTO_INCREMENT PRIMARY KEY,
    reported_by INT NOT NULL,
    title       VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,

    category    ENUM('Technical','Security','Workplace','Other') NOT NULL DEFAULT 'Other',
    severity    ENUM('Low','Medium','High','Critical')           NOT NULL DEFAULT 'Low',
    location    VARCHAR(120),
    status      ENUM('Pending','Verified','Assigned','In Progress','Resolved','Rejected')
                    NOT NULL DEFAULT 'Pending',
    assigned_to INT NULL,
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_at TIMESTAMP NULL,
    CONSTRAINT fk_incident_user
        FOREIGN KEY (reported_by) REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_incident_admin
        FOREIGN KEY (assigned_to) REFERENCES admins(admin_id)
        ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE verifications (
    verification_id INT AUTO_INCREMENT PRIMARY KEY,
    incident_id     INT NOT NULL UNIQUE,
    verified_by     INT NOT NULL,
    status          ENUM('Verified','Rejected') NOT NULL,
    notes           TEXT,
    verified_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_verif_incident
        FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_verif_admin
        FOREIGN KEY (verified_by) REFERENCES admins(admin_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE resolutions (
    resolution_id   INT AUTO_INCREMENT PRIMARY KEY,
    incident_id     INT NOT NULL UNIQUE,
    resolved_by     INT NOT NULL,
    actions_taken   TEXT NOT NULL,
    status          ENUM('Resolved','Closed','Reopened') NOT NULL DEFAULT 'Resolved',
    completion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_resol_incident
        FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_resol_admin
        FOREIGN KEY (resolved_by) REFERENCES admins(admin_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    incident_id     INT NOT NULL,
    recipient_id    INT NOT NULL,
    message         VARCHAR(255) NOT NULL,
    type            ENUM('System','Email','SMS') NOT NULL DEFAULT 'System',
    status          ENUM('Unread','Read') NOT NULL DEFAULT 'Unread',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notif_incident
        FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_notif_user
        FOREIGN KEY (recipient_id) REFERENCES users(user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_incident_reporter ON incidents(reported_by);
CREATE INDEX idx_incident_status   ON incidents(status);
CREATE INDEX idx_notif_recipient   ON notifications(recipient_id);
