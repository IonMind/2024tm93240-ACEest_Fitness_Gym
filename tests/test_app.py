import pytest

from app import PROGRAMS, app, create_ai_program, database_connection, initialize_database


@pytest.fixture()
def client(tmp_path):
    app.config.update(TESTING=True)
    app.config["DATABASE"] = str(tmp_path / "test.db")
    initialize_database()
    with app.test_client() as test_client:
        yield test_client


def test_home_page_lists_all_programs(client):
    response = authenticated_client_get(client, "/")

    assert response.status_code == 200
    for program_name in PROGRAMS:
        assert program_name.encode() in response.data


def test_version_3_program_descriptions_and_calorie_factors(client):
    expected = {
        "Fat Loss (FL) – 3 day": (22, "3-day full-body fat loss"),
        "Fat Loss (FL) – 5 day": (24, "5-day split, higher volume fat loss"),
        "Muscle Gain (MG) – PPL": (35, "Push/Pull/Legs hypertrophy"),
        "Beginner (BG)": (26, "3-day simple beginner full-body"),
    }

    response = authenticated_client_get(client, "/")

    assert set(PROGRAMS) == set(expected)
    for name, (factor, description) in expected.items():
        assert PROGRAMS[name]["calorie_factor"] == factor
        assert description.encode() in response.data


@pytest.mark.parametrize(
    ("program_name", "expected_text"),
    [
        ("Fat Loss (FL) – 3 day", "Back Squat 5x5 + Core"),
        ("Fat Loss (FL) – 5 day", "Back Squat 5x5 + Core"),
        ("Muscle Gain (MG) – PPL", "Deadlift 4x6"),
        ("Beginner (BG)", "Technique &amp; Consistency"),
    ],
)
def test_program_page_displays_workout(client, program_name, expected_text):
    response = authenticated_client_get(client, f"/program/{program_name}")

    assert response.status_code == 200
    assert expected_text.encode() in response.data


def test_program_page_displays_nutrition_plan(client):
    response = authenticated_client_get(client, "/program/Fat%20Loss%20(FL)%20%E2%80%93%203%20day")

    assert response.status_code == 200
    assert b"Grilled Chicken + Brown Rice" in response.data


def test_client_profile_calculates_estimated_calories(client):
    response = authenticated_client_post(client,
        "/client",
        data={
            "name": "Asha",
            "age": "30",
            "weight": "70",
            "program": "Muscle Gain (MG) – PPL",
            "adherence": "85",
        },
    )

    assert response.status_code == 200
    assert b"Estimated calories: 2450 kcal" in response.data


def test_client_profile_requires_name_and_program(client):
    response = authenticated_client_post(client, "/client", data={"name": "", "program": ""})

    assert response.status_code == 400
    assert b"Client name and program are required." in response.data


def test_multiple_clients_are_listed_with_notes(client):
    authenticated_client_post(client,
        "/client",
        data={
            "name": "Asha",
            "age": "30",
            "weight": "70",
            "program": "Muscle Gain (MG) – PPL",
            "adherence": "85",
            "notes": "Increase weekly volume",
        },
    )
    response = authenticated_client_post(client,
        "/client",
        data={
            "name": "Ravi",
            "age": "25",
            "weight": "65",
            "program": "Beginner (BG)",
            "adherence": "60",
            "notes": "Focus on form",
        },
    )

    assert response.status_code == 200
    assert b"Asha" in response.data
    assert b"Ravi" in response.data
    assert b"Focus on form" in response.data


def test_saved_client_can_be_loaded(client):
    authenticated_client_post(client,
        "/client",
        data={
            "name": "Asha",
            "age": "30",
            "weight": "70",
            "program": "Muscle Gain (MG) – PPL",
            "adherence": "85",
        },
    )

    response = authenticated_client_post(client, "/client/load", data={"name": "Asha"})

    assert response.status_code == 200
    assert b"Client loaded." in response.data
    assert b"Calories: 2450 kcal/day" in response.data


def test_weekly_progress_is_saved(client):
    authenticated_client_post(client,
        "/client",
        data={
            "name": "Asha",
            "program": "Beginner (BG)",
            "adherence": "80",
        },
    )

    response = authenticated_client_post(client, "/progress", data={"name": "Asha", "adherence": "80"})

    assert response.status_code == 200
    assert b"Weekly progress logged." in response.data


def test_progress_page_displays_adherence_history(client):
    authenticated_client_post(client,
        "/client",
        data={"name": "Asha", "program": "Beginner (BG)", "adherence": "80"},
    )
    authenticated_client_post(client, "/progress", data={"name": "Asha", "adherence": "80"})
    authenticated_client_post(client, "/progress", data={"name": "Asha", "adherence": "95"})

    response = authenticated_client_get(client, "/client/Asha/progress")

    assert response.status_code == 200
    assert b"Weekly adherence progress" in response.data
    assert b"80%" in response.data
    assert b"95%" in response.data


def test_client_goals_and_bmi_are_available(client):
    authenticated_client_post(client,
        "/client",
        data={
            "name": "Asha",
            "height": "170",
            "weight": "70",
            "program": "Beginner (BG)",
            "target_weight": "65",
            "target_adherence": "90",
        },
    )

    response = authenticated_client_get(client, "/client/Asha/bmi")

    assert response.status_code == 200
    assert b">24.2</strong>" in response.data
    assert b"Normal" in response.data
    assert b"Low risk if active and strong." in response.data


def test_workout_and_metrics_history_are_available(client):
    authenticated_client_post(client,
        "/client",
        data={"name": "Asha", "program": "Beginner (BG)"},
    )
    workout_response = authenticated_client_post(client,
        "/workouts",
        data={
            "client_name": "Asha",
            "date": "2026-10-07",
            "workout_type": "Strength",
            "duration_min": "60",
            "exercise_name": "Air Squat",
            "sets": "3",
            "reps": "10",
            "exercise_weight": "20",
            "notes": "Good form",
        },
    )
    metrics_response = authenticated_client_post(client,
        "/metrics",
        data={
            "client_name": "Asha",
            "date": "2026-10-07",
            "weight": "70",
            "waist": "80",
            "bodyfat": "20",
        },
    )

    history_response = authenticated_client_get(client, "/client/Asha/workouts")

    assert workout_response.status_code == 200
    assert metrics_response.status_code == 200
    assert history_response.status_code == 200
    assert b"Air Squat" in history_response.data
    assert b"Good form" in history_response.data
    assert b"Latest body metrics" in history_response.data

    with database_connection() as connection:
        saved_client = connection.execute(
            "SELECT weight, calories FROM clients WHERE name = ?", ("Asha",)
        ).fetchone()
    assert saved_client["weight"] == 70
    assert saved_client["calories"] == 1820


def test_clients_can_be_exported_as_csv(client):
    authenticated_client_post(client,
        "/client",
        data={
            "name": "Asha",
            "age": "30",
            "weight": "70",
            "program": "Muscle Gain (MG) – PPL",
            "adherence": "85",
            "notes": "Coach note",
        },
    )

    response = authenticated_client_get(client, "/clients/export.csv")

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert b"Name,Age,Weight,Program,Adherence,Notes" in response.data
    assert b"Asha,30,70,Muscle Gain (MG) \xe2\x80\x93 PPL,85,Coach note" in response.data


def test_unknown_program_returns_not_found(client):
    response = authenticated_client_get(client, "/program/Unknown")

    assert response.status_code == 404


def authenticated_client_get(client, path):
    with client.session_transaction() as session:
        session["username"] = "admin"
        session["role"] = "Admin"
    return client.get(path)


def authenticated_client_post(client, path, data):
    with client.session_transaction() as session:
        session["username"] = "admin"
        session["role"] = "Admin"
    return client.post(path, data=data)


def test_login_authenticates_seeded_admin(client):
    response = client.post("/login", data={"username": "admin", "password": "admin"})

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_invalid_login_is_rejected(client):
    response = client.post("/login", data={"username": "admin", "password": "wrong"})

    assert response.status_code == 200
    assert b"Invalid username or password." in response.data


def test_protected_home_redirects_to_login(client):
    response = client.get("/")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_membership_expiry_is_saved_and_invalid_dates_rejected(client):
    saved = authenticated_client_post(
        client,
        "/client",
        data={
            "name": "Mira",
            "program": "Beginner (BG)",
            "membership_expiry": "2027-03-31",
        },
    )
    invalid = authenticated_client_post(
        client,
        "/client",
        data={
            "name": "Invalid Date",
            "program": "Beginner (BG)",
            "membership_expiry": "31/03/2027",
        },
    )

    assert saved.status_code == 200
    assert b"2027-03-31" in saved.data
    assert invalid.status_code == 400
    assert b"Membership expiry must be a valid date." in invalid.data
    with database_connection() as connection:
        row = connection.execute("SELECT membership_expiry FROM clients WHERE name = ?", ("Mira",)).fetchone()
    assert row["membership_expiry"] == "2027-03-31"


@pytest.mark.parametrize(
    ("experience", "expected_days"),
    [("beginner", 3), ("intermediate", 4), ("advanced", 5)],
)
def test_ai_program_generation_returns_level_sized_plan(experience, expected_days):
    plan = create_ai_program("Fat Loss (FL) – 3 day", experience)

    assert len(plan) == expected_days * (3 if expected_days < 4 else 4)
    all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    assert {item["day"] for item in plan} == set(all_days[:expected_days])
    assert len({item["day"] for item in plan}) == expected_days
    assert all(2 <= item["sets"] <= 5 and 6 <= item["reps"] <= 15 for item in plan)


def test_ai_program_generation_rejects_invalid_experience(client):
    with pytest.raises(ValueError):
        create_ai_program("Beginner (BG)", "expert")


def test_generated_plan_route_renders_workout_rows(client):
    authenticated_client_post(
        client,
        "/client",
        data={"name": "Mira", "program": "Beginner (BG)"},
    )
    response = authenticated_client_post(
        client,
        "/client/Mira/generate-program",
        data={"experience": "beginner"},
    )

    assert response.status_code == 200
    assert b"Generated workout plan" in response.data
    assert b"Monday" in response.data


def test_client_pdf_report_download(client):
    authenticated_client_post(
        client,
        "/client",
        data={"name": "Mira", "age": "31", "program": "Beginner (BG)", "membership_expiry": "2027-03-31"},
    )
    response = authenticated_client_get(client, "/client/Mira/report.pdf")

    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF")
    assert "Mira_report.pdf" in response.headers["Content-Disposition"]