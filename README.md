# PDF Report Generator

A full-stack application that turns raw sales data into polished, print-ready PDF
reports. A FastAPI service reads from a SQLite database, aggregates the data into
summary metrics, renders an HTML template, and prints it to a pixel-accurate PDF
with a headless Chromium browser. A React dashboard lets you generate new reports
on demand and download any report that has been produced.

This is a personal project built to explore server-side PDF generation, data
aggregation with plain SQL, and a clean separation between a rendering backend and
a thin frontend client.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [How It Works](#how-it-works)
- [API Reference](#api-reference)
- [Data Model](#data-model)
- [Configuration](#configuration)
- [Development Notes](#development-notes)
- [Roadmap](#roadmap)
- [License](#license)

---

## Features

- **On-demand PDF generation** – create a sales report from the current contents
  of the database with a single API call or a button in the UI.
- **Real aggregation, not mock data** – total orders, total revenue, average
  order value, top products by revenue, and a rolling 7-day breakdown, all
  computed in SQL.
- **High-fidelity output** – reports are laid out in HTML/CSS and printed through
  headless Chromium, so the PDF matches exactly what a browser would render
  (A4 page size, background colors, page-break-aware tables).
- **Idempotent by default** – requesting a report for a date that already has one
  returns the existing report; pass `force` to generate a fresh copy.
- **Report history** – every generated report is recorded in the database and
  served back through a listing endpoint, each downloadable by a stable URL.
- **React dashboard** – generate, refresh, and download reports from a small
  single-page app with loading and error states.
- **Zero-config startup** – the database schema is created automatically on first
  run via a FastAPI lifespan hook.

---

## Architecture

```
┌──────────────────┐      HTTP/JSON       ┌────────────────────────────┐
│  React dashboard  │  ───────────────▶   │        FastAPI app          │
│  (Vite dev server)│  ◀───────────────   │                             │
└──────────────────┘   PDF file download  │  ┌───────────────────────┐  │
                                          │  │ /reports API router    │  │
                                          │  └──────────┬────────────┘  │
                                          │             │               │
                                          │   ┌─────────▼─────────┐     │
                                          │   │  queries.py        │     │
                                          │   │  (SQL aggregation) │     │
                                          │   └─────────┬─────────┘     │
                                          │             │               │
                                          │   ┌─────────▼─────────┐     │
                                          │   │  renderer.py       │     │
                                          │   │  HTML → Chromium   │     │
                                          │   │  → PDF on disk     │     │
                                          │   └───────────────────┘     │
                                          │             │               │
                                          │   ┌─────────▼─────────┐     │
                                          │   │  SQLite (report.db)│     │
                                          │   └───────────────────┘     │
                                          └────────────────────────────┘
```

The backend is organised in layers:

| Layer | Module | Responsibility |
|-------|--------|----------------|
| API | `app/api/reports.py`, `app/api/health.py` | HTTP routing, request/response shaping, error handling |
| Domain | `app/reports/queries.py` | Read and aggregate order data into a report payload |
| Rendering | `app/reports/renderer.py` | Build the report HTML and print it to PDF |
| Data | `app/db/database.py`, `app/db/seed.py` | Connection management, schema bootstrap, sample data |
| Config | `app/core/config.py` | Filesystem paths for the database and report output |

---

## Tech Stack

**Backend**

- [FastAPI](https://fastapi.tiangolo.com/) – web framework and routing
- [Uvicorn](https://www.uvicorn.org/) – ASGI server
- [Playwright](https://playwright.dev/python/) – headless Chromium for HTML-to-PDF
- SQLite via the Python standard library `sqlite3`
- Pydantic – request body validation

**Frontend**

- [React 18](https://react.dev/)
- [Vite](https://vitejs.dev/) – dev server and build tool
- [lucide-react](https://lucide.dev/) – icons
- Plain CSS

---

## Project Structure

```
pdf-generator/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── health.py        # GET /health
│   │   │   └── reports.py       # /reports CRUD + file download
│   │   ├── core/
│   │   │   └── config.py        # DATABASE_PATH, REPORTS_DIR
│   │   ├── db/
│   │   │   ├── database.py      # connection context manager + schema
│   │   │   └── seed.py          # generate 200 sample orders
│   │   ├── reports/
│   │   │   ├── queries.py       # SQL aggregation → report payload
│   │   │   └── renderer.py      # HTML template + Chromium PDF print
│   │   └── main.py             # FastAPI app, CORS, lifespan startup
│   ├── reports/                # generated PDF files (git-ignored)
│   ├── report.db               # SQLite database (git-ignored)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── reports.js       # fetch wrapper for the backend
│   │   ├── components/
│   │   │   └── ReportList.jsx   # dashboard: generate / list / download
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10 or newer
- Node.js 18 or newer
- ~200 MB of disk space for the Chromium browser Playwright downloads

### Backend Setup

```bash
cd backend

# 1. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install the Chromium browser used for PDF rendering
playwright install chromium

# 4. Seed the database with sample orders
python -m app.db.seed

# 5. Start the API (from the backend/ directory)
uvicorn app.main:app --reload
```

The API is now available at `http://localhost:8000`. Interactive docs are served
at `http://localhost:8000/docs`.

> The `orders` and `reports` tables are created automatically the first time the
> app starts, so step 4 is only about populating sample data. Without seeded
> orders, `POST /reports` returns `400` with a message telling you to seed first.

### Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

The dashboard runs at `http://localhost:5173` and talks to the backend at
`http://localhost:8000` (see [Configuration](#configuration) to change this).

---

## How It Works

1. **Request** – The client calls `POST /reports`. If `force` is `false` (the
   default) and a report already exists for today's date, that existing report is
   returned untouched.
2. **Aggregate** – `get_report_data()` runs four queries against the `orders`
   table: a summary row (count, sum, average), top 5 products by revenue, orders
   grouped by day for the last 7 days, and the full list of orders.
3. **Guard** – If there are no orders, the endpoint responds with `400` instead
   of producing an empty report.
4. **Render** – `build_report_html()` interpolates the data into a self-contained
   HTML document with embedded CSS (`@page` rules for A4, page-break-safe table
   styling). All user-supplied values are HTML-escaped.
5. **Print** – `render_report_pdf()` launches headless Chromium via Playwright,
   loads the HTML, waits for network idle, and writes a PDF to
   `backend/reports/sales-report-<timestamp>.pdf`.
6. **Record** – A row is inserted into the `reports` table with the file path,
   creation timestamp, and report date. The response includes an `id` and a
   `file` URL.
7. **Download** – `GET /reports/{id}/file` streams the stored PDF back with
   `Content-Type: application/pdf`.

---

## API Reference

Base URL: `http://localhost:8000`

### `GET /health`

Health check.

```json
{ "status": "ok" }
```

### `GET /reports`

List all reports, newest first.

```json
{
  "reports": [
    {
      "id": 3,
      "created_at": "2026-08-28T03:22:56",
      "report_date": "2026-08-28",
      "file": "/reports/3/file"
    }
  ]
}
```

### `POST /reports`

Generate a report for today.

**Request body** (optional):

```json
{ "force": false }
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `force` | boolean | `false` | When `true`, always render a new PDF even if one already exists for today. |

**Responses**

- `201 Created` – a new report was rendered.
- `200 OK` – an existing report for today was returned (`force` was `false`).
- `400 Bad Request` – no orders in the database; run the seed script.

```json
{
  "id": 4,
  "created_at": "2026-08-28T03:30:10",
  "report_date": "2026-08-28",
  "file": "/reports/4/file"
}
```

### `GET /reports/{id}`

Fetch metadata for a single report. Returns `404` if the id is unknown.

### `GET /reports/{id}/file`

Download the rendered PDF. Returns `404` if the report or its file is missing.

---

## Data Model

**`orders`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | primary key |
| `customer` | TEXT | customer name |
| `product` | TEXT | product name |
| `amount` | REAL | order value |
| `created_at` | TEXT | ISO date (`YYYY-MM-DD`) |

**`reports`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | primary key |
| `path` | TEXT | absolute path to the PDF on disk |
| `created_at` | TEXT | ISO timestamp of generation |
| `report_date` | TEXT | the date the report covers |

The seed script inserts 200 randomised orders spread across the previous 30 days
using a fixed random seed, so results are reproducible.

---

## Configuration

**Backend paths** – `backend/app/core/config.py`

| Constant | Default | Purpose |
|----------|---------|---------|
| `DATABASE_PATH` | `backend/report.db` | SQLite database file |
| `REPORTS_DIR` | `backend/reports/` | where generated PDFs are written |

**CORS** – `backend/app/main.py` allows `http://localhost:5173` by default. Add
your own origins there if you serve the frontend elsewhere.

**API base URL** – `frontend/src/api/reports.js` hard-codes
`http://localhost:8000`. Change `API_BASE_URL` to point the dashboard at a
different backend.

---

## Development Notes

- **No ORM.** Queries are plain SQL executed through `sqlite3` with
  `Row` factory access. The connection is managed by a context manager in
  `app/db/database.py`.
- **Rendering is synchronous.** `render_report_pdf` uses Playwright's sync API and
  runs inside the request. For a single user this is fine; a production version
  would move it to a background task or worker.
- **Generated artifacts are git-ignored.** `report.db` and everything under
  `backend/reports/` stay out of version control.
- **Frontend has no test/build pipeline configured** beyond Vite's defaults;
  `npm run build` produces a static bundle in `frontend/dist/`.

---

## things yet to try 


- Background job + polling for report generation
- Charts in the PDF (currently tables only)
- Auth around the API


---

## License

Released under the MIT License. Do what you like with it.
