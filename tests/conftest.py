from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.settings import FunctionalTestSettings, test_settings


@pytest.fixture(scope="session")
def settings() -> FunctionalTestSettings:
    return test_settings


@pytest.fixture(scope="session")
def testdata_path(settings: FunctionalTestSettings) -> Path:
    return settings.testdata.path
