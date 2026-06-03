"""
Tester Pydantic-validatorene på JobInput — input-grensene som beskytter mot
tomme og overdimensjonerte forespørsler.
"""

import pytest
from pydantic import ValidationError

from main import JobInput


def test_gyldig_input():
    job = JobInput(job_posting="Vi søker utvikler", cv="Min CV")
    assert job.job_posting == "Vi søker utvikler"
    assert job.cv == "Min CV"


def test_tom_stillingsannonse_avvises():
    with pytest.raises(ValidationError, match="kan ikke være tom"):
        JobInput(job_posting="   ", cv="Min CV")


def test_tom_cv_avvises():
    with pytest.raises(ValidationError, match="kan ikke være tom"):
        JobInput(job_posting="Annonse", cv="")


def test_for_lang_stillingsannonse_avvises():
    with pytest.raises(ValidationError, match="for lang"):
        JobInput(job_posting="x" * 10_001, cv="Min CV")


def test_for_lang_cv_avvises():
    with pytest.raises(ValidationError, match="for lang"):
        JobInput(job_posting="Annonse", cv="x" * 15_001)


def test_grenseverdier_godtas():
    # Akkurat på grensen skal være lov.
    JobInput(job_posting="x" * 10_000, cv="x" * 15_000)
