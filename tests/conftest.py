import json
from pathlib import Path
from typing import Union
from urllib.parse import urlparse
from uuid import UUID

import pytest

RESOURCE = Path(__file__).parent / "resource"

JSONVal = Union[
    None, bool, str, float, int, list["JSONVal"], dict[str, "JSONVal"]
]


@pytest.fixture
def user1():
    return UUID(int=1)


@pytest.fixture
def user2():
    return UUID(int=2)


@pytest.fixture
def group():
    return UUID(int=11)


@pytest.fixture
def mock_config():
    from server import config

    config.__data = {
        "im": {
            "app_id": "123456",
            "secret_key": "123456",
            "admin": "admin",
        },
    }


response = None


def search_resource() -> dict[str, JSONVal]:
    global response

    if response is None:
        response = {}

        for file in RESOURCE.glob("**/*.json"):
            url = file.relative_to(RESOURCE).with_suffix("").as_posix()
            with open(file, "r", encoding="utf-8") as f:
                response[url] = json.load(f)

    return response


@pytest.fixture
def mock_im_api(mocker, mock_config):
    def _mock_im_api(url) -> JSONVal:
        url = urlparse(url)
        return search_resource().get(f"{url.hostname}{url.path}", None)

    class MockPost:
        def __init__(self, url, json=None):
            self.url = url

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def json(self):
            return _mock_im_api(self.url)

    mock_client = mocker.AsyncMock()

    mock_client.post = MockPost

    mocker.patch("aiohttp.ClientSession", return_value=mock_client)
