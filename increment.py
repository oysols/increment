#!/usr/bin/env python3
from functools import wraps
import os
import sqlite3
from typing import Tuple, Callable, List, Any

import markdown  # type: ignore
from flask import Flask, request, escape  # type: ignore

AUTH_KEY = os.getenv("AUTH_KEY")
app = Flask(__name__)


class Sqlite3Dict():
    def __init__(self, path: str) -> None:
        self.conn = sqlite3.connect(path)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS dict (" +
                "key VARCHAR PRIMARY KEY, value INT)")
        self.conn.commit()

    def get(self, key: str, default: int=0) -> int:
        self.cur.execute('SELECT value FROM dict WHERE key=?', (key, ))
        data = self.cur.fetchone()
        if data is None:
            return default
        return int(data[0])

    def __setitem__(self, key: str, value: int) -> None:
        self.cur.execute('REPLACE INTO dict (key, value) VALUES (?, ?)',
                (key, value))
        self.conn.commit()

    def items(self) -> List[Tuple[str, int]]:
        self.cur.execute('SELECT key, value FROM dict')
        return self.cur.fetchall()


db = Sqlite3Dict("db.sqlite")


class Unauthorized(Exception):
    status_code = 401
    detail = "Unauthorized"


@app.errorhandler(Unauthorized)
def error_handler(e: Unauthorized) -> Tuple[str, int]:
    return "{} {} {}".format(e.status_code, e.detail.upper(), e), e.status_code


def authorization_required(func: Callable) -> Callable:
    @wraps(func)
    def decorator(*args: Any, **kwargs: Any) -> Any:
        auth = request.args.get("auth")
        if AUTH_KEY and auth != AUTH_KEY:
            raise Unauthorized
        else:
            return func(*args, **kwargs)
    return decorator


@app.route("/next/<key>")
@authorization_required
def increment(key: str) -> Tuple[str, int]:
    value = int(db.get(key, -1)) + 1
    db[key] = value
    return str(value), 200


@app.route("/set_next/<key>/<int:value>")
@authorization_required
def set_next(key: str, value: int) -> Tuple[str, int]:
    db[key] = value - 1
    return "Next value will be: {}".format(value), 200


@app.route("/list")
@authorization_required
def list() -> Tuple[str, int]:
    out = ""
    for key, value in db.items():
        out += str(escape("{},{}".format(key, value)))
        out += "<br>\n"
    return out, 200


@app.route("/")
def index() -> Tuple[str, int]:
    with open("README.md", "r") as f:
        body = markdown.markdown(f.read())
    return "<html><title>Incrementing value as a service</title><body>" + \
            body + \
            "</body></html>", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
