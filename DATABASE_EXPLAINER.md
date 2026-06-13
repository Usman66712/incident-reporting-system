# Database Explainer — Incident Reporting System
### Your complete viva preparation guide

> Read this once slowly and you will be able to answer **any** database
> question about this project. Everything here maps to `database/schema.sql`
> and the SQL queries inside `app.py`.

---

## 1. What the database does (the big picture)

The system stores everything about **incidents** reported inside an
organization. There are **7 tables**:

| # | Table            | Stores…                                              |
|---|------------------|------------------------------------------------------|
| 1 | `users`          | People who **report** incidents                      |
| 2 | `user_profiles`  | Extra details for a user (1 profile per user)        |
| 3 | `admins`         | Administrators / staff who **manage** incidents      |
| 4 | `incidents`      | The reported incidents (the central table)           |
| 5 | `verifications`  | An admin's decision that an incident is valid        |
| 6 | `resolutions`    | How an incident was finally fixed                    |
| 7 | `notifications`  | Messages sent to a user about their incident         |

The `incidents` table is the **centre** of the design — almost every other
table points to it with a foreign key.

---

## 2. Key terms (say these confidently in viva)

- **Primary Key (PK):** a column that uniquely identifies each row. Every
  table here has one (e.g. `user_id`, `incident_id`). It is never NULL and
  never repeats.
- **Foreign Key (FK):** a column that points to the primary key of another
  table. It creates the *relationship* between two tables. Example:
  `incidents.reported_by` is a FK pointing to `users.user_id`.
- **UNIQUE:** value cannot repeat (e.g. `email`). A UNIQUE foreign key is how
  we force a **1-to-1** relationship.
- **NOT NULL:** the column must always have a value.
- **DEFAULT:** value used when none is supplied (e.g. status defaults to
  `'Pending'`).
- **ENUM:** the column may only hold one value from a fixed list
  (e.g. severity ∈ {Low, Medium, High, Critical}). It keeps data clean.
- **AUTO_INCREMENT:** MySQL fills the PK automatically with 1, 2, 3, …
- **ON DELETE CASCADE / SET NULL:** what happens to child rows when a parent
  row is deleted (explained in section 6).

---

## 3. The tables in detail

### 3.1 `users` — people who report incidents
| Column         | Type        | Key / rule           | Meaning                         |
|----------------|-------------|----------------------|---------------------------------|
| `user_id`      | INT         | **PK**, AUTO_INCREMENT | unique id of the user         |
| `name`         | VARCHAR(100)| NOT NULL             | full name                       |
| `email`        | VARCHAR(120)| NOT NULL, **UNIQUE** | login email (no duplicates)     |
| `password`     | VARCHAR(255)| NOT NULL             | **hashed** password             |
| `contact_info` | VARCHAR(50) |                      | phone number                    |
| `role`         | VARCHAR(20) | DEFAULT 'Reporter'   | role of the user                |
| `created_at`   | TIMESTAMP   | DEFAULT now          | when the account was made       |

### 3.2 `user_profiles` — extra info (1-to-1 with users)
| Column        | Type         | Key / rule            | Meaning                    |
|---------------|--------------|-----------------------|----------------------------|
| `profile_id`  | INT          | **PK**                | id of the profile          |
| `user_id`     | INT          | **FK → users**, UNIQUE| which user it belongs to   |
| `department`  | VARCHAR(80)  |                       | e.g. IT, Finance           |
| `designation` | VARCHAR(80)  |                       | job title                  |
| `address`     | VARCHAR(200) |                       | address                    |

> The `user_id` here is **UNIQUE**, so a user can have **at most one** profile
> → this is what makes the relationship **1-to-1**.

### 3.3 `admins` — administrators / support staff
| Column        | Type         | Key / rule           | Meaning                    |
|---------------|--------------|----------------------|----------------------------|
| `admin_id`    | INT          | **PK**               | unique id of the admin     |
| `name`        | VARCHAR(100) | NOT NULL             | name                       |
| `email`       | VARCHAR(120) | NOT NULL, **UNIQUE** | login email                |
| `password`    | VARCHAR(255) | NOT NULL             | hashed password            |
| `designation` | VARCHAR(50)  | DEFAULT 'Administrator' | Admin / Support Staff   |

### 3.4 `incidents` — the central table
| Column        | Type      | Key / rule                | Meaning                          |
|---------------|-----------|---------------------------|----------------------------------|
| `incident_id` | INT       | **PK**                    | unique id of the incident        |
| `reported_by` | INT       | **FK → users**, NOT NULL  | who reported it                  |
| `title`       | VARCHAR   | NOT NULL                  | short title                      |
| `description` | TEXT      | NOT NULL                  | full description                 |
| `category`    | ENUM      | Technical/Security/Workplace/Other | type of incident        |
| `severity`    | ENUM      | Low/Medium/High/Critical  | how serious                      |
| `location`    | VARCHAR   |                           | where it happened                |
| `status`      | ENUM      | DEFAULT 'Pending'         | current stage                    |
| `assigned_to` | INT       | **FK → admins**, NULL     | which admin is handling it       |
| `reported_at` | TIMESTAMP | DEFAULT now               | when reported                    |
| `assigned_at` | TIMESTAMP | NULL                      | when assigned                    |

