import csv
import io

from flask import Flask, Response, abort, render_template, request

app = Flask(__name__)

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

CLIENTS = []


@app.get("/")
def home():
    return render_template(
        "index.html",
        programs=PROGRAMS,
        metrics=SITE_METRICS,
        selected_program=None,
        client=None,
        error=None,
        clients=CLIENTS,
    )


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
        return render_template(
            "index.html",
            programs=PROGRAMS,
            metrics=SITE_METRICS,
            selected_program=None,
            client=client,
            error="Client name and program are required.",
            clients=CLIENTS,
        ), 400

    selected_program = PROGRAMS.get(client["program"])
    if selected_program is None:
        return render_template(
            "index.html",
            programs=PROGRAMS,
            metrics=SITE_METRICS,
            selected_program=None,
            client=client,
            error="Select a valid program.",
            clients=CLIENTS,
        ), 400

    try:
        calories = int(float(client["weight"]) * selected_program["calorie_factor"])
    except (TypeError, ValueError):
        calories = None

    client["calories"] = calories
    CLIENTS.append(client)
    return render_template(
        "index.html",
        programs=PROGRAMS,
        metrics=SITE_METRICS,
        selected_program=selected_program,
        selected_name=client["program"],
        client=client,
        error=None,
        clients=CLIENTS,
    )


@app.get("/clients/export.csv")
def export_clients():
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["Name", "Age", "Weight", "Program", "Adherence", "Notes"])
    writer.writerows(
        [
            client["name"],
            client["age"],
            client["weight"],
            client["program"],
            client["adherence"],
            client["notes"],
        ]
        for client in CLIENTS
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

    return render_template(
        "index.html",
        programs=PROGRAMS,
        metrics=SITE_METRICS,
        selected_program=selected_program,
        selected_name=program_name,
        client=None,
        error=None,
        clients=CLIENTS,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
