from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = BASE_DIR / "report.db"
REPORTS_DIR = BASE_DIR / "reports"
