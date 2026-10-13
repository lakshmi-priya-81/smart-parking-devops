# SmartPark — Smart Parking Management System with DevOps Automation

A colourful, responsive Flask + SQLite demo application with a parking dashboard, slot reservations, check-in/release workflow, operations inventory, CSV export, health endpoint, Docker packaging, Jenkins pipeline, Ansible playbook and pytest checks.

## Features

- Vibrant dashboard with gradient hero, colourful statistics, parking-garage illustration, animated status accents and responsive layout.
- Dark and light themes; preference saved in the browser.
- Parking bay map with available/reserved/occupied status, vehicle and driver details.
- Search and status filters, plus quick status filter chips.
- Reserve an available bay, mark a vehicle checked in, or release a bay with confirmation.
- Occupancy donut chart and capacity summary.
- Operations/admin page with inventory search, recent audit trail and CSV export.
- SQLite persistence, JSON APIs, and `/health` endpoint for Docker/Jenkins.
- Docker volume for persistent database storage, Jenkins CI/CD example, Ansible deployment playbook, and automated pytest suite.

> This is a classroom/demo application. It is not connected to physical parking sensors, ANPR cameras, payment gateways, or a production authentication system. “Live” status reflects the current local database and refreshes when the page is reloaded.

## Required folder structure

Files must be in these folders (Flask looks for `templates/` and `static/`):

```text
Smart_Parking_DevOps_Project/
├── app.py
├── test_app.py
├── requirements.txt
├── Dockerfile
├── Jenkinsfile
├── README.md
├── .dockerignore
├── .gitignore
├── templates/   base.html  index.html  admin.html  _icons.html
├── static/      style.css  app.js
└── ansible/     deploy.yml  hosts.ini
```

`parking.db` is not needed — the app creates `data/parking.db` automatically on first run.

## Requirements

- Python 3.10+ (Python 3.12 recommended)
- Git Bash on Windows
- Docker Desktop for containerization
- Optional: GitHub, Jenkins and Ansible/WSL for the DevOps parts

## Run locally — Windows Git Bash

Open Git Bash in this project directory. If extracting to `E:\Smart_Parking_DevOps_Final\Smart_Parking_DevOps_Project`, run:

```bash
cd /e/Smart_Parking_DevOps_Final/Smart_Parking_DevOps_Project
py --version
py -m venv .venv
source .venv/Scripts/activate
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py -m pytest -v
py app.py
```

Open `http://127.0.0.1:5000`. Admin/operations is at `http://127.0.0.1:5000/admin`. Stop the server with `Ctrl+C`.

`requirements.txt` must contain one dependency per line:

```text
Flask==3.1.0
pytest==8.3.5
```

## Docker deployment

Start Docker Desktop and wait for it to report that the engine is running. From the project root:

```bash
docker --version
docker build -t smart-parking-app:latest .
docker volume create parking_data
docker rm -f smart-parking-app 2>/dev/null || true
docker run -d --name smart-parking-app --restart unless-stopped -p 5001:5000 -v parking_data:/app/data smart-parking-app:latest
docker ps
docker logs smart-parking-app
curl http://localhost:5001/health
curl http://localhost:5001/api/summary
```

Open `http://localhost:5001`. The host port is 5001; Flask listens on port 5000 inside the container. The named `parking_data` volume persists SQLite data across container replacement.

To stop/remove the container (the volume remains):

```bash
docker rm -f smart-parking-app
```

## Git and branching demonstration

If this is a new repository, from the project root:

```bash
git init
git add .
git commit -m "Initial SmartPark application"
git branch -M main
git checkout -b feature/dashboard-ui
# Make a small visible improvement, then:
git add .
git commit -m "Improve dashboard presentation"
git checkout main
git merge feature/dashboard-ui
git log --oneline --graph --all
```

Create an empty repository on GitHub, then use the actual URL GitHub gives you:

```bash
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
git push -u origin feature/dashboard-ui
```

Replace the placeholders; do not paste them literally.

## Jenkins

The supplied `Jenkinsfile` is a Linux-agent example. Configure a Jenkins Pipeline job linked to the Git repository and choose “Pipeline script from SCM” with `Jenkinsfile`. The agent needs Python 3, pip, pytest, Git, and Docker CLI access to a running Docker engine. Pipeline stages: checkout, install dependencies, automated tests, Docker build, container deployment and `/health` smoke test. A Windows-only Jenkins agent needs the shell commands adapted or should use a Linux agent.

## Ansible

Run from Linux/WSL where Ansible, Docker and the `community.docker` collection are installed:

```bash
ansible-galaxy collection install community.docker
ansible-playbook -i ansible/hosts.ini ansible/deploy.yml
```

Review `ansible/hosts.ini` and `ansible/deploy.yml` for the target host and deployment port before execution.

## Useful endpoints

- `/` — main dashboard
- `/admin` — operations dashboard
- `/admin/export.csv` — downloadable current inventory
- `/health` — machine-readable service/database health check (not a user-facing page)
- `/api/slots` — current bay inventory as JSON
- `/api/summary` — counts by status as JSON

## Evidence checklist for the report

Capture your own real screenshots of: dashboard, light/dark theme, slot reservation, check-in/release, admin inventory and CSV export, pytest output, Git history/branch merge, Docker image and running container, health endpoint, Jenkins successful build, and Ansible playbook output. Do not claim tools ran successfully until you have actually executed them.
