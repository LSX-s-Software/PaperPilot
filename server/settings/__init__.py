import os
import sys
from pathlib import Path

from server.settings.components import *  # noqa
from server.settings.util import _ENV

if _ENV == "development":
    from server.settings.environments.development import *  # noqa
elif _ENV == "production":
    from server.settings.environments.production import *  # noqa
elif _ENV == "test":
    from server.settings.environments.test import *  # noqa

if os.path.exists(
    os.path.join(os.path.dirname(__file__), "environments", "local.py")
):
    from server.settings.environments.local import *  # noqa
