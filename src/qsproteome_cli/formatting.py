from __future__ import annotations

import json
from typing import Any


def render_data(data: Any, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    return render_table(data)


def render_table(data: Any) -> str:
    if isinstance(data, dict):
        if "message" in data and len(data) == 1:
            return str(data["message"])
        return "\n".join(
            f"{key}: {json.dumps(value, ensure_ascii=True)}" for key, value in data.items()
        )
    if not isinstance(data, list):
        return json.dumps(data, indent=2, sort_keys=True)
    if not data:
        return "(no results)"
    if not all(isinstance(item, dict) for item in data):
        return json.dumps(data, indent=2, sort_keys=True)

    rows = []
    for item in data:
        rows.append(
            [
                _stringify(item.get("entryId")),
                _stringify(item.get("model_engine")),
                _stringify(item.get("format")),
                _stringify(item.get("iptm")),
                _stringify(item.get("submitted")),
                _author(item),
                _stringify(item.get("qsproteomeUrl")),
            ]
        )
    headers = ["entryId", "engine", "format", "iptm", "submitted", "author", "entry"]
    return _render_grid(headers, rows) + _render_stoichiometry_section(data)


def _author(item: dict[str, Any]) -> str:
    first = _stringify(item.get("author_first"))
    last = _stringify(item.get("author_last"))
    full = " ".join(part for part in (first, last) if part and part != "-").strip()
    return full or "-"


def _render_stoichiometry_section(data: list[dict[str, Any]]) -> str:
    lines = ["", "Stoichiometry:"]
    for item in data:
        parts = []
        for component in item.get("stoichiometry", []):
            if not isinstance(component, dict):
                continue
            name = str(component.get("name") or "?")
            stoich = component.get("stoich")
            chains = component.get("chain_ids") or []
            chain_suffix = f" chains={','.join(str(c) for c in chains)}" if chains else ""
            parts.append(f"{name} x{stoich}{chain_suffix}")
        summary = "; ".join(parts) if parts else "-"
        lines.append(f"- {item.get('entryId', '?')}: {summary}")
    return "\n".join(lines)


def _render_grid(headers: list[str], rows: list[list[str]]) -> str:
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    header_line = "  ".join(header.ljust(widths[index]) for index, header in enumerate(headers))
    separator = "  ".join("-" * widths[index] for index in range(len(headers)))
    body = ["  ".join(cell.ljust(widths[index]) for index, cell in enumerate(row)) for row in rows]
    return "\n".join([header_line, separator, *body])


def _stringify(value: Any) -> str:
    if value is None or value == "":
        return "-"
    return str(value)
