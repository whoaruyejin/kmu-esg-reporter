# app/services/report/renderer.py
from pathlib import Path
from xhtml2pdf import pisa

def html_to_pdf(html_str: str, out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        result = pisa.CreatePDF(src=html_str, dest=f, encoding="utf-8")
    if result.err:
        raise RuntimeError("xhtml2pdf 변환 실패")
    return out_path
