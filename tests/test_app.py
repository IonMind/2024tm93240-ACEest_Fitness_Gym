import pytest

from app import PROGRAMS, app


@pytest.fixture()
def client(tmp_path):
    app.config.update(TESTING=True)
    app.config["DATABASE"] = str(tmp_path / "test.db")
    with app.test_client() as test_client:
        yield test_client


def test_home_page_lists_all_programs(client):
    response = client.get("/")

    assert response.status_code == 200
    for program_name in PROGRAMS:
        assert program_name.encode() in response.data


@pytest.mark.parametrize(
    ("program_name", "expected_text"),
    [
        ("Fat Loss (FL)", "Back Squat 5x5 + Core"),
        ("Muscle Gain (MG)", "Deadlift 4x6"),
        ("Beginner (BG)", "Technique &amp; Consistency"),
    ],
)
def test_program_page_displays_workout(client, program_name, expected_text):
    response = client.get(f"/program/{program_name}")

    assert response.status_code == 200
    assert expected_text.encode() in response.data


def test_program_page_displays_nutrition_plan(client):
    response = client.get("/program/Fat%20Loss%20(FL)")

    assert response.status_code == 200
    assert b"Grilled Chicken + Brown Rice" in response.data


def test_client_profile_calculates_estimated_calories(client):
    response = client.post(
        "/client",
        data={
            "name": "Asha",
            "age": "30",
            "weight": "70",
            "program": "Muscle Gain (MG)",
            "adherence": "85",
        },
    )

    assert response.status_code == 200
    assert b"Estimated calories: 2450 kcal" in response.data


def test_client_profile_requires_name_and_program(client):
    response = client.post("/client", data={"name": "", "program": ""})

    assert response.status_code == 400
    assert b"Client name and program are required." in response.data


def test_multiple_clients_are_listed_with_notes(client):
    client.post(
        "/client",
        data={
            "name": "Asha",
            "age": "30",
            "weight": "70",
            "program": "Muscle Gain (MG)",
            "adherence": "85",
            "notes": "Increase weekly volume",
        },
    )
    response = client.post(
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
    client.post(
        "/client",
        data={
            "name": "Asha",
            "age": "30",
            "weight": "70",
            "program": "Muscle Gain (MG)",
            "adherence": "85",
        },
    )

    response = client.post("/client/load", data={"name": "Asha"})

    assert response.status_code == 200
    assert b"Client loaded." in response.data
    assert b"Calories: 2450 kcal/day" in response.data


def test_weekly_progress_is_saved(client):
    client.post(
        "/client",
        data={
            "name": "Asha",
            "program": "Beginner (BG)",
            "adherence": "80",
        },
    )

    response = client.post("/progress", data={"name": "Asha", "adherence": "80"})

    assert response.status_code == 200
    assert b"Weekly progress logged." in response.data


def test_progress_page_displays_adherence_history(client):
    client.post(
        "/client",
        data={"name": "Asha", "program": "Beginner (BG)", "adherence": "80"},
    )
    client.post("/progress", data={"name": "Asha", "adherence": "80"})
    client.post("/progress", data={"name": "Asha", "adherence": "95"})

    response = client.get("/client/Asha/progress")

    assert response.status_code == 200
    assert b"Weekly adherence progress" in response.data
    assert b"80%" in response.data
    assert b"95%" in response.data


def test_client_goals_and_bmi_are_available(client):
    client.post(
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

    response = client.get("/client/Asha/bmi")

    assert response.status_code == 200
    assert b">24.2</strong>" in response.data
    assert b"Normal" in response.data


def test_workout_and_metrics_history_are_available(client):
    client.post(
        "/client",
        data={"name": "Asha", "program": "Beginner (BG)"},
    )
    workout_response = client.post(
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
    metrics_response = client.post(
        "/metrics",
        data={
            "client_name": "Asha",
            "date": "2026-10-07",
            "weight": "70",
            "waist": "80",
            "bodyfat": "20",
        },
    )

    history_response = client.get("/client/Asha/workouts")

    assert workout_response.status_code == 200
    assert metrics_response.status_code == 200
    assert history_response.status_code == 200
    assert b"Air Squat" in history_response.data
    assert b"Good form" in history_response.data
    assert b"Latest body metrics" in history_response.data


def test_clients_can_be_exported_as_csv(client):
    client.post(
        "/client",
        data={
            "name": "Asha",
            "age": "30",
            "weight": "70",
            "program": "Muscle Gain (MG)",
            "adherence": "85",
            "notes": "Coach note",
        },
    )

    response = client.get("/clients/export.csv")

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert b"Name,Age,Weight,Program,Adherence,Notes" in response.data
    assert b"Asha,30,70,Muscle Gain (MG),85,Coach note" in response.data


def test_unknown_program_returns_not_found(client):
    response = client.get("/program/Unknown")

    assert response.status_code == 404