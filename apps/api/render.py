from __future__ import annotations

import subprocess
from pathlib import Path

from .storage import page_image_path


class RenderError(RuntimeError):
    pass


def render_page_to_webp(pdf_file: Path, doc_id: str, page: int, dpi: int = 160) -> Path:
    """Render a single page using pdftoppm.

    pdftoppm -f <page> -l <page> -r <dpi> -singlefile -png input.pdf output_prefix

    Then convert to webp via ffmpeg if you want; but for MVP, we can just keep PNG.
    However, to keep deps minimal, we’ll output PNG first.
    """

    # MVP: output PNG (no extra deps). Name it .png but still use path helper with fmt.
    out = page_image_path(doc_id, page, fmt="png")
    if out.exists():
        return out

    out_prefix = out.with_suffix("")  # pdftoppm adds .png

    cmd = [
        "pdftoppm",
        "-f",
        str(page),
        "-l",
        str(page),
        "-r",
        str(dpi),
        "-singlefile",
        "-png",
        str(pdf_file),
        str(out_prefix),
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        raise RenderError("pdftoppm not found. Install poppler-utils / poppler.")

    if proc.returncode != 0:
        raise RenderError(f"pdftoppm failed: {proc.stderr.strip()[:400]}")

    # pdftoppm produces <prefix>.png
    produced = out_prefix.with_suffix(".png")
    if not produced.exists():
        raise RenderError("pdftoppm completed but output file missing.")

    # ensure final path name is exactly out (same as produced usually)
    if produced != out:
        produced.replace(out)

    return out
