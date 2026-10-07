import pytest

from app import PROGRAMS, app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
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


def test_unknown_program_returns_not_found(client):
    response = client.get("/program/Unknown")

    assert response.status_code == 404