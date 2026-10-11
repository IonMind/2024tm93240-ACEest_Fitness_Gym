# ACEest Fitness & Gym

ACEest Fitness & Gym is a Flask application for managing fitness programs, client profiles, progress, workouts, and body metrics. The current application release is **v2.2.4**.

## Features

- Fitness program catalog:
	- Fat Loss (FL)
	- Muscle Gain (MG)
	- Beginner (BG)
- Client profiles with age, height, weight, goals, adherence, and coach notes
- Estimated daily calories based on weight and selected program
- SQLite persistence for clients and weekly progress
- Workout and exercise logging
- Body metric logging for weight, waist, and body fat
- Adherence history with a visual progress chart
- Workout history and latest body metrics
- BMI calculation and category display
- CSV export for saved clients
- Docker image build and automated GitHub Actions validation

The original gym reference metrics are also displayed: capacity of 150 users, area of 10,000 sq ft, and break-even at 250 members.

## Run locally

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the application:

```powershell
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

By default, the application stores data in `aceest_fitness.db`. To use another database path:

```powershell
$env:ACEEST_DB_PATH = "data\aceest_fitness.db"
python app.py
```

## Main routes

| Route | Purpose |
| --- | --- |
| `/` | Program catalog and client dashboard |
| `/program/<program_name>` | View a program plan |
| `/client` | Save or update a client profile with `POST` |
| `/client/load` | Load a saved client with `POST` |
| `/progress` | Save weekly adherence with `POST` |
| `/client/<name>/progress` | View adherence history |
| `/workouts` | Log a workout and exercise with `POST` |
| `/client/<name>/workouts` | View workout history |
| `/metrics` | Log body metrics with `POST` |
| `/client/<name>/bmi` | View BMI classification |
| `/clients/export.csv` | Download saved clients as CSV |

## Tests

Install the dependencies and run the test suite:

```powershell
python -m pytest -q
```

## Docker

Build and run the application image:

```powershell
docker build -t aceest-fitness-gym .
docker run --rm -p 5000:5000 aceest-fitness-gym
```

## Continuous integration

The workflow in `.github/workflows/main.yml` runs on every push and pull request. It performs:

1. Python dependency installation
2. Application compilation check
3. Pytest execution
4. Docker image build
5. Pytest execution inside the Docker image

The `Jenkinsfile` defines the Jenkins BUILD stages: install Python dependencies, compile the application, and run Pytest with JUnit test results. The pipeline expects Jenkins to have the Docker Pipeline and JUnit plugins enabled, because it uses a `python:3.12-slim` Docker build agent.

## GitHub releases

To create a release, merge the release branch into `master`, create a version tag, and push the tag:

```powershell
git tag -a v2.3.0 -m "Release version 2.3.0"
git push origin v2.3.0
```

The workflow in `.github/workflows/release.yml` runs when a tag beginning with `v` is pushed. It verifies that the tagged commit is on `master` and creates a GitHub Release with automatically generated release notes.

## Release history

- `v1.0`: Initial Flask program catalog
- `v1.1`: Client profile and calorie estimation
- `v1.1.2`: Multiple clients, notes, adherence, and CSV export
- `v2.0.1`: SQLite client and progress persistence
- `v2.1.2`: Versioned persistence release
- `v2.2.1`: Adherence history and progress chart
- `v2.2.4`: Goals, workouts, exercises, body metrics, and BMI
