# ACEest Fitness & Gym

[![Release](https://img.shields.io/badge/release-v3.2.4-2f855a)](https://github.com/IonMind/2024tm93240-ACEest_Fitness_Gym/releases/tag/v3.2.4)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-222222?logo=flask&logoColor=white)
[![Build and test](https://github.com/IonMind/2024tm93240-ACEest_Fitness_Gym/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/IonMind/2024tm93240-ACEest_Fitness_Gym/actions/workflows/main.yml)

ACEest Fitness & Gym is a Flask application for managing fitness programs, client profiles, progress, workouts, and body metrics. The current application release is **v3.2.4**.

## Features

- Fitness program catalog:
	- Fat Loss (FL) – 3 day
	- Fat Loss (FL) – 5 day
	- Muscle Gain (MG) – PPL
	- Beginner (BG)
- Client profiles with age, height, weight, goals, adherence, and coach notes
- Username/password login with hashed password storage
- Membership expiry dates on client profiles
- Active, expired, and unset membership status checks
- Estimated daily calories based on weight and selected program
- SQLite persistence for clients and weekly progress
- Workout and exercise logging
- Body metric logging for weight, waist, and body fat
- Adherence history with a visual progress chart
- Workout history and latest body metrics
- BMI calculation and category display
- Experience-based workout plan generation
- Randomized program recommendations saved to client history
- Weight trend chart from recorded body metrics
- Downloadable PDF client reports
- CSV export for saved clients
- Non-root Docker image build and automated GitHub Actions validation

The original gym reference metrics are also displayed: capacity of 150 users, area of 10,000 sq ft, and break-even at 250 members.

## Run locally

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
```

Open `http://127.0.0.1:5000` in a browser.

The initial local administrator account is `admin` / `admin`. Set `ACEEST_ADMIN_USERNAME`, `ACEEST_ADMIN_PASSWORD`, and `ACEEST_SECRET_KEY` before deploying outside local development. The default account is created only when the users table is first initialized; passwords are stored as hashes.

By default, the application stores data in `aceest_fitness.db`. To use another database path:

$env:ACEEST_DB_PATH = "data\aceest_fitness.db"
python app.py


## Main routes

| Route | Purpose |
| --- | --- |
| `/login` | Sign in to the application |
| `/logout` | End the current session with `POST` |
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
| `/client/<name>/generate-program` | Generate a workout plan with `POST` |
| `/client/<name>/generate-random-program` | Generate and save a randomized recommendation with `POST` |
| `/client/<name>/membership` | Check membership status and expiry |
| `/client/<name>/report.pdf` | Download a client PDF report |
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

The workflow in `.github/workflows/main.yml` runs on every push and pull request. The dedicated `.github/workflows/pr-check.yml` adds an explicit required-looking PR validation check on pull requests targeting `master`. The workflows perform:

1. Python dependency installation
2. Application compilation check
3. Pytest execution
4. Docker image build
5. Pytest execution inside the Docker image

The `Jenkinsfile` cleans the workspace, checks out the branch source, creates a fresh Python virtual environment, compiles the application, and runs Pytest with JUnit test results. Its Jenkins agent needs Python 3, `venv`, and shell support.

For Jenkins, create a **Multibranch Pipeline** job connected to this GitHub repository and set the script path to `Jenkinsfile`. Scan the repository to discover branches, then build the branch job. A webhook is optional when branch scans and builds are started manually.

## GitHub releases

To create a release, merge the release branch into `master`, create a version tag, and push the tag:

```powershell
git tag -a v3.2.4 -m "Release version 3.2.4"
git push origin v3.2.4
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
- `v3.0.1`: Expanded program catalog with program descriptions and variants
- `v3.1.2`: Login, membership expiry, generated workout plans, and PDF client reports
- `v3.2.4`: Membership status checks, randomized program history, and weight trend chart
