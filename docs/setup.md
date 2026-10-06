# Setup Guide: THE CLOCK IS RUNNING (Core Backend)

## Prerequisites
- Python 3.12+ (or 3.14+)
- Docker & Docker Compose (for PostgreSQL) OR a local PostgreSQL 16 instance

---

## 1. Environment Configuration

Copy the example environment configuration:
```bash
cp backend/.env.example backend/.env
```

Ensure `DATABASE_URL` is configured for your PostgreSQL instance:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/the_clock_is_running
SECRET_KEY=your-secure-random-secret-key-at-least-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## 2. Running with Docker Compose (PostgreSQL)

Start the PostgreSQL database service:
```bash
docker compose -f backend/docker-compose.yml up -d db
```

---

## 3. Running Backend Locally

Install the required dependencies:
```bash
pip install -r backend/requirements.txt
```

Run the FastAPI application with Uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir backend
```

Access the interactive API documentation:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **Health Check:** `http://localhost:8000/health`

---

## 4. Running the Test Suite

Execute the test suite with pytest:
```bash
pytest -q
```
or specifically for the backend test directory:
```bash
python -m pytest backend/tests -q
```
