from flask import Flask, abort, render_template

app = Flask(__name__)

SITE_METRICS = {
    "capacity": "150 users",
    "area": "10,000 sq ft",
    "break_even": "250 members",
}

PROGRAMS = {
    "Fat Loss (FL)": {
        "workout": "Mon: 5x5 Back Squat + AMRAP\nTue: EMOM 20min Assault Bike\nWed: Bench Press + 21-15-9\nThu: 10RFT Deadlifts/Box Jumps\nFri: 30min Active Recovery",
        "diet": "B: 3 Egg Whites + Oats Idli\nL: Grilled Chicken + Brown Rice\nD: Fish Curry + Millet Roti\nTarget: 2,000 kcal",
        "color": "#c0392b",
    },
    "Muscle Gain (MG)": {
        "workout": "Mon: Squat 5x5\nTue: Bench 5x5\nWed: Deadlift 4x6\nThu: Front Squat 4x8\nFri: Incline Press 4x10\nSat: Barbell Rows 4x10",
        "diet": "B: 4 Eggs + PB Oats\nL: Chicken Biryani (250g Chicken)\nD: Mutton Curry + Jeera Rice\nTarget: 3,200 kcal",
        "color": "#218c5a",
    },
    "Beginner (BG)": {
        "workout": "Circuit Training: Air Squats, Ring Rows, Push-ups.\nFocus: Technique Mastery & Form (90% Threshold)",
        "diet": "Balanced Tamil Meals: Idli-Sambar, Rice-Dal, Chapati.\nProtein: 120g/day",
        "color": "#2474a8",
    },
}


@app.get("/")
def home():
    return render_template(
        "index.html",
        programs=PROGRAMS,
        metrics=SITE_METRICS,
        selected_program=None,
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
    )


if __name__ == "__main__":
    app.run()
