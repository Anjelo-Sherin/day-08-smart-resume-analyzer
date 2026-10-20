# Setup & Installation Guide

This guide walks you through setting up **RoleFit AI** locally or with Docker Compose.

---

## Prerequisites

- **Python 3.9+** (tested on 3.9, 3.10, 3.11, 3.12)
- **Node.js 18+** & npm / pnpm
- **(Optional) Docker & Docker Compose** for containerized execution
- **(Optional) Gemini API Key** for live LLM bullet rewriting (works offline without a key)

---

## Local Development (Zero-Setup)

### 1. Clone the Repository
```bash
git clone https://github.com/Anjelo-Sherin/day-08-smart-resume-analyzer.git
cd day-08-smart-resume-analyzer
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
```
*(Optionally paste your `GEMINI_API_KEY` into `.env` if you want live `gemini-3.8-flash` rewrites).*

### 3. Setup and Run the FastAPI Backend
```bash
cd apps/api

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend service
PYTHONPATH=. uvicorn app.main:app --host 127.0.0.1 --port 8008 --reload
```
The backend will be available at `http://127.0.0.1:8008` (API docs at `http://127.0.0.1:8008/docs`).

### 4. Setup and Run the Next.js Frontend
In a new terminal:
```bash
cd day-08-smart-resume-analyzer/apps/web

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
Open **`http://localhost:3008`** in your browser.

---

## Running with Docker Compose

To spin up both services with one command:
```bash
docker compose up --build
```
- **Web UI:** `http://localhost:3008`
- **FastAPI API:** `http://localhost:8008`

---

## Running Automated Tests

```bash
cd apps/api
PYTHONPATH=. .venv/bin/python -m pytest -v
```
All 6 unit and integration tests should pass.
