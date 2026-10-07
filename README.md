# ACEest Fitness & Gym

Version 1.1 is a Flask web presentation of the ACEest program catalog with a simple client profile workflow. It provides three fitness profiles with their weekly workout and nutrition plans:

- Fat Loss (FL)
- Muscle Gain (MG)
- Beginner (BG)

It also displays the original gym reference metrics: capacity, area, and break-even membership count.

The client profile form accepts a name, age, weight, program, and weekly adherence percentage. Estimated calories are calculated from the client weight and the selected program's calorie factor. Client data is not persisted yet.

## Run locally

Create and activate a virtual environment, then install Flask:

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

Open `http://127.0.0.1:5000` in a browser and select a program to view its plan.

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

The GitHub Actions workflow runs syntax checks, Pytest, the Docker build, and Pytest inside the built image on every push and pull request. Jenkins integration will be added separately.
