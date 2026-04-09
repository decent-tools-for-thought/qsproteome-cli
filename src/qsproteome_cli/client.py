from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .metadata import DEFAULT_BASE_URL, DEFAULT_TIMEOUT


class ApiError(RuntimeError):
    pass


@dataclass(frozen=True)
class PreparedRequest:
    method: str
    url: str
    body: bytes | None = None
    content_type: str | None = None


def prepare_request(
    path: str,
    *,
    method: str = "GET",
    base_url: str = DEFAULT_BASE_URL,
    query: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
) -> PreparedRequest:
    clean_query = {
        key: value for key, value in (query or {}).items() if value is not None and value != ""
    }
    url = f"{base_url.rstrip('/')}{path}"
    if clean_query:
        url = f"{url}?{urlencode(clean_query)}"
    body = None
    content_type = None
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        content_type = "application/json"
    return PreparedRequest(method=method, url=url, body=body, content_type=content_type)


class ApiClient:
    def __init__(
        self, *, base_url: str = DEFAULT_BASE_URL, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def request(
        self,
        path: str,
        *,
        method: str = "GET",
        query: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        prepared = prepare_request(
            path,
            method=method,
            base_url=self.base_url,
            query=query,
            json_body=json_body,
        )
        headers = {
            "Accept": "application/json",
            "User-Agent": "qsproteome-cli/0.1.0",
        }
        if prepared.content_type:
            headers["Content-Type"] = prepared.content_type
        request = Request(prepared.url, data=prepared.body, headers=headers, method=prepared.method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = response.read().decode("utf-8")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace").strip()
            raise ApiError(f"HTTP {exc.code}: {detail or exc.reason}") from exc
        except URLError as exc:
            raise ApiError(f"Network error: {exc.reason}") from exc
        try:
            return json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ApiError(f"Response was not valid JSON: {exc}") from exc
