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
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                date TEXT NOT NULL,
                workout_type TEXT NOT NULL,
                duration_min INTEGER,
                notes TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                sets INTEGER,
                reps INTEGER,
                weight REAL
            );
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                date TEXT NOT NULL,
                weight REAL,
                waist REAL,
                bodyfat REAL
            );
            """
        )
        client_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(clients)")
        }
        for column, definition in {
            "height": "REAL",
            "target_weight": "REAL",
            "target_adherence": "INTEGER",
        }.items():
            if column not in client_columns:
                connection.execute(f"ALTER TABLE clients ADD COLUMN {column} {definition}")


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
        "progress_entries": [],
        "workouts": [],
        "latest_metric": None,
        "bmi": None,
        "bmi_category": None,
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
        "height": request.form.get("height", "").strip(),
        "weight": request.form.get("weight", "").strip(),
        "program": request.form.get("program", "").strip(),
        "adherence": request.form.get("adherence", "0").strip(),
        "notes": request.form.get("notes", "").strip(),
        "target_weight": request.form.get("target_weight", "").strip(),
        "target_adherence": request.form.get("target_adherence", "").strip(),
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
            INSERT INTO clients
                (name, age, height, weight, program, calories, adherence, notes,
                 target_weight, target_adherence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                age=excluded.age, height=excluded.height, weight=excluded.weight,
                program=excluded.program, calories=excluded.calories,
                adherence=excluded.adherence, notes=excluded.notes,
                target_weight=excluded.target_weight,
                target_adherence=excluded.target_adherence
            """,
            (
                client["name"], client["age"] or None, client["height"] or None,
                client["weight"] or None, client["program"], calories,
                client["adherence"] or 0, client["notes"],
                client["target_weight"] or None, client["target_adherence"] or None,
            ),
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
    with database_connection() as connection:
        client = connection.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
    progress_entries = progress_for(name)
    return render_template("index.html", **page_context(
        client=dict(client) if client else None,
        selected_program=PROGRAMS.get(client["program"]) if client else None,
        selected_name=client["program"] if client else None,
        progress_entries=progress_entries,
        status="Weekly progress logged.",
    ))


@app.post("/workouts")
def save_workout():
    workout = {
        "client_name": request.form.get("client_name", "").strip(),
        "date": request.form.get("date", "").strip(),
        "workout_type": request.form.get("workout_type", "").strip(),
        "duration_min": request.form.get("duration_min", "").strip(),
        "notes": request.form.get("notes", "").strip(),
        "exercise_name": request.form.get("exercise_name", "").strip(),
        "sets": request.form.get("sets", "").strip(),
        "reps": request.form.get("reps", "").strip(),
        "weight": request.form.get("exercise_weight", "").strip(),
    }
    if not workout["client_name"] or not workout["date"] or not workout["workout_type"]:
        return render_template("index.html", **page_context(error="Client, date, and workout type are required.")), 400

    initialize_database()
    with database_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO workouts (client_name, date, workout_type, duration_min, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                workout["client_name"], workout["date"], workout["workout_type"],
                workout["duration_min"] or None, workout["notes"],
            ),
        )
        if workout["exercise_name"]:
            connection.execute(
                "INSERT INTO exercises (workout_id, name, sets, reps, weight) VALUES (?, ?, ?, ?, ?)",
                (
                    cursor.lastrowid, workout["exercise_name"], workout["sets"] or None,
                    workout["reps"] or None, workout["weight"] or None,
                ),
            )
    return render_template("index.html", **page_context(status="Workout logged successfully."))


@app.post("/metrics")
def save_metrics():
    metric = {
        "client_name": request.form.get("client_name", "").strip(),
        "date": request.form.get("date", "").strip(),
        "weight": request.form.get("weight", "").strip(),
        "waist": request.form.get("waist", "").strip(),
        "bodyfat": request.form.get("bodyfat", "").strip(),
    }
    if not metric["client_name"] or not metric["date"]:
        return render_template("index.html", **page_context(error="Client and date are required.")), 400

    initialize_database()
    with database_connection() as connection:
        connection.execute(
            "INSERT INTO metrics (client_name, date, weight, waist, bodyfat) VALUES (?, ?, ?, ?, ?)",
            (metric["client_name"], metric["date"], metric["weight"] or None,
             metric["waist"] or None, metric["bodyfat"] or None),
        )
    return render_template("index.html", **page_context(status="Body metrics logged successfully."))


def progress_for(name):
    initialize_database()
    with database_connection() as connection:
        return [
            dict(row)
            for row in connection.execute(
                "SELECT week, adherence FROM progress WHERE client_name = ? ORDER BY id",
                (name,),
            )
        ]


def workouts_for(name):
    initialize_database()
    with database_connection() as connection:
        return [
            dict(row)
            for row in connection.execute(
                """
                SELECT workouts.date, workouts.workout_type, workouts.duration_min,
                       workouts.notes, exercises.name AS exercise_name,
                       exercises.sets, exercises.reps, exercises.weight AS exercise_weight
                FROM workouts
                LEFT JOIN exercises ON exercises.workout_id = workouts.id
                WHERE workouts.client_name = ?
                ORDER BY workouts.date DESC, workouts.id DESC
                """,
                (name,),
            )
        ]


def latest_metric_for(name):
    initialize_database()
    with database_connection() as connection:
        row = connection.execute(
            "SELECT * FROM metrics WHERE client_name = ? ORDER BY date DESC, id DESC LIMIT 1",
            (name,),
        ).fetchone()
    return dict(row) if row else None


@app.get("/client/<path:name>/progress")
def show_progress(name):
    initialize_database()
    with database_connection() as connection:
        row = connection.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()

    if row is None:
        abort(404)

    client = dict(row)
    return render_template("index.html", **page_context(
        client=client,
        selected_program=PROGRAMS[client["program"]],
        selected_name=client["program"],
        summary=client,
        progress_entries=progress_for(name),
        workouts=workouts_for(name),
        latest_metric=latest_metric_for(name),
    ))


@app.get("/client/<path:name>/bmi")
def show_bmi(name):
    initialize_database()
    with database_connection() as connection:
        row = connection.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
    if row is None:
        abort(404)

    client = dict(row)
    height = float(client["height"] or 0)
    weight = float(client["weight"] or 0)
    bmi = round(weight / ((height / 100) ** 2), 1) if height > 0 and weight > 0 else None
    category = None
    if bmi is not None:
        category = "Underweight" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
    return render_template("index.html", **page_context(
        client=client,
        selected_program=PROGRAMS[client["program"]],
        selected_name=client["program"],
        summary=client,
        bmi=bmi,
        bmi_category=category,
        progress_entries=progress_for(name),
        workouts=workouts_for(name),
        latest_metric=latest_metric_for(name),
    ))


@app.get("/client/<path:name>/workouts")
def show_workouts(name):
    initialize_database()
    with database_connection() as connection:
        row = connection.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
    if row is None:
        abort(404)

    client = dict(row)
    return render_template("index.html", **page_context(
        client=client,
        selected_program=PROGRAMS[client["program"]],
        selected_name=client["program"],
        summary=client,
        progress_entries=progress_for(name),
        workouts=workouts_for(name),
        latest_metric=latest_metric_for(name),
    ))


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
