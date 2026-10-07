# ACEest Fitness & Gym

Version 1 is a Flask web presentation of the original ACEest program catalog. It provides three read-only fitness profiles with their weekly workout and nutrition plans:

- Fat Loss (FL)
- Muscle Gain (MG)
- Beginner (BG)

It also displays the original gym reference metrics: capacity, area, and break-even membership count.

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

This initial version intentionally contains only the version-1 program catalog. Tests, Docker, Jenkins, and later application features will be added in subsequent releases.
