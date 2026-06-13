from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import SECRET_KEY
from db import get_connection

app = Flask(__name__)
app.secret_key = SECRET_KEY

def query_all(sql, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()
    finally:
        conn.close()

def query_one(sql, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchone()
    finally:
        conn.close()

def execute(sql, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            conn.commit()
            return cur.lastrowid
    finally:
        conn.close()

def add_notification(incident_id, recipient_id, message, ntype="System"):
    execute(
        """INSERT INTO notifications (incident_id, recipient_id, message, type)
           VALUES (%s, %s, %s, %s)""",
        (incident_id, recipient_id, message, ntype),
    )

def login_required(kind):
    return session.get("account_type") == kind

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        contact = request.form.get("contact_info", "").strip()
        department = request.form.get("department", "").strip()

        existing = query_one("SELECT user_id FROM users WHERE email = %s", (email,))
        if existing:
            flash("That email is already registered. Please log in.", "error")
            return redirect(url_for("login"))

        pw_hash = generate_password_hash(password)

        new_id = execute(
            """INSERT INTO users (name, email, password, contact_info)
               VALUES (%s, %s, %s, %s)""",
            (name, email, pw_hash, contact),
        )

        execute(
            "INSERT INTO user_profiles (user_id, department) VALUES (%s, %s)",
            (new_id, department),
        )

        flash("Account created! You can log in now.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = query_one("SELECT * FROM users WHERE email = %s", (email,))
        if user and check_password_hash(user["password"], password):
            session.clear()
            session["account_type"] = "user"
            session["user_id"] = user["user_id"]
            session["name"] = user["name"]
            return redirect(url_for("dashboard"))

        flash("Wrong email or password.", "error")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if not login_required("user"):
        return redirect(url_for("login"))
    uid = session["user_id"]

    incidents = query_all(
        """SELECT incident_id, title, category, severity, status, reported_at
             FROM incidents
            WHERE reported_by = %s
            ORDER BY reported_at DESC""",
        (uid,),
    )

    unread = query_one(
        """SELECT COUNT(*) AS c FROM notifications
            WHERE recipient_id = %s AND status = 'Unread'""",
        (uid,),
    )["c"]

    return render_template("dashboard.html", incidents=incidents, unread=unread)

@app.route("/report", methods=["GET", "POST"])
def report():
    if not login_required("user"):
        return redirect(url_for("login"))

    if request.method == "POST":
        uid = session["user_id"]
        incident_id = execute(
            """INSERT INTO incidents
                   (reported_by, title, description, category, severity, location)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                uid,
                request.form["title"].strip(),
                request.form["description"].strip(),
                request.form["category"],
                request.form["severity"],
                request.form.get("location", "").strip(),
            ),
        )

        add_notification(
            incident_id, uid,
            "Your incident was submitted and is now Pending review.",
        )
        flash("Incident reported successfully!", "success")
        return redirect(url_for("incident_detail", incident_id=incident_id))

    return render_template("report.html")

@app.route("/incident/<int:incident_id>")
def incident_detail(incident_id):
    if not login_required("user"):
        return redirect(url_for("login"))

    incident = query_one(
        """SELECT i.*,
                  u.name  AS reporter_name,
                  a.name  AS admin_name
             FROM incidents i
             JOIN users  u ON i.reported_by = u.user_id
        LEFT JOIN admins a ON i.assigned_to = a.admin_id
            WHERE i.incident_id = %s""",
        (incident_id,),
    )
    if not incident or incident["reported_by"] != session["user_id"]:
        flash("Incident not found.", "error")
        return redirect(url_for("dashboard"))

    verification = query_one(
        """SELECT v.*, a.name AS admin_name
             FROM verifications v JOIN admins a ON v.verified_by = a.admin_id
            WHERE v.incident_id = %s""",
        (incident_id,),
    )
    resolution = query_one(
        """SELECT r.*, a.name AS admin_name
             FROM resolutions r JOIN admins a ON r.resolved_by = a.admin_id
            WHERE r.incident_id = %s""",
        (incident_id,),
    )
    return render_template(
        "incident_detail.html",
        incident=incident, verification=verification, resolution=resolution,
    )

@app.route("/notifications")
def notifications():
    if not login_required("user"):
        return redirect(url_for("login"))
    uid = session["user_id"]

    rows = query_all(
        """SELECT n.*, i.title AS incident_title
             FROM notifications n
             JOIN incidents i ON n.incident_id = i.incident_id
            WHERE n.recipient_id = %s
            ORDER BY n.created_at DESC""",
        (uid,),
    )

    execute(
        "UPDATE notifications SET status = 'Read' WHERE recipient_id = %s",
        (uid,),
    )
    return render_template("notifications.html", notifications=rows)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        admin = query_one("SELECT * FROM admins WHERE email = %s", (email,))
        if admin and check_password_hash(admin["password"], password):
            session.clear()
            session["account_type"] = "admin"
            session["admin_id"] = admin["admin_id"]
            session["name"] = admin["name"]
            return redirect(url_for("admin_dashboard"))

        flash("Wrong email or password.", "error")

    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if not login_required("admin"):
        return redirect(url_for("admin_login"))

    status_filter = request.args.get("status", "All")
    if status_filter == "All":
        incidents = query_all(
            """SELECT i.*, u.name AS reporter_name
                 FROM incidents i JOIN users u ON i.reported_by = u.user_id
                ORDER BY i.reported_at DESC"""
        )
    else:
        incidents = query_all(
            """SELECT i.*, u.name AS reporter_name
                 FROM incidents i JOIN users u ON i.reported_by = u.user_id
                WHERE i.status = %s
                ORDER BY i.reported_at DESC""",
            (status_filter,),
        )

    counts = query_all(
        "SELECT status, COUNT(*) AS c FROM incidents GROUP BY status"
    )
    summary = {row["status"]: row["c"] for row in counts}
    summary["All"] = sum(summary.values())

    return render_template(
        "admin_dashboard.html",
        incidents=incidents, summary=summary, active=status_filter,
    )

@app.route("/admin/incident/<int:incident_id>")
def admin_incident(incident_id):
    if not login_required("admin"):
        return redirect(url_for("admin_login"))

    incident = query_one(
        """SELECT i.*, u.name AS reporter_name, u.email AS reporter_email,
                  a.name AS admin_name
             FROM incidents i
             JOIN users  u ON i.reported_by = u.user_id
        LEFT JOIN admins a ON i.assigned_to = a.admin_id
            WHERE i.incident_id = %s""",
        (incident_id,),
    )
    if not incident:
        flash("Incident not found.", "error")
        return redirect(url_for("admin_dashboard"))

    verification = query_one(
        "SELECT * FROM verifications WHERE incident_id = %s", (incident_id,)
    )
    resolution = query_one(
        "SELECT * FROM resolutions WHERE incident_id = %s", (incident_id,)
    )
    me = query_one("SELECT designation FROM admins WHERE admin_id = %s", (session["admin_id"],))
    if me and me["designation"] == "Support Staff":
        admins = query_all(
            "SELECT admin_id, name FROM admins WHERE admin_id <> %s AND designation <> 'Administrator' ORDER BY name",
            (session["admin_id"],),
        )
    else:
        admins = query_all(
            "SELECT admin_id, name FROM admins WHERE admin_id <> %s ORDER BY name",
            (session["admin_id"],),
        )

    return render_template(
        "admin_incident.html",
        incident=incident, verification=verification,
        resolution=resolution, admins=admins,
    )

@app.route("/admin/verify/<int:incident_id>", methods=["POST"])
def admin_verify(incident_id):
    if not login_required("admin"):
        return redirect(url_for("admin_login"))

    decision = request.form["decision"]
    notes = request.form.get("notes", "").strip()
    admin_id = session["admin_id"]

    execute(
        """INSERT INTO verifications (incident_id, verified_by, status, notes)
           VALUES (%s, %s, %s, %s)""",
        (incident_id, admin_id, decision, notes),
    )

    new_status = "Verified" if decision == "Verified" else "Rejected"
    execute(
        "UPDATE incidents SET status = %s WHERE incident_id = %s",
        (new_status, incident_id),
    )

    reporter = query_one(
        "SELECT reported_by FROM incidents WHERE incident_id = %s", (incident_id,)
    )
    add_notification(
        incident_id, reporter["reported_by"],
        f"Your incident was reviewed and marked: {new_status}.",
    )
    flash(f"Incident marked {new_status}.", "success")
    return redirect(url_for("admin_incident", incident_id=incident_id))

@app.route("/admin/assign/<int:incident_id>", methods=["POST"])
def admin_assign(incident_id):
    if not login_required("admin"):
        return redirect(url_for("admin_login"))

    assignee = int(request.form["assigned_to"])
    me_id = session["admin_id"]

    if assignee == me_id:
        flash("You cannot assign an incident to yourself.", "error")
        return redirect(url_for("admin_incident", incident_id=incident_id))

    me = query_one("SELECT designation FROM admins WHERE admin_id = %s", (me_id,))
    target = query_one("SELECT designation FROM admins WHERE admin_id = %s", (assignee,))
    if me and target and me["designation"] == "Support Staff" and target["designation"] == "Administrator":
        flash("Support staff cannot assign an incident to an administrator.", "error")
        return redirect(url_for("admin_incident", incident_id=incident_id))

    execute(
        """UPDATE incidents
              SET assigned_to = %s,
                  status      = 'Assigned',
                  assigned_at = CURRENT_TIMESTAMP
            WHERE incident_id = %s""",
        (assignee, incident_id),
    )
    reporter = query_one(
        "SELECT reported_by FROM incidents WHERE incident_id = %s", (incident_id,)
    )
    add_notification(
        incident_id, reporter["reported_by"],
        "Your incident has been assigned to a staff member.",
    )
    flash("Incident assigned.", "success")
    return redirect(url_for("admin_incident", incident_id=incident_id))

@app.route("/admin/resolve/<int:incident_id>", methods=["POST"])
def admin_resolve(incident_id):
    if not login_required("admin"):
        return redirect(url_for("admin_login"))

    verification = query_one("SELECT status FROM verifications WHERE incident_id = %s", (incident_id,))
    if not verification or verification["status"] != "Verified":
        flash("This incident must be verified before it can be resolved.", "error")
        return redirect(url_for("admin_incident", incident_id=incident_id))

    actions = request.form["actions_taken"].strip()
    admin_id = session["admin_id"]

    execute(
        """INSERT INTO resolutions (incident_id, resolved_by, actions_taken, status)
           VALUES (%s, %s, %s, 'Resolved')""",
        (incident_id, admin_id, actions),
    )
    execute(
        "UPDATE incidents SET status = 'Resolved' WHERE incident_id = %s",
        (incident_id,),
    )
    reporter = query_one(
        "SELECT reported_by FROM incidents WHERE incident_id = %s", (incident_id,)
    )
    add_notification(
        incident_id, reporter["reported_by"],
        "Good news - your incident has been Resolved.",
    )
    flash("Incident resolved.", "success")
    return redirect(url_for("admin_incident", incident_id=incident_id))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
