from pathlib import Path
from typing import Iterable, List

SUPPORTED = {".pdf", ".txt", ".md", ".docx", ".pptx", ".csv", ".xlsx", ".png", ".jpg", ".jpeg"}

def iter_files(root: str | Path) -> Iterable[Path]:
    root = Path(root)
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in SUPPORTED:
            yield p
