import re

import mmc


def test_version():
    assert re.match(r"^\d+\.\d+\.\d+", mmc.__version__)
