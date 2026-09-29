import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
# setu_kern is niet geïnstalleerd (zoals cao_setu_v2): de tests lezen het pakket rechtstreeks uit src/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@pytest.fixture(scope="session")
def webform():
    """De echte wijzerbelonen-webform (v2.1.0) in V8, als referentie. Overgeslagen zonder mini-racer."""
    pytest.importorskip("py_mini_racer")
    from referentie_kern.webform import Webform

    wf = Webform()
    yield wf
    wf.close()
