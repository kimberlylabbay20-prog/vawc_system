# Barangay VAWC Reporting System

> A web-based incident reporting system for **Violence Against Women and Children (VAWC)** cases at the barangay level. Built with FastAPI and PostgreSQL. Supports bilingual (English/Tagalog) submissions and optional file attachments.

---

## System Overview

This system allows barangay constituents to submit VAWC incident reports online. Reports are stored in a PostgreSQL database and can be viewed by authorized personnel. The frontend is a server-rendered HTML form using Jinja2 templating, styled with a purple/magenta theme and bilingual labels for accessibility.

The project consists of two code versions:

| Version | Location | Features |
|---------|----------|----------|
| **Active (root)** | `./main.py` | File upload, Jinja2 templating, bilingual UI |
| **Legacy (nested)** | `./vawc_system/main.py` | JSON-only API, static HTML, no file upload |

---

## Features

- **Submit VAWC Reports** – File a report with victim name, contact info, incident type, description, and location
- **Bilingual UI** – All form labels and placeholders in English and Tagalog
- **File Attachments** – Optional upload of supporting documents/evidence
- **Incident Categorization** – Physical Abuse, Emotional Abuse, Threat, or Other
- **View Reports** – API endpoint to retrieve all submitted reports
- **Auto-creates Database Tables** – Tables are generated on application startup
- **CORS Enabled** – Cross-Origin Resource Sharing configured for all origins
- **Responsive Design** – Mobile-friendly form layout

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.14** | Runtime environment |
| **FastAPI** | Web framework and REST API |
| **SQLAlchemy** | ORM for database interaction |
| **PostgreSQL** | Relational database (hosted on Render.com) |
| **Pydantic** | Data validation and schema modeling |
| **Jinja2** | Server-side HTML templating |
| **python-multipart** | File upload handling |
| **Uvicorn** | ASGI server for running the app |

---

## Project Structure

```
vawc_system/
├── main.py                  # FastAPI app entry point
├── database.py              # Database engine and session config
├── models.py                # SQLAlchemy ORM model (Report table)
├── schemas.py               # Pydantic request/response schemas
├── crud.py                  # Database CRUD operations
├── requirements.txt         # Python dependencies
├── _redirects.txt           # Render.com redirect config
├── .gitattributes           # Git line-ending normalization
├── templates/
│   └── report.html          # Jinja2 HTML form (bilingual)
├── vawc_system/             # Legacy version (older code)
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── requirements.txt
│   └── report.html
├── uploads/                 # Uploaded file attachments (auto-created)
├── .venv/                   # Python virtual environment
└── README.md                # This file
```

---

## Database Schema

### Table: `reports`

| Column | Type | Notes |
|--------|------|-------|
| `id` | `INTEGER` (PK) | Auto-increment, primary key |
| `victim_name` | `VARCHAR` | Name of the victim |
| `contact_number` | `VARCHAR` | Contact number of the reporter/victim |
| `incident_type` | `VARCHAR` | Type of VAWC incident |
| `description` | `TEXT` | Detailed incident description |
| `location` | `TEXT` | Location of the incident |
| `date_reported` | `TIMESTAMP` | Auto-set to current timestamp |
| `status` | `VARCHAR` | Default: `"Pending"` |
| `file_path` | `VARCHAR` (nullable) | Path to uploaded file (active version only) |

---

## Requirements / Dependencies

All dependencies are listed in `requirements.txt`:

```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
pydantic
jinja2
python-multipart
```

---

## Installation & Setup Guide

### Prerequisites

