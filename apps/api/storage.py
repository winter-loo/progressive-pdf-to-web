from __future__ import annotations

import os
from pathlib import Path

DATA_DIR = Path(os.getenv("PP2W_DATA_DIR", "./data")).resolve()
PDF_DIR = DATA_DIR / "pdf"
PAGE_DIR = DATA_DIR / "pages"  # rendered images
META_DIR = DATA_DIR / "meta"


def ensure_dirs() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    PAGE_DIR.mkdir(parents=True, exist_ok=True)
    META_DIR.mkdir(parents=True, exist_ok=True)


def pdf_path(doc_id: str) -> Path:
    return PDF_DIR / f"{doc_id}.pdf"


def page_image_path(doc_id: str, page: int, fmt: str = "png") -> Path:
    # store as .../pages/<doc_id>/<page>.png
    d = PAGE_DIR / doc_id
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{page}.{fmt}"
