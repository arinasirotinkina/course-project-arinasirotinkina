import requests
from starlette.responses import HTMLResponse


def vulnerable_html(user_input: str):
    return HTMLResponse(f"<div>{user_input}</div>")


def call_requests():
    r = requests.get("http://example.com")
    return r.status_code