- Python 3.9+ installed ([python.org](https://python.org))
- PostgreSQL database (local or cloud-hosted like Render, Aiven, etc.)
- pip (Python package installer)

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd vawc_system
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

**Activate it:**

- **Windows:**
  ```bash
  .venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```bash
  source .venv/bin/activate
  ```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up the Database

Create a PostgreSQL database and note the connection string:

```
postgresql://username:password@host:port/database_name
```

> **⚠️ Security Notice:** The database URL is currently **hardcoded** in `database.py`. You should move it to an environment variable (see [Configuration](#configuration) below).

### Step 5: Configure Environment Variables (Recommended)

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://username:password@host:port/database_name
```

Then update `database.py` to read from the environment:

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/vawc_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

### Step 6: Run the Application

```bash
uvicorn main:app --reload
```

The server will start at **http://127.0.0.1:8000**.

---

## How to Run

### Development Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- **Web form:** http://127.0.0.1:8000/
- **API docs (Swagger):** http://127.0.0.1:8000/docs
- **Alternative API docs (ReDoc):** http://127.0.0.1:8000/redoc

### Production Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/` | Serves the bilingual report submission form (HTML) | No |
| `POST` | `/submit_report` | Submit a new VAWC report (multipart form-data) | No |
| `GET` | `/view_reports` | Retrieve all submitted reports (JSON) | No |

### POST `/submit_report`

**Request (multipart/form-data):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `victim_name` | string | Yes | Name of the victim |
| `contact_number` | string | Yes | Contact number |
| `incident_type` | string | Yes | Physical Abuse, Emotional Abuse, Threat, or Other |
| `description` | string | Yes | Detailed incident description |
| `location` | string | Yes | Location of the incident |
| `file` | file | No | Supporting document or evidence |

**Response (200):**

```json
{
  "message": "Report submitted",
  "file": "uploads/filename.pdf"
}
```

### GET `/view_reports`

**Response (200):**

```json
[
  {
    "id": 1,
    "victim_name": "Maria Santos",
    "contact_number": "09123456789",
    "incident_type": "Physical Abuse (Pananakit)",
    "description": "Details of the incident...",
    "location": "Barangay 5, Manila",
    "date_reported": "2026-05-11T10:30:00",
    "status": "Pending",
    "file_path": "uploads/evidence.pdf"
  }
]
```

---

## User Roles and Permissions

Currently the system has **no authentication or role-based access control**. All endpoints are publicly accessible.

| Role | Access |
|------|--------|
| **Reporter (Public)** | Can submit reports via the web form |
| **Admin/Viewer** | Can view all reports via `/view_reports` |

> **Future improvement:** Add authentication (JWT/OAuth2) and role-based access with barangay admin and investigator roles.

---

## Security Notes & Recommended Improvements

### Detected Issues

| Issue | Location | Recommendation |
|-------|----------|----------------|
| **Hardcoded database credentials** | `database.py:5` | Move to `.env` file and use `os.getenv()` |
| **No `.gitignore`** | Project root | Add one to exclude `.env`, `uploads/`, `__pycache__/`, `.venv/` |
| **CORS wide open** | `main.py:18` | Restrict `allow_origins` to specific frontend domains in production |
| **No authentication** | All endpoints | Add user authentication for report viewing |
| **No input sanitization** | `crud.py` | Validate and sanitize file uploads to prevent path traversal |
| **Legacy duplicate code** | `vawc_system/` | Remove the nested legacy version to avoid confusion |

---

## Screenshots

*Add screenshots here:*

| Page | Screenshot |
|------|------------|
| Report Submission Form | `![Form](screenshots/form.png)` |
| Success State | `![Success](screenshots/success.png)` |
| API Docs (Swagger) | `![Swagger](screenshots/swagger.png)` |

---

## Deployment

This app is deployable to **Render.com** (as previously configured). The `_redirects.txt` file is for Render static site redirects.

### Deploy to Render

1. Push the repository to GitHub
2. On Render Dashboard, create a **New Web Service**
3. Connect your repository
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable `DATABASE_URL` in Render dashboard
6. Deploy

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

Please ensure your code follows the existing style and passes basic checks.

---

## License

This project is open-source and available for educational and community use.

---

## Acknowledgments

- Built for barangay-level VAWC case reporting and management
- Inspired by the need for accessible, bilingual reporting tools in Filipino communities