> `status` moves through: **Pending → Verified → Assigned → Resolved**
> (or **Rejected**). This is the life-cycle of an incident.

### 3.5 `verifications` — 1-to-1 with incidents
| Column            | Type | Key / rule                   | Meaning                  |
|-------------------|------|------------------------------|--------------------------|
| `verification_id` | INT  | **PK**                       | id of the verification   |
| `incident_id`     | INT  | **FK → incidents**, UNIQUE   | which incident           |
| `verified_by`     | INT  | **FK → admins**              | which admin checked it   |
| `status`          | ENUM | Verified / Rejected          | the decision             |
| `notes`           | TEXT |                              | optional notes           |
| `verified_at`     | TIMESTAMP | DEFAULT now             | when verified            |

> `incident_id` is **UNIQUE** → one incident has **one** verification (1:1).

### 3.6 `resolutions` — 1-to-1 with incidents
| Column            | Type | Key / rule                   | Meaning                  |
|-------------------|------|------------------------------|--------------------------|
| `resolution_id`   | INT  | **PK**                       | id of the resolution     |
| `incident_id`     | INT  | **FK → incidents**, UNIQUE   | which incident           |
| `resolved_by`     | INT  | **FK → admins**              | responsible admin        |
| `actions_taken`   | TEXT | NOT NULL                     | what was done            |
| `status`          | ENUM | Resolved/Closed/Reopened     | resolution status        |
| `completion_date` | TIMESTAMP | DEFAULT now             | when resolved            |

### 3.7 `notifications` — 1-to-many with incidents and users
| Column            | Type | Key / rule                 | Meaning                    |
|-------------------|------|----------------------------|----------------------------|
| `notification_id` | INT  | **PK**                     | id of the notification     |
| `incident_id`     | INT  | **FK → incidents**         | what it is about           |
| `recipient_id`    | INT  | **FK → users**             | who receives it            |
| `message`         | VARCHAR(255) | NOT NULL           | the text                   |
| `type`            | ENUM | System / Email / SMS       | how it was sent            |
| `status`          | ENUM | Unread / Read              | read state                 |
| `created_at`      | TIMESTAMP | DEFAULT now           | when created               |

> One incident can generate **many** notifications → **1-to-many**.

---

## 4. The relationships (THE most important viva topic)

| Relationship                         | Type | How it is enforced                              |
|--------------------------------------|------|-------------------------------------------------|
| users ↔ user_profiles                | 1:1  | `user_profiles.user_id` is a **UNIQUE FK**      |
| users → incidents (reports)          | 1:N  | `incidents.reported_by` FK → users              |
| admins → incidents (assigned to)     | 1:N  | `incidents.assigned_to` FK → admins             |
| incidents ↔ verifications            | 1:1  | `verifications.incident_id` is a **UNIQUE FK**  |
| admins → verifications (verified by) | 1:N  | `verifications.verified_by` FK → admins         |
| incidents ↔ resolutions              | 1:1  | `resolutions.incident_id` is a **UNIQUE FK**    |
| admins → resolutions (responsible)   | 1:N  | `resolutions.resolved_by` FK → admins           |
| incidents → notifications (generates)| 1:N  | `notifications.incident_id` FK → incidents      |
| users → notifications (receives)     | 1:N  | `notifications.recipient_id` FK → users         |

**How to read "1:N" out loud:** *"One user can report many incidents, but each
incident is reported by exactly one user."*

**How to read "1:1" out loud:** *"One incident has exactly one verification, and
each verification belongs to exactly one incident — enforced by a UNIQUE
foreign key."*

This project deliberately uses **only 1:1 and 1:N** relationships (no
many-to-many) to keep the design clean. *(If asked about many-to-many: it
would need a third "junction" table holding two foreign keys — we did not need
one here.)*

---

## 5. Normalization (be ready for this)

The database is in **Third Normal Form (3NF)**. Quick way to defend it:

- **1NF (atomic values):** every column holds a single value — no lists, no
  repeating groups. ✔
- **2NF (no partial dependency):** every table has a single-column primary key
  (`*_id`), so no non-key column depends on only *part* of the key. ✔
- **3NF (no transitive dependency):** non-key columns depend **only** on the
  primary key, not on another non-key column. For example, the admin's name is
  **not** copied into `incidents`; we only store `assigned_to` (the admin's id)
  and look the name up by a JOIN. ✔

**One-line answer:** *"Every non-key attribute depends on the key, the whole
key, and nothing but the key — so it's in 3NF."*

---

## 6. Constraints & referential integrity

- **Referential integrity** = a foreign key must point to a row that actually
  exists. MySQL (InnoDB) enforces this — you cannot insert an incident for a
  `reported_by` user that does not exist.
- **ON DELETE CASCADE** (used on most child tables): if a parent row is
  deleted, its children are deleted too. *Example:* delete a user → their
  incidents, profile and notifications are automatically removed. This avoids
  orphan rows.
- **ON DELETE SET NULL** (used on `incidents.assigned_to`): if an admin is
  deleted, the incident is **kept** but its `assigned_to` becomes NULL — we
  don't want to lose incident records just because a staff member left.
- **ENUM** restricts a column to a fixed set of valid values.
- **UNIQUE** on `email` stops duplicate accounts; UNIQUE on the `incident_id`
  foreign keys creates the 1:1 relationships.

---

## 7. The important SQL queries (and where they are)

All of these are in `app.py`. Here are the ones an examiner is most likely to
ask about.

**a) Insert a new incident** (when a user reports one):
```sql
INSERT INTO incidents (reported_by, title, description, category, severity, location)
VALUES (%s, %s, %s, %s, %s, %s);
```

**b) Show a user only their own incidents** (the WHERE filter):
```sql
SELECT incident_id, title, category, severity, status, reported_at
FROM incidents
WHERE reported_by = %s
ORDER BY reported_at DESC;
```

**c) JOIN — show an incident with its reporter and assigned admin:**
```sql
SELECT i.*, u.name AS reporter_name, a.name AS admin_name
FROM incidents i
JOIN users  u ON i.reported_by = u.user_id      -- inner join: reporter always exists
LEFT JOIN admins a ON i.assigned_to = a.admin_id -- left join: admin may be NULL
WHERE i.incident_id = %s;
```
> **Why LEFT JOIN for the admin?** Because an incident might **not** be assigned
> yet (`assigned_to` is NULL). An INNER JOIN would hide such incidents; a LEFT
> JOIN keeps them and just shows NULL for the admin.

**d) GROUP BY — count incidents per status** (admin dashboard tabs):
```sql
SELECT status, COUNT(*) AS c
FROM incidents
GROUP BY status;
```

**e) UPDATE — assign an incident to an admin:**
```sql
UPDATE incidents
SET assigned_to = %s, status = 'Assigned', assigned_at = CURRENT_TIMESTAMP
WHERE incident_id = %s;
```

> **Why `%s` and not the value directly?** These are **parameterized queries**.
> The value is passed separately to the driver, which prevents **SQL
> injection**. (Good bonus point to mention.)

---

## 8. Likely viva questions — with short answers

**Q: How many tables and why?**
A: Seven. One per real-world entity (users, profiles, admins, incidents,
verifications, resolutions, notifications), so each fact is stored once.

**Q: What is your primary key strategy?**
A: Every table has a surrogate `*_id` integer primary key with AUTO_INCREMENT.
Surrogate keys are stable and simple to reference from foreign keys.

**Q: Show me a one-to-one relationship.**
A: `incidents` ↔ `verifications`. `verifications.incident_id` is a UNIQUE
foreign key, so an incident can have only one verification.

**Q: Show me a one-to-many relationship.**
A: `users` → `incidents`. One user reports many incidents; each incident has
one `reported_by`.

**Q: How do you prevent duplicate users?**
A: `email` is declared UNIQUE, so MySQL rejects a second row with the same
email. The app also checks first and shows a friendly message.

**Q: What happens if you delete a user who has incidents?**
A: ON DELETE CASCADE removes that user's incidents, profile and notifications
automatically, so there are no orphan rows.

**Q: Why keep the incident if its admin is deleted?**
A: That FK uses ON DELETE SET NULL — incident records are valuable, so we keep
them and just clear the assignment.

**Q: Is the database normalized?**
A: Yes, 3NF — explained in section 5: atomic columns, full dependency on the
key, no transitive dependencies (we store admin **ids**, not their names).

**Q: How are passwords stored?**
A: Hashed (with Werkzeug's `generate_password_hash`), never in plain text.

**Q: How do you join tables?**
A: With the `JOIN ... ON` clause on the foreign key = primary key columns —
see section 7c.

---

## 9. One-paragraph summary (memorize this)

> *"The Incident Reporting System uses a MySQL relational database of seven
> tables centred on the `incidents` table. Users report incidents; admins
> verify, assign and resolve them; and notifications keep users informed.
> Relationships are built with primary and foreign keys — one-to-one links
> (incident–verification, incident–resolution, user–profile) are enforced with
> UNIQUE foreign keys, and one-to-many links (user–incidents,
> incident–notifications) with ordinary foreign keys. The schema is in 3NF,
> uses ENUMs and constraints to keep data valid, and uses ON DELETE rules to
> protect referential integrity."*
