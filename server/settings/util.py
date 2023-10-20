# Loading `.env` files
# See docs: https://gitlab.com/mkleehammer/autoconfig
from os import environ
from pathlib import Path

from decouple import AutoConfig

BASE_DIR = Path(__file__).parent.parent.parent
config = AutoConfig(search_path=BASE_DIR.joinpath("config"))

environ.setdefault("DJANGO_ENV", config("DJANGO_ENV", "development"))
_ENV = environ["DJANGO_ENV"]
