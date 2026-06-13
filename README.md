# Incident Reporting System

A Database Systems project: users report incidents, admins verify / assign /
resolve them, and the reporter is notified — all stored in a **MySQL**
relational database.

**Stack:** MySQL 8.0 (portable) · Python + Flask (raw SQL) · HTML / CSS / JS

---

## How to run it (after first-time setup is done)

You only need **two windows**, started in order:

1. **Double-click `1 - Start MySQL.bat`** — starts the database. *Leave it open.*
2. **Double-click `2 - Start App.bat`** — starts the web app.
3. Open your browser at **http://127.0.0.1:5000**

To stop: close both black windows.

---

## Demo logins

| Role  | Email               | Password     |
|-------|---------------------|--------------|
| User  | alice@example.com   | password123  |
| User  | bilal@example.com   | password123  |
| Admin | admin@example.com   | admin123     |
| Admin | sara@example.com    | sara123      |

---

## The end-to-end flow (good to demo in viva)

1. **User** logs in → **Report Incident** (title, description, category, severity, location).
2. Incident is saved with status **Pending**; the user gets a **notification**.
3. **Admin** logs in → opens the incident → **Verifies** it (Verified / Rejected).
4. Admin **Assigns** it to a staff member → status becomes **Assigned**.
5. Admin **Resolves** it (records the actions taken) → status becomes **Resolved**.
6. The **user** sees every status change under **Notifications** and on the
   incident's tracking page.

---

## Files

| File / folder            | What it is                                              |
|--------------------------|---------------------------------------------------------|
| `database/schema.sql`    | **The database** — all 7 tables, keys, constraints.     |
| `setup_database.py`      | Creates the DB and inserts demo data (run once).        |
| `app.py`                 | Flask backend — every SQL query lives here.             |
| `db.py`, `config.py`     | Database connection settings + helper.                  |
| `templates/`, `static/`  | Frontend (HTML pages + CSS). *Not asked about in viva.* |
| `DATABASE_EXPLAINER.md`  | **Read this for viva** — explains the whole database.   |

---

## If you ever need to rebuild the database from scratch

With the MySQL window running:

```
python setup_database.py
```

This drops and recreates all tables and re-inserts the demo data.
