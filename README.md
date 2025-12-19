# 📅 Resource Reservation Platform – FastAPI

## Overview

This project is a **RESTful API**
It provides a complete backend for managing **shared resource reservations** within a multi-site company.

Employees can reserve **meeting rooms, equipment, or vehicles**, while the system enforces:

* time slot rules
* conflict detection
* role-based permissions
* availability checks with alternative suggestions

The API is built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy (async)**, following **professional backend practices**.

---

## Business Context

A multi-site company wants to centralize the management of shared resources:

* meeting rooms
* IT equipment
* service vehicles

The platform must:

* prevent double bookings
* respect user permissions (employee / manager / admin)
* provide visibility on resource availability
* offer alternative time slots when a resource is unavailable

---

## Technical Stack

* **Python 3.11+**
* **FastAPI**
* **PostgreSQL**
* **SQLAlchemy 2.0 (async)**
* **Alembic** (database migrations)
* **Pydantic** (validation)
* **Uvicorn**
* **Swagger / OpenAPI**

---

## Project Architecture

The project is organized by **business domains**, following a clean REST architecture:

```
app/
  core/               # Configuration, database, security
  modules/
    users/            # User management
    resources/        # Resources (rooms, equipment, vehicles)
    bookings/         # Reservations
  utils/              # Time & availability helpers
alembic/              # Database migrations
```

Each module follows the same structure:

* `models.py` → SQLAlchemy models
* `schemas.py` → Pydantic validation
* `repository.py` → Database access
* `service.py` → Business rules
* `routes.py` → API endpoints

This separation ensures **maintainability, testability, and scalability**.

---

## Database & Migrations

The database schema is **fully versioned using Alembic**.

### Why Alembic

* Reproducible schema
* Versioned changes
* No manual table creation
* Suitable for CI/CD and grading

### Run migrations

```bash
alembic upgrade head
```

---

## Environment Configuration

Create a `.env` file at the project root:

```env
APP_NAME=project-reservation
ENV=dev

DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=project-reservation
DB_USER=postgres
DB_PASSWORD=your_password
```

---

## Running the Application

### 1. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
```

### 2️. Install dependencies

```bash
pip install -r requirements.txt
```

### 3️. Apply database migrations

```bash
alembic upgrade head
```

### 4️. Start the API

```bash
uvicorn app.main:app --reload
```

API will be available at:

* **[http://127.0.0.1:8000](http://127.0.0.1:8000)**
* Swagger UI: **/docs**

---

## Authentication & Permissions

For simplicity, authentication is simulated using HTTP headers:

```
X-User-Id: <integer>
X-Role: employee | manager | admin
```

### Permission rules

| Role     | Permissions                                |
| -------- | ------------------------------------------ |
| Employee | Book allowed resource types, only for self |
| Manager  | Same as employee + manage department       |
| Admin    | Full access (users, resources, bookings)   |

---

## Core Features

### Users

* CRUD operations
* Role management
* Account activation / deactivation
* Permission inspection

### Resources

* Types: `room`, `equipment`, `vehicle`
* Unique name per site
* Capacity validation for rooms
* Maintenance & out-of-service states
* Filtering, sorting, pagination

### Bookings

* Min duration: **30 minutes**
* Max duration: **8 hours**
* No past booking (except admin)
* Conflict detection (overlapping slots)
* Status lifecycle: pending, confirmed, cancelled, completed, no-show

### Availability & Suggestions

* Check availability for a time slot
* Get free slots for a day or week
* Suggest alternative slots when unavailable
* Smart slot rounding (15/30 minutes)
* Avoid micro-gaps

---

## Error Handling

The API uses **consistent JSON error responses**:

```json
{
  "error_code": "BOOKING_CONFLICT",
  "message": "This resource is already booked for this time slot."
}
```

### HTTP status codes used

* `400` – Business rule violation
* `403` – Insufficient permissions
* `404` – Resource not found
* `409` – Conflict (overlapping booking)
* `422` – Validation error

---

## API Documentation

All endpoints are documented using **OpenAPI / Swagger**:

* Request schemas
* Validation rules
* Response examples
* Error responses

Accessible at:

```
/docs
```

---

## Quality & Best Practices

* Typed code (Python type hints)
* Clear domain separation
* Async database access
* Short, readable comments
* No business logic in routes
* Professional migration workflow
* RESTful conventions respected

## Author

Developed by **Keenan MARTIN**, as part of an academic project, with the objective of demonstrating:

* backend architecture skills
* REST API design
* data modeling
* business rule implementation
* professional tooling (migrations, validation, documentation)
