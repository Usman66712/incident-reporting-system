USE incident_db;

SELECT * FROM users  WHERE email = ?;

SELECT * FROM admins WHERE email = ?;

INSERT INTO users (name, email, password, contact_info)
VALUES (?, ?, ?, ?);

INSERT INTO user_profiles (user_id, department)
VALUES (?, ?);

INSERT INTO incidents (reported_by, title, description, category, severity, location)
VALUES (?, ?, ?, ?, ?, ?);

SELECT incident_id, title, category, severity, status, reported_at
FROM   incidents
WHERE  reported_by = ?
ORDER  BY reported_at DESC;

SELECT i.*,
       u.name AS reporter_name,
       a.name AS admin_name
FROM       incidents i
JOIN       users  u ON i.reported_by = u.user_id
LEFT JOIN  admins a ON i.assigned_to = a.admin_id
WHERE i.incident_id = ?;

SELECT v.*, a.name AS admin_name
FROM   verifications v
JOIN   admins a ON v.verified_by = a.admin_id
WHERE  v.incident_id = ?;

SELECT r.*, a.name AS admin_name
FROM   resolutions r
JOIN   admins a ON r.resolved_by = a.admin_id
WHERE  r.incident_id = ?;

SELECT i.*, u.name AS reporter_name
FROM   incidents i
JOIN   users u ON i.reported_by = u.user_id
ORDER  BY i.reported_at DESC;

SELECT status, COUNT(*) AS total
FROM   incidents
GROUP  BY status;

INSERT INTO verifications (incident_id, verified_by, status, notes)
VALUES (?, ?, ?, ?);
UPDATE incidents SET status = ? WHERE incident_id = ?;

UPDATE incidents
SET    assigned_to = ?, status = 'Assigned', assigned_at = CURRENT_TIMESTAMP
WHERE  incident_id = ?;

INSERT INTO resolutions (incident_id, resolved_by, actions_taken, status)
VALUES (?, ?, ?, 'Resolved');
UPDATE incidents SET status = 'Resolved' WHERE incident_id = ?;

INSERT INTO notifications (incident_id, recipient_id, message, type)
VALUES (?, ?, ?, ?);

SELECT n.*, i.title AS incident_title
FROM   notifications n
JOIN   incidents i ON n.incident_id = i.incident_id
WHERE  n.recipient_id = ?
ORDER  BY n.created_at DESC;

UPDATE notifications SET status = 'Read' WHERE recipient_id = ?;
