import os
import shutil
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pdf2docx import Converter
from starlette.background import BackgroundTask

MAX_MB = int(os.getenv("MAX_MB", "20"))
# في الإنتاج حط رابط موقعك: ALLOWED_ORIGINS=https://username.github.io
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

app = FastAPI(title="PDF to Word")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


def _convert(pdf_path: str, docx_path: str) -> None:
    cv = Converter(pdf_path)
    try:
        cv.convert(docx_path)
    finally:
        cv.close()


@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    name = file.filename or "file.pdf"
    if not name.lower().endswith(".pdf"):
        raise HTTPException(400, "لازم الملف يكون PDF")

    data = await file.read()
    if len(data) > MAX_MB * 1024 * 1024:
        raise HTTPException(413, f"حجم الملف أكبر من {MAX_MB} ميجابايت")
    if not data.startswith(b"%PDF"):
        raise HTTPException(400, "الملف مش PDF صالح")

    tmpdir = tempfile.mkdtemp()
    pdf_path = os.path.join(tmpdir, "input.pdf")
    docx_path = os.path.join(tmpdir, "output.docx")

    with open(pdf_path, "wb") as f:
        f.write(data)

    try:
        await run_in_threadpool(_convert, pdf_path, docx_path)
    except Exception:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise HTTPException(500, "فشل التحويل. جرّب ملف تاني أو تأكد إن الملف مش ممسوح ضوئياً")

    out_name = os.path.splitext(os.path.basename(name))[0] + ".docx"
    return FileResponse(
        docx_path,
        media_type=DOCX_MIME,
        filename=out_name,
        background=BackgroundTask(shutil.rmtree, tmpdir, True),
    )
