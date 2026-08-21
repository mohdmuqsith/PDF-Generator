# PDF Report Generator

A personal full-stack project for generating PDF reports from SQLite data.

## Stack

- React frontend
- FastAPI backend
- SQLite database
- Playwright + Chromium for HTML-to-PDF rendering

## Project Structure

```text
pdf-generator/
  backend/
    app/
      api/
        health.py
        reports.py
      core/
        config.py
      db/
        database.py
        seed.py
      reports/
        queries.py
        renderer.py
      main.py
    reports/
    requirements.txt
  frontend/
    src/
      api/
        reports.js
      components/
        ReportList.jsx
      App.jsx
      main.jsx
    package.json
    index.html
  .gitignore
```

## Run Order

1. Build and test the FastAPI backend.
2. Seed SQLite with sample data.
3. Generate a PDF from backend code.
4. Add report API endpoints.
5. Build the React dashboard.
