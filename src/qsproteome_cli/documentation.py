from __future__ import annotations

from .metadata import (
    API_RATE_LIMIT_NOTE,
    DEFAULT_BASE_URL,
    DEFAULT_PARENT_SELECTOR,
    LOOKUP_DOC_MAP,
    LOOKUP_DOCS,
    MODEL_ENGINES,
    WIDGET_DOC_MAP,
    WIDGET_DOCS,
    build_common_response_notes,
)


def render_doc(surface: str | None = None, topic: str | None = None) -> str:
    if surface is None:
        return _render_overview()
    if surface == "lookup":
        if topic is None:
            return _render_lookup_overview()
        return _render_lookup_topic(topic)
    if surface == "serve":
        if topic is None:
            return _render_serve_overview()
        return _render_serve_topic(topic)
    raise ValueError(f"Unsupported doc surface: {surface}")


def _render_overview() -> str:
    lines = [
        "QSProteome CLI",
        "",
        "Purpose:",
        "Self-documenting CLI for the QSProteome API usage page "
        "and its documented widget previews.",
        "",
        "Command surfaces:",
        "- lookup: call each documented API lookup endpoint",
        "- serve: start a local preview site for each documented Mol* widget",
        "- doc: describe the whole command surface or one subtree",
        "",
        f"Base URL default: {DEFAULT_BASE_URL}",
        f"Model engine choices: {', '.join(MODEL_ENGINES)}",
        API_RATE_LIMIT_NOTE,
        "",
        "Lookups:",
    ]
    for lookup_doc in LOOKUP_DOCS:
        lines.append(f"- {lookup_doc.command}: {lookup_doc.summary}")
        lines.append(f"  endpoint: {lookup_doc.method} {lookup_doc.path}")
    lines.extend(["", "Preview servers:"])
    for widget_doc in WIDGET_DOCS:
        lines.append(f"- {widget_doc.command}: {widget_doc.summary}")
        lines.append(f"  script: {widget_doc.script_path}")
    lines.extend(
        [
            "",
            "Contextual help:",
            "- Bare invocation prints help and exits successfully.",
            "- Partial positional paths such as `qsproteome lookup` "
            "or `qsproteome serve` print subtree help.",
            "",
            "Try:",
            "- qsproteome doc lookup",
            "- qsproteome doc lookup biocyc",
            "- qsproteome doc serve complexportal",
        ]
    )
    return "\n".join(lines)


def _render_lookup_overview() -> str:
    lines = [
        "QSProteome lookup commands",
        "",
        "Each lookup command maps to one documented endpoint.",
        API_RATE_LIMIT_NOTE,
        "",
    ]
    for doc in LOOKUP_DOCS:
        lines.append(f"- {doc.command}: {doc.method} {doc.path}")
        lines.append(f"  {doc.summary}")
    lines.extend(
        [
            "",
            "Shared options:",
            "- --base-url: override the API base URL",
            "- --timeout: HTTP timeout in seconds",
            "- --format: table or json",
            f"- --model-engine: one of {', '.join(MODEL_ENGINES)}",
            "",
            "Use `qsproteome <command> --help` for parser help or "
            "`qsproteome doc lookup <topic>` for the long form docs.",
        ]
    )
    return "\n".join(lines)


def _render_lookup_topic(topic: str) -> str:
    doc = LOOKUP_DOC_MAP.get(topic)
    if doc is None:
        raise ValueError(f"Unknown lookup topic: {topic}")
    lines = [
        doc.title,
        "",
        f"Endpoint: {doc.method} {doc.path}",
        f"Summary: {doc.summary}",
        f"Details: {doc.details}",
        "",
        "Positional parameters:",
    ]
    for parameter in doc.positional_parameters:
        lines.append(f"- {parameter.name}: {parameter.description}")
    lines.append("")
    lines.append("Options:")
    for parameter in doc.option_parameters:
        suffix = "optional" if not parameter.required else "required"
        lines.append(f"- {parameter.name} ({suffix}): {parameter.description}")
    if doc.body_parameters:
        lines.extend(["", "JSON body:"])
        for parameter in doc.body_parameters:
            lines.append(f"- {parameter.name}: {parameter.description}")
    if doc.notes:
        lines.extend(["", "Notes:"])
        for note in doc.notes:
            lines.append(f"- {note}")
    lines.extend(["", "Response shape notes:"])
    for note in (*build_common_response_notes(), *doc.response_notes):
        lines.append(f"- {note}")
    lines.extend(["", "Examples:"])
    for example in doc.examples:
        lines.append(f"- {example}")
    return "\n".join(lines)


def _render_serve_overview() -> str:
    lines = [
        "QSProteome serve commands",
        "",
        "These commands start a small local site that embeds the documented QSProteome widgets.",
        f"Default parent selector: {DEFAULT_PARENT_SELECTOR}",
        "",
    ]
    for doc in WIDGET_DOCS:
        lines.append(f"- {doc.command}: {doc.script_path}")
        lines.append(f"  {doc.summary}")
    lines.extend(
        [
            "",
            "Shared options:",
            "- --host: host/interface to bind",
            "- --port: port to bind; use 0 for an ephemeral port",
            "- --model-engine: widget model filter",
            "",
            "Behavior:",
            "- Starts an HTTP server and serves a single HTML page with the widget embedded.",
            "- Prints the preview URL before entering the serve loop.",
        ]
    )
    return "\n".join(lines)


def _render_serve_topic(topic: str) -> str:
    doc = WIDGET_DOC_MAP.get(topic)
    if doc is None:
        raise ValueError(f"Unknown serve topic: {topic}")
    lines = [
        doc.title,
        "",
        f"Script: {doc.script_path}",
        f"Summary: {doc.summary}",
        f"Details: {doc.details} The CLI wraps this in a minimal local preview page.",
        "",
        "Positional parameters:",
    ]
    for parameter in doc.positional_parameters:
        lines.append(f"- {parameter.name}: {parameter.description}")
    lines.extend(["", "Options:"])
    for parameter in doc.option_parameters:
        lines.append(f"- {parameter.name}: {parameter.description}")
    if doc.notes:
        lines.extend(["", "Notes:"])
        for note in doc.notes:
            lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "Examples:",
            f"- qsproteome serve {topic} "
            + ("ECOLI ABC-12-CPLX" if topic == "biocyc" else "CPX-4822"),
            f"- qsproteome serve {topic} "
            + ("ECOLI ABC-12-CPLX" if topic == "biocyc" else "CPX-4822")
            + " --host 127.0.0.1 --port 8000",
        ]
    )
    return "\n".join(lines)
