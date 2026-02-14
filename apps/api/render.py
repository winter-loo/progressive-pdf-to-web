from __future__ import annotations

import subprocess
from pathlib import Path

from .storage import page_image_path


class RenderError(RuntimeError):
    pass


def render_page_to_png(pdf_file: Path, doc_id: str, page: int, dpi: int = 144) -> Path:
    """Render a single PDF page to PNG using poppler's `pdftoppm`.

    - Output is cached at data/pages/<doc_id>/<page>.png
    """

    out_path = page_image_path(doc_id, page, fmt="png")
    if out_path.exists() and out_path.stat().st_size > 0:
        return out_path

    out_prefix = out_path.with_suffix("")  # pdftoppm expects prefix, adds .png

    # pdftoppm -f N -l N -singlefile -png -r <dpi> <pdf> <outprefix>
    cmd = [
        "pdftoppm",
        "-f",
        str(page),
        "-l",
        str(page),
        "-singlefile",
        "-png",
        "-r",
        str(dpi),
        str(pdf_file),
        str(out_prefix),
    ]

    try:
        p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError as e:
        raise RenderError("pdftoppm not found. Install poppler-utils/poppler.") from e

    if p.returncode != 0:
        raise RenderError(f"pdftoppm failed ({p.returncode}): {p.stderr.strip()}")

    if not out_path.exists():
        raise RenderError("Render completed but output file not found")

    return out_path
