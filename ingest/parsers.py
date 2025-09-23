from __future__ import annotations
from pathlib import Path
from typing import Tuple
from pypdf import PdfReader

try:
    import docx  # python-docx
except Exception:
    docx = None

try:
    import pptx  # python-pptx
except Exception:
    pptx = None


def read_text(path: Path) -> Tuple[str, dict]:
    meta: dict = {"source": str(path), "name": path.name}
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text, meta
    if path.suffix.lower() in {".txt", ".md"}:
        return path.read_text(errors="ignore"), meta
    if path.suffix.lower() == ".docx" and docx:
        d = docx.Document(str(path))
        return "\n".join(p.text for p in d.paragraphs), meta
    if path.suffix.lower() == ".pptx" and pptx:
        pres = pptx.Presentation(str(path))
        texts = []
        for slide in pres.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    texts.append(shape.text)
        return "\n".join(texts), meta
    if path.suffix.lower() in {".csv", ".xlsx"}:
        try:
            import pandas as pd
            df = pd.read_csv(path) if path.suffix.lower() == ".csv" else pd.read_excel(path)
            return df.to_csv(index=False), meta
        except Exception:
            return "", meta
    return "", meta
