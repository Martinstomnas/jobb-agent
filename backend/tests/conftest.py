"""
Felles testoppsett. Sørger for at en API-nøkkel finnes ved import, slik at
Anthropic-klienten kan instansieres uten å treffe nettet — alle LLM-kall mockes
i testene, så nøkkelen brukes aldri til ekte kall.
"""

import os

import pytest

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")


@pytest.fixture(autouse=True)
def disable_rate_limiter():
    import main
    main.limiter.enabled = False
    yield
    main.limiter.enabled = True
