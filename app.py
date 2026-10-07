import csv
import io
import os
import sqlite3
from datetime import datetime

from flask import Flask, Response, abort, render_template, request

app = Flask(__name__)
app.config["DATABASE"] = os.environ.get("ACEEST_DB_PATH", "aceest_fitness.db")

SITE_METRICS = {
    "capacity": "150 users",
    "area": "10,000 sq ft",
    "break_even": "250 members",
}

PROGRAMS = {
    "Fat Loss (FL)": {
        "workout": "Mon: Back Squat 5x5 + Core\nTue: EMOM 20min Assault Bike\nWed: Bench Press + 21-15-9\nThu: Deadlift + Box Jumps\nFri: Zone 2 Cardio 30min",
        "diet": "Breakfast: Egg Whites + Oats\nLunch: Grilled Chicken + Brown Rice\nDinner: Fish Curry + Millet Roti\nTarget: ~2000 kcal",
        "color": "#c0392b",
        "calorie_factor": 22,
    },
    "Muscle Gain (MG)": {
        "workout": "Mon: Squat 5x5\nTue: Bench 5x5\nWed: Deadlift 4x6\nThu: Front Squat 4x8\nFri: Incline Press 4x10\nSat: Barbell Rows 4x10",
        "diet": "Breakfast: Eggs + Peanut Butter Oats\nLunch: Chicken Biryani\nDinner: Mutton Curry + Rice\nTarget: ~3200 kcal",
        "color": "#218c5a",
        "calorie_factor": 35,
    },
    "Beginner (BG)": {
        "workout": "Full Body Circuit:\n- Air Squats\n- Ring Rows\n- Push-ups\nFocus: Technique & Consistency",
        "diet": "Balanced Tamil Meals\nIdli / Dosa / Rice + Dal\nProtein Target: 120g/day",
        "color": "#2474a8",
        "calorie_factor": 26,
    },
}

def database_connection():
    connection = sqlite3.connect(app.config["DATABASE"])
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with database_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                age INTEGER,
                weight REAL,
                program TEXT NOT NULL,
                calories INTEGER,
                adherence INTEGER DEFAULT 0,
                notes TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                week TEXT NOT NULL,
                adherence INTEGER NOT NULL
            );
            """
        )


def client_rows():
    initialize_database()
    with database_connection() as connection:
        return [dict(row) for row in connection.execute("SELECT * FROM clients ORDER BY name")]


def display_number(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return value


def page_context(**values):
    context = {
        "programs": PROGRAMS,
        "metrics": SITE_METRICS,
        "selected_program": None,
        "client": None,
        "error": None,
        "status": None,
        "clients": client_rows(),
        "summary": None,
    }
    context.update(values)
    return context


@app.get("/")
def home():
    return render_template("index.html", **page_context())


@app.post("/client")
def save_client():
    client = {
        "name": request.form.get("name", "").strip(),
        "age": request.form.get("age", "").strip(),
        "weight": request.form.get("weight", "").strip(),
        "program": request.form.get("program", "").strip(),
        "adherence": request.form.get("adherence", "0").strip(),
        "notes": request.form.get("notes", "").strip(),
    }

    if not client["name"] or not client["program"]:
        return render_template("index.html", **page_context(
            client=client,
            error="Client name and program are required.",
        )), 400

    selected_program = PROGRAMS.get(client["program"])
    if selected_program is None:
        return render_template("index.html", **page_context(
            client=client,
            error="Select a valid program.",
        )), 400

    try:
        calories = int(float(client["weight"]) * selected_program["calorie_factor"])
    except (TypeError, ValueError):
        calories = None

    client["calories"] = calories
    initialize_database()
    with database_connection() as connection:
        connection.execute(
            """
            INSERT INTO clients (name, age, weight, program, calories, adherence, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                age=excluded.age, weight=excluded.weight, program=excluded.program,
                calories=excluded.calories, adherence=excluded.adherence, notes=excluded.notes
            """,
            (client["name"], client["age"] or None, client["weight"] or None,
             client["program"], calories, client["adherence"] or 0, client["notes"]),
        )
    return render_template("index.html", **page_context(
        selected_program=selected_program,
        selected_name=client["program"],
        client=client,
        status="Client data saved.",
    ))


@app.post("/client/load")
def load_client():
    name = request.form.get("name", "").strip()
    initialize_database()
    with database_connection() as connection:
        row = connection.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()

    if row is None:
        return render_template("index.html", **page_context(error="Client not found.")), 404

    client = dict(row)
    return render_template("index.html", **page_context(
        client=client,
        selected_program=PROGRAMS[client["program"]],
        selected_name=client["program"],
        summary=client,
        status="Client loaded.",
    ))


@app.post("/progress")
def save_progress():
    name = request.form.get("name", "").strip()
    adherence = request.form.get("adherence", "0").strip()
    if not name:
        return render_template("index.html", **page_context(error="Client name is required.")), 400

    initialize_database()
    with database_connection() as connection:
        connection.execute(
            "INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
            (name, datetime.now().strftime("Week %U - %Y"), int(adherence or 0)),
        )
    return render_template("index.html", **page_context(status="Weekly progress logged."))


@app.get("/clients/export.csv")
def export_clients():
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["Name", "Age", "Weight", "Program", "Adherence", "Notes"])
    writer.writerows(
        [client["name"], client["age"], display_number(client["weight"]), client["program"], client["adherence"], client["notes"]]
        for client in client_rows()
    )
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=clients.csv"},
    )


@app.get("/program/<path:program_name>")
def show_program(program_name):
    selected_program = PROGRAMS.get(program_name)
    if selected_program is None:
        abort(404)

    return render_template("index.html", **page_context(
        selected_program=selected_program,
        selected_name=program_name,
    ))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
