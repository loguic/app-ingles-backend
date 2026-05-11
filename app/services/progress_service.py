import json
from pathlib import Path
from app.schemas.progress import ProgressRecord

PROGRESS_DIR = Path(__file__).resolve().parents[2] / "data" / "progress"

def save_progress(record: ProgressRecord) -> ProgressRecord:
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)

    file_path = PROGRESS_DIR / f"{record.user_id}.json"

    if file_path.exists():
        records = json.loads(file_path.read_text(encoding="utf-8"))
    else:
        records = []

    records.append(record.model_dump())

    file_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return record

def get_progress_by_user(user_id: str) -> list[ProgressRecord]:
    file_path = PROGRESS_DIR / f"{user_id}.json"

    if not file_path.exists():
        return []

    records = json.loads(file_path.read_text(encoding="utf-8"))
    return [ProgressRecord.model_validate(record) for record in records]
