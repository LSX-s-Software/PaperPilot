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

# Build paths inside the project like this: BASE_DIR.joinpath('some')
# `pathlib` is better than writing: dirname(dirname(dirname(__file__)))
BASE_DIR = Path(__file__).parent.parent.parent
# 添加导包路径
sys.path.insert(0, str(BASE_DIR.joinpath("server", "apps")))
