import os
import pymysql
from werkzeug.security import generate_password_hash
from config import DB_CONFIG

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_FILE = os.path.join(HERE, "database", "schema.sql")

def run_schema():
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        sql_text = f.read()

    clean_lines = []
    for line in sql_text.splitlines():
        idx = line.find("--")
        if idx != -1:
            line = line[:idx]
        clean_lines.append(line)
    clean_sql = "\n".join(clean_lines)

    cfg = dict(DB_CONFIG)
    cfg.pop("database", None)
    conn = pymysql.connect(**cfg)
    try:
        with conn.cursor() as cur:

            for statement in clean_sql.split(";"):
                if statement.strip():
                    cur.execute(statement)
        conn.commit()
    finally:
        conn.close()
    print("  schema.sql executed - database and 7 tables created.")

def seed_data():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:

            admins = [
                ("System Admin", "admin@example.com", "admin123", "Administrator"),
                ("Sara Khan",    "sara@example.com",  "sara123",  "Support Staff"),
                ("Ali Raza",     "ali@example.com",   "ali123",   "Administrator"),
                ("Zara Sheikh",  "zara@example.com",  "zara123",  "Administrator"),
                ("Hina Malik",   "hina@example.com",  "hina123",  "Support Staff"),
                ("Omar Farooq",  "omar@example.com",  "omar123",  "Support Staff"),
            ]
            for name, email, pw, role in admins:
                cur.execute(
                    """INSERT INTO admins (name, email, password, designation)
                       VALUES (%s, %s, %s, %s)""",
                    (name, email, generate_password_hash(pw), role),
                )

            users = [
                ("Alice Johnson", "alice@example.com", "password123", "0300-1111111", "IT"),
                ("Bilal Ahmed",   "bilal@example.com", "password123", "0300-2222222", "Finance"),
            ]
            user_ids = []
            for name, email, pw, contact, dept in users:
                cur.execute(
                    """INSERT INTO users (name, email, password, contact_info)
                       VALUES (%s, %s, %s, %s)""",
                    (name, email, generate_password_hash(pw), contact),
                )
                uid = cur.lastrowid
                user_ids.append(uid)
                cur.execute(
                    "INSERT INTO user_profiles (user_id, department) VALUES (%s, %s)",
                    (uid, dept),
                )

            alice, bilal = user_ids

            cur.execute(
                """INSERT INTO incidents
                       (reported_by, title, description, category, severity, location, status)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (alice, "Wi-Fi not working in Block A",
                 "The wireless network keeps disconnecting every few minutes.",
                 "Technical", "Medium", "Block A", "Pending"),
            )
            inc1 = cur.lastrowid

            cur.execute(
                """INSERT INTO incidents
                       (reported_by, title, description, category, severity, location, status)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (bilal, "Suspicious login attempt",
                 "Someone tried to log into the finance portal multiple times.",
                 "Security", "High", "Finance Dept", "Verified"),
            )
            inc2 = cur.lastrowid

            cur.execute(
                """INSERT INTO verifications (incident_id, verified_by, status, notes)
                   VALUES (%s, 1, 'Verified', 'Confirmed from server logs.')""",
                (inc2,),
            )
            cur.execute(
                """INSERT INTO notifications (incident_id, recipient_id, message)
                   VALUES (%s, %s, 'Your incident was reviewed and marked: Verified.')""",
                (inc2, bilal),
            )
            cur.execute(
                """INSERT INTO notifications (incident_id, recipient_id, message)
                   VALUES (%s, %s, 'Your incident was submitted and is now Pending review.')""",
                (inc1, alice),
            )

        conn.commit()
        print("  Demo data inserted (6 admins, 2 users, 2 incidents).")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Setting up the Incident Reporting database...")
    run_schema()
    seed_data()
    print("\nDone! You can now run the app:  python app.py")
    print("Login pages:")
    print("  User  -> alice@example.com / password123")
    print("  Admin -> admin@example.com / admin123")
