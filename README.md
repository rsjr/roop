# ROOP

Rogerio's Offshore Operations Platform

Service

## Prerequisites

- Docker and Docker Compose
- Git (to clone the repository)

## Quick Start from Scratch

### 1. Setup env

Clone the repository and go to the repo folder :)
Then:
```bash
# Create environment file (optional - uses defaults if not created)
cp .env.example .env
# Edit .env if you want to customize database credentials or other settings
```

### 2. Build and Start Services

```bash
# Build Docker images
make docker-build

# Start all services (database + API)
make docker-up

# Check that services are running
docker compose ps
```

### 4. Run Database Migrations

```bash
# Run migrations to set up the database schema
docker compose exec api uv run alembic revision --autogenerate -m "initial migration"
# if you see this error FAILED: Target database is not up to date. don't panic :). Just move on.
docker compose exec api uv run alembic upgrade head
```

### 5. Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Expected response: {"status": "healthy"}
```

## Service URLs

- **API**: http://localhost:8000
- **Database**: localhost:5432
- **API Documentation**: http://localhost:8000/docs (Swagger UI)

## Environment Configuration

The application uses environment variables for configuration. You can customize these by creating a `.env` file:

```bash
# Database Configuration
POSTGRES_USER=bla
POSTGRES_PASSWORD=blabla
POSTGRES_DB=roop_marine_ops

# Application Configuration
SECRET_KEY=your-super-secret-key-here
LOG_LEVEL=INFO
DEBUG=false
```

## API Documentation

Once the service is running, you can access interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture

The service consists of:
- **FastAPI application**: REST API with automatic documentation
- **PostgreSQL database**: Data persistence with Alembic migrations

It's a PoC, so everything runs (both service and mock integration with the weather external API) in the same container.
I tried to come up with a layered structure to split schema (Pydantic), model (ORM) and service (business logic on service level).
app/main.py has the routes.

In the docker-compose.yaml file you can see 

It's all based on Postgres, but in a production scenario this might obviously change, depending on load and other tradeoffs (cost, how structured is the data etc etc). I almost used redis as cache, but it was too much to begin with.


## Technology Stack

### Backend Framework
- **FastAPI** 
- **Uvicorn** 
- **Pydantic**

### Database & ORM
- **PostgreSQL 16** 
- **SQLAlchemy 2.0** 
- **Alembic** 

### Development & Packaging
- **uv** 

### Code Quality & Testing
- **pytest** 
- **pytest-asyncio** 
- **ruff** 
- **mypy** 


### Architecture Patterns
- **Service Layer Pattern**
- **Repository Pattern**
- **Dependency Injection** 
- **Configuration Management** 
- **Database Migrations**

## API Testing Guide

Just import the postman_collection.json file in Postman :) 

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Task Management

#### Create Tasks

```bash
# Create a single task
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {
        "name": "Cable Installation",
        "wave_height_limit": 2.0,
        "duration_hours": 4.0
      }
    ]
  }'
```

#### Create Tasks with Dependencies

```bash
# Create multiple tasks with predecessor relationships
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {
        "name": "Site Preparation",
        "wave_height_limit": 2.5,
        "duration_hours": 2.0
      },
      {
        "name": "Cable Installation",
        "wave_height_limit": 2.0,
        "duration_hours": 4.0,
        "predecessor_id": 1
      },
      {
        "name": "Testing & Commissioning",
        "wave_height_limit": 1.5,
        "duration_hours": 3.0,
        "predecessor_id": 2
      }
    ]
  }'
```

#### Get All Tasks

```bash
curl -X GET "http://localhost:8000/tasks"
```

#### Get Specific Task

```bash
curl -X GET "http://localhost:8000/tasks/1"
```

#### Complete a Task

```bash
# Mark task 1 as completed (this will unblock dependent tasks)
curl -X PUT "http://localhost:8000/tasks/1/complete"
```

#### Start a Task

```bash
# Mark task 2 as in progress
curl -X PUT "http://localhost:8000/tasks/2/start"
```

#### Get Schedule Status

```bash
curl -X GET "http://localhost:8000/schedule/status"
```

### 3. Weather Forecasting

#### Get 12-Hour Forecast

```bash
curl -X GET "http://localhost:8000/weather/12h?lat=61.5&lon=4.8"
```

#### Get Custom Time Range Forecast

```bash
curl -X GET "http://localhost:8000/weather?lat=61.5&lon=4.8&from_time=2025-08-20T12:00:00Z&to_time=2025-08-20T18:00:00Z"
```

### 4. Wait on Weather (WoW) Analysis

```bash
# Analyze weather conditions for task execution
curl -X POST "http://localhost:8000/wow/analyze?task_id=1&lat=61.5&lon=4.8&forecast_hours=12"
```

Expected response includes:
- `can_proceed`: Boolean indicating GO/NO-GO recommendation
- `recommendation`: Human-readable recommendation
- `operational_windows`: Time windows suitable for task execution
- `go_no_go_signals`: Boolean array for each forecast point

### 5. Complete Workflow Test

Here's a complete workflow to test all functionality:

```bash
# 1. Create tasks with dependencies
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {"name": "Preparation", "wave_height_limit": 3.0, "duration_hours": 2.0},
      {"name": "Installation", "wave_height_limit": 2.0, "duration_hours": 4.0, "predecessor_id": 1},
      {"name": "Testing", "wave_height_limit": 1.5, "duration_hours": 3.0, "predecessor_id": 2}
    ]
  }'

# 2. Check schedule status
curl -X GET "http://localhost:8000/schedule/status"

# 3. Analyze weather for ready task
curl -X POST "http://localhost:8000/wow/analyze?task_id=1&lat=61.5&lon=4.8&forecast_hours=12"

# 4. Complete first task
curl -X PUT "http://localhost:8000/tasks/1/complete"

# 5. Check updated schedule
curl -X GET "http://localhost:8000/schedule/status"

# 6. Start second task
curl -X PUT "http://localhost:8000/tasks/2/start"

# 7. Analyze weather for second task
curl -X POST "http://localhost:8000/wow/analyze?task_id=2&lat=61.5&lon=4.8&forecast_hours=12"
```