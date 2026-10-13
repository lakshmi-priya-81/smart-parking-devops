import os
import csv
import io
import sqlite3
from datetime import datetime
from pathlib import Path
from contextlib import closing
from flask import (Flask, render_template, request, redirect, url_for, flash, jsonify,
                   Response, send_from_directory, abort)

BASE_DIR = Path(__file__).resolve().parent
# Normal layout: templates/ and static/ folders next to app.py.
# Fallback: if every file was dropped flat into one folder, still run.
NESTED_LAYOUT = (BASE_DIR / "templates" / "base.html").exists()

if NESTED_LAYOUT:
    app = Flask(__name__, template_folder=str(BASE_DIR / "templates"),
                static_folder=str(BASE_DIR / "static"))
else:
    app = Flask(__name__, template_folder=str(BASE_DIR), static_folder=None)
    FLAT_STATIC = {"style.css", "app.js"}

    @app.get("/static/<path:filename>", endpoint="static")
    def flat_static(filename):
        if filename not in FLAT_STATIC:
            abort(404)
        return send_from_directory(str(BASE_DIR), filename)

app.secret_key = os.environ.get("SECRET_KEY", "change-this-for-production")
DB_PATH = os.environ.get("DB_PATH", str(BASE_DIR / "data" / "parking.db"))
TOTAL_SLOTS = max(1, min(int(os.environ.get("TOTAL_SLOTS", "12")), 200))
VALID_STATUSES = {"available", "reserved", "occupied"}


def db():
    """Open a connection. Use as: with closing(db()) as conn: (closes the file handle)."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout=10000")
    return connection


def init_db():
    with closing(db()) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS slots (
            id INTEGER PRIMARY KEY, label TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL DEFAULT 'available', vehicle_number TEXT,
            reserved_by TEXT, updated_at TEXT)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT, slot_label TEXT NOT NULL,
            action TEXT NOT NULL, detail TEXT, created_at TEXT NOT NULL)""")
        count = conn.execute("SELECT COUNT(*) FROM slots").fetchone()[0]
        if count == 0:
            conn.executemany("INSERT INTO slots(label,status) VALUES(?,'available')",
                             [(f"P-{i:02d}",) for i in range(1, TOTAL_SLOTS + 1)])
        conn.commit()


