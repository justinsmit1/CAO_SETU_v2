import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))


@pytest.fixture(scope="session")
def webform():
    """De echte wijzerbelonen-webform (v2.1.0) in V8, als referentie. Overgeslagen zonder mini-racer."""
    pytest.importorskip("py_mini_racer")
    from referentie.webform import Webform

    wf = Webform()
    yield wf
    wf.close()
