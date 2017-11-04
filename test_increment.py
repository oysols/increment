import os
from typing import Any

import pytest  # type: ignore

import increment


@pytest.fixture
def client() -> Any:
    increment.AUTH_KEY = ""
    increment.db = increment.Sqlite3Dict("testdb.sqlite")
    client = increment.app.test_client()
    yield client
    os.remove("testdb.sqlite")


def test_increment(client: Any) -> None:
    res = client.get('/next/test1')
    res = client.get('/next/test1')
    assert res.data.decode() == "1"

    res = client.get('/next/test4')
    assert res.data.decode() == "0"


def test_set_value(client: Any) -> None:
    res = client.get('/set_next/test1/5')
    res = client.get('/next/test1')
    assert res.data.decode() == "5"

    res = client.get('/set_next/test1/0')
    res = client.get('/next/test1')
    assert res.data.decode() == "0"


def test_list(client: Any) -> None:
    res = client.get('/next/test1')
    res = client.get('/next/test1')
    res = client.get('/next/test2')
    res = client.get('/list')
    assert res.data.decode() == "test1,1<br>\ntest2,0<br>\n"


def test_auth(client: Any) -> None:
    res = client.get('/next/test1?auth=supersecret-pass')
    assert res.data.decode() == "0"

    increment.AUTH_KEY = "supersecret"
    res = client.get('/next/test1?auth=nope')
    assert res.status == "401 UNAUTHORIZED"

    res = client.get('/next/test1')
    assert res.status == "401 UNAUTHORIZED"

    res = client.get('/next/test1?auth=supersecret')
    assert res.data.decode() == "1"

    res = client.get('/set_next/test1/342')
    res = client.get('/next/test1?auth=supersecret')
    assert res.data.decode() == "2"

    res = client.get('/set_next/test1/342?auth=supersecret')
    res = client.get('/next/test1?auth=supersecret')
    assert res.data.decode() == "342"