def record_activity(conn, label, action, detail=""):
    conn.execute("INSERT INTO activity(slot_label,action,detail,created_at) VALUES(?,?,?,?)",
                 (label, action, detail, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


_initialised = set()


@app.before_request
def ensure_database():
    if DB_PATH not in _initialised:
        init_db()
        _initialised.add(DB_PATH)


@app.get("/")
def index():
    with closing(db()) as conn:
        slots = conn.execute("SELECT * FROM slots ORDER BY id").fetchall()
        activity = conn.execute("SELECT * FROM activity ORDER BY id DESC LIMIT 6").fetchall()
    occupied = sum(s["status"] == "occupied" for s in slots)
    reserved = sum(s["status"] == "reserved" for s in slots)
    available = len(slots) - occupied - reserved
    return render_template("index.html", slots=slots, total=len(slots), occupied=occupied,
                           reserved=reserved, available=available, activity=activity,
                           occupancy=round((occupied / len(slots)) * 100) if slots else 0)


@app.post("/reserve/<int:sid>")
def reserve(sid):
    vehicle = request.form.get("vehicle_number", "").strip().upper()
    name = request.form.get("reserved_by", "").strip()
    if not vehicle or not name:
        flash("Add both the vehicle number and driver name to reserve a slot.", "error")
        return redirect(url_for("index"))
    if len(vehicle) > 20 or len(name) > 60:
        flash("Vehicle number or driver name is too long.", "error")
        return redirect(url_for("index"))
    with closing(db()) as conn:
        row = conn.execute("SELECT label FROM slots WHERE id=? AND status='available'", (sid,)).fetchone()
        if row:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("UPDATE slots SET status='reserved',vehicle_number=?,reserved_by=?,updated_at=? WHERE id=? AND status='available'",
                         (vehicle, name, now, sid))
            record_activity(conn, row["label"], "Slot reserved", f"{vehicle} · {name}")
            conn.commit()
            flash(f"{row['label']} is reserved for {vehicle}.", "success")
        else:
            flash("That slot is no longer available. Please choose another.", "error")
    return redirect(url_for("index"))


@app.post("/occupy/<int:sid>")
def occupy(sid):
    with closing(db()) as conn:
        row = conn.execute("SELECT label,status FROM slots WHERE id=?", (sid,)).fetchone()
        if row and row["status"] in ("available", "reserved"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("UPDATE slots SET status='occupied',updated_at=? WHERE id=?", (now, sid))
            record_activity(conn, row["label"], "Vehicle checked in", "Entry recorded by operator")
            conn.commit()
            flash(f"Vehicle entry recorded at {row['label']}.", "success")
        else:
            flash("This slot cannot be marked occupied.", "error")
    return redirect(url_for("index"))


@app.post("/release/<int:sid>")
def release(sid):
    with closing(db()) as conn:
        row = conn.execute("SELECT label,status,vehicle_number FROM slots WHERE id=?", (sid,)).fetchone()
        if row and row["status"] != "available":
            detail = row["vehicle_number"] or "Vehicle"
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("UPDATE slots SET status='available',vehicle_number=NULL,reserved_by=NULL,updated_at=? WHERE id=?",
                         (now, sid))
            record_activity(conn, row["label"], "Slot released", f"{detail} · slot available")
            conn.commit()
            flash(f"{row['label']} has been released and is available again.", "success")
        else:
            flash("This slot is already available or does not exist.", "error")
    return redirect(url_for("index"))


@app.get("/admin")
def admin():
    with closing(db()) as conn:
        slots = conn.execute("SELECT * FROM slots ORDER BY id").fetchall()
        activity = conn.execute("SELECT * FROM activity ORDER BY id DESC LIMIT 20").fetchall()
    counts = {status: sum(s["status"] == status for s in slots) for status in VALID_STATUSES}
    return render_template("admin.html", slots=slots, activity=activity, counts=counts, total=len(slots))


@app.get("/admin/export.csv")
def export_csv():
    """Download the current parking inventory as a CSV file for reporting."""
    with closing(db()) as conn:
        rows = conn.execute(
            "SELECT label, status, vehicle_number, reserved_by, updated_at FROM slots ORDER BY id"
        ).fetchall()
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["Bay ID", "Status", "Vehicle Number", "Driver", "Last Updated"])
    for row in rows:
        writer.writerow([row["label"], row["status"], row["vehicle_number"] or "",
                         row["reserved_by"] or "", row["updated_at"] or ""])
    return Response(output.getvalue(), mimetype="text/csv", headers={
        "Content-Disposition": "attachment; filename=smart-parking-inventory.csv"
    })


@app.get("/health")
def health():
    """Machine-readable health endpoint for Docker/Jenkins; not a user-facing page."""
    try:
        with closing(db()) as conn:
            conn.execute("SELECT 1").fetchone()
            slot_count = conn.execute("SELECT COUNT(*) FROM slots").fetchone()[0]
        return jsonify(status="ok", service="smart-parking", database="connected", slots=slot_count), 200
    except sqlite3.Error:
        return jsonify(status="error", service="smart-parking", database="unavailable"), 503


@app.get("/api/slots")
def api_slots():
    with closing(db()) as conn:
        rows = conn.execute("SELECT id,label,status,vehicle_number,reserved_by,updated_at FROM slots ORDER BY id").fetchall()
    return jsonify([dict(row) for row in rows])


@app.get("/api/summary")
def api_summary():
    with closing(db()) as conn:
        rows = conn.execute("SELECT status,COUNT(*) AS count FROM slots GROUP BY status").fetchall()
    counts = {status: 0 for status in VALID_STATUSES}
    counts.update({row["status"]: row["count"] for row in rows})
    counts["total"] = sum(counts[s] for s in VALID_STATUSES)
    return jsonify(counts)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
