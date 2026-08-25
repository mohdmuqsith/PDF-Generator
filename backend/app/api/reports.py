from datetime import date, datetime # noqa: I001
from pathlib import Path

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.config import REPORTS_DIR
from app.db.database import get_connection, initialize_database
from app.reports.queries import get_report_data
from app.reports.renderer import render_report_pdf

router = APIRouter(prefix="/reports", tags=["reports"])


class CreateReportRequest(BaseModel):
    force: bool = False


def _report_response(row):
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "report_date": row["report_date"],
        "file": f"/reports/{row['id']}/file",
    }


def _get_report(report_id):
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT id, path, created_at, report_date
            FROM reports
            WHERE id = ?
            """,
            (report_id,),
        ).fetchone()


@router.get("")
def list_reports():
    initialize_database()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, path, created_at, report_date
            FROM reports
            ORDER BY created_at DESC
            """
        ).fetchall()

    return {"reports": [_report_response(row) for row in rows]}


@router.post("")
def create_report(payload: CreateReportRequest | None = None):
    initialize_database()
    force = payload.force if payload else False
    report_date = date.today().isoformat()

    if not force:
        with get_connection() as connection:
            existing = connection.execute(
                """
                SELECT id, path, created_at, report_date
                FROM reports
                WHERE report_date = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (report_date,),
            ).fetchone()

        if existing:
            return _report_response(existing)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    created_at = datetime.now().isoformat(timespec="seconds")
    filename = f"sales-report-{created_at.replace(':', '-')}.pdf"
    output_path = REPORTS_DIR / filename

    report_data = get_report_data()

    if report_data["summary"]["total_orders"] == 0:
        raise HTTPException(
            status_code=400,
            detail="No orders found. Run the seed script before generating a report.",
        )

    render_report_pdf(report_data, output_path)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO reports (path, created_at, report_date)
            VALUES (?, ?, ?)
            """,
            (str(output_path), created_at, report_date),
        )
        connection.commit()
        report_id = cursor.lastrowid

    row = _get_report(report_id)
    return JSONResponse(status_code=201, content=_report_response(row))


@router.get("/{report_id}")
def get_report(report_id: int):
    row = _get_report(report_id)

    if not row:
        raise HTTPException(status_code=404, detail="Report not found")

    return _report_response(row)


@router.get("/{report_id}/file")
def download_report(report_id: int):
    row = _get_report(report_id)

    if not row:
        raise HTTPException(status_code=404, detail="Report not found")

    path = Path(row["path"])

    if not path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=path.name,
    )
