"""
Tester /extract-pdf sin input-validering: filtype, tom fil, størrelsesgrense
og korrupt PDF. Bruker FastAPI TestClient — ingen ekte PDF-er nødvendig.
"""

from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)


def test_avviser_ikke_pdf():
    res = client.post(
        "/extract-pdf",
        files={"file": ("cv.txt", b"hei", "text/plain")},
    )
    assert res.status_code == 400
    assert "PDF" in res.json()["detail"]


def test_avviser_tom_fil():
    res = client.post(
        "/extract-pdf",
        files={"file": ("cv.pdf", b"", "application/pdf")},
    )
    assert res.status_code == 400


def test_avviser_for_stor_fil():
    big = b"%PDF-1.4" + b"0" * (main._MAX_PDF_BYTES + 1)
    res = client.post(
        "/extract-pdf",
        files={"file": ("cv.pdf", big, "application/pdf")},
    )
    assert res.status_code == 413


def test_korrupt_pdf_gir_422_ikke_500():
    # Gyldig filnavn, men ikke en faktisk PDF -> fitz.open skal feile pent.
    res = client.post(
        "/extract-pdf",
        files={"file": ("cv.pdf", b"dette er ikke en pdf", "application/pdf")},
    )
    assert res.status_code == 422
