from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from .quota import check_and_consume
from .render import RenderError, render_page_to_png
from .storage import ensure_dirs, pdf_path

APP_TITLE = "progressive-pdf-to-web"

app = FastAPI(title=APP_TITLE)


def _mobile_html(doc_id: str, page: int, img_url: str) -> str:
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
  <title>{APP_TITLE} · {doc_id} · p{page}</title>
  <style>
    body {{ margin: 0; font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; background:#0b0b0f; color:#eee; }}
    .top {{ position: sticky; top: 0; background: rgba(11,11,15,.92); padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,.08); }}
    .top b {{ font-size: 14px; }}
    .wrap {{ padding: 10px; }}
    img {{ width: 100%; height: auto; display:block; border-radius: 10px; background:#111; }}
    .hint {{ opacity:.75; font-size: 12px; margin-top: 8px; }}
  </style>
</head>
<body>
  <div class=\"top\"><b>{doc_id}</b> · page {page}</div>
  <div class=\"wrap\">
    <img src=\"{img_url}\" alt=\"page {page}\" />
    <div class=\"hint\">Rendered on demand. Cache: enabled.</div>
  </div>
</body>
</html>"""


@app.on_event("startup")
def _startup() -> None:
    ensure_dirs()


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/v1/upload")
async def upload_pdf(file: UploadFile = File(...)) -> JSONResponse:
    ensure_dirs()

    if file.content_type not in {"application/pdf", "application/x-pdf", "application/acrobat"}:
        # allow unknown types but require .pdf name
        if not (file.filename or "").lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF is supported")

    doc_id = uuid.uuid4().hex
    dest = pdf_path(doc_id)

    with dest.open("wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)

    return JSONResponse({"document_id": doc_id})


@app.get("/v1/docs/{doc_id}/pages/{page}.png")
def get_page_png(doc_id: str, page: int) -> FileResponse:
    pdf_file = pdf_path(doc_id)
    if not pdf_file.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        out_path = render_page_to_png(pdf_file, doc_id=doc_id, page=page)
    except RenderError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(path=str(out_path), media_type="image/png")


@app.get("/v1/docs/{doc_id}/page/{page}")
def page_view(
    doc_id: str,
    page: int,
    user_id: str = "anon",
    paid: bool = False,
) -> HTMLResponse:
    pdf_file = pdf_path(doc_id)
    if not pdf_file.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    allowed, used, limit_ = check_and_consume(user_id=user_id, is_paid=paid, pages=1)
    if not allowed:
        raise HTTPException(status_code=402, detail={"error": "quota_exceeded", "used_today": used, "limit": limit_})

    # Render / cache
    try:
        render_page_to_png(pdf_file, doc_id=doc_id, page=page)
    except RenderError as e:
        raise HTTPException(status_code=500, detail=str(e))

    img_url = f"/v1/docs/{doc_id}/pages/{page}.png"
    return HTMLResponse(_mobile_html(doc_id, page, img_url))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "8000")))
