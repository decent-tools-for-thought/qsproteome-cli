from __future__ import annotations

import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlencode

from .metadata import DEFAULT_BASE_URL, DEFAULT_PARENT_SELECTOR


def build_biocyc_widget_script(
    org_id: str,
    complex_id: str,
    *,
    model_engine: str = "colabfold",
    parent: str = DEFAULT_PARENT_SELECTOR,
    base_url: str = DEFAULT_BASE_URL,
) -> str:
    script_url = f"{base_url.rstrip('/')}/js/biocyc-molstar-widget.js"
    query: dict[str, str] = {"orgid": org_id, "complexid": complex_id, "parent": parent}
    if model_engine != "any":
        query["modelEngine"] = model_engine
    return f'<script src="{script_url}?{urlencode(query)}"></script>'


def build_complexportal_widget_script(
    complex_id: str,
    *,
    model_engine: str = "colabfold",
    parent: str = "#viewer",
    base_url: str = DEFAULT_BASE_URL,
) -> str:
    script_url = f"{base_url.rstrip('/')}/js/complexportal-molstar-widget.js"
    query: dict[str, str] = {"id": complex_id, "parent": parent}
    if model_engine != "any":
        query["modelEngine"] = model_engine
    return f'<script src="{script_url}?{urlencode(query)}"></script>'


def build_preview_html(
    *, title: str, subtitle: str, widget_script: str, container_id: str = "viewer"
) -> str:
    escaped_title = html.escape(title)
    escaped_subtitle = html.escape(subtitle)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f3efe4;
      --ink: #142018;
      --muted: #516154;
      --panel: #fffdf7;
      --line: #cfd6c7;
      --accent: #2f6c4f;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Iosevka Aile", "IBM Plex Sans", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(47,108,79,0.12), transparent 28rem),
        linear-gradient(180deg, #f7f4ea, var(--bg));
      color: var(--ink);
    }}
    main {{
      width: min(1100px, calc(100vw - 2rem));
      margin: 0 auto;
      padding: 2rem 0 3rem;
    }}
    header {{
      margin-bottom: 1.25rem;
    }}
    h1 {{
      margin: 0 0 0.4rem;
      font-size: clamp(2rem, 4vw, 3.4rem);
      line-height: 0.95;
      letter-spacing: -0.03em;
    }}
    p {{
      margin: 0;
      color: var(--muted);
      max-width: 72ch;
    }}
    .panel {{
      background: color-mix(in srgb, var(--panel) 94%, white);
      border: 1px solid var(--line);
      border-radius: 20px;
      overflow: hidden;
      box-shadow: 0 20px 60px rgba(20, 32, 24, 0.08);
    }}
    .meta {{
      display: flex;
      gap: 0.75rem;
      flex-wrap: wrap;
      padding: 1rem 1.25rem;
      border-bottom: 1px solid var(--line);
      background: rgba(47,108,79,0.04);
      font-size: 0.95rem;
    }}
    .meta code {{
      background: rgba(47,108,79,0.08);
      padding: 0.15rem 0.45rem;
      border-radius: 999px;
      color: var(--accent);
    }}
    #{container_id} {{
      min-height: 72vh;
      height: 72vh;
      width: 100%;
      background: linear-gradient(180deg, rgba(47,108,79,0.04), rgba(47,108,79,0.01));
    }}
    @media (max-width: 720px) {{
      main {{ width: min(100vw - 1rem, 1100px); padding-top: 1rem; }}
      #{container_id} {{ min-height: 60vh; height: 60vh; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>{escaped_title}</h1>
      <p>{escaped_subtitle}</p>
    </header>
    <section class="panel">
      <div class="meta">
        <span>Served by <code>qsproteome serve</code></span>
        <span>Widget target <code>#{container_id}</code></span>
      </div>
      <div id="{container_id}"></div>
    </section>
    {widget_script}
  </main>
</body>
</html>
"""


def start_preview_server(
    html_document: str,
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
) -> tuple[ThreadingHTTPServer, str]:
    encoded = html_document.encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path not in {"/", "/index.html"}:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            del format, args

    server = ThreadingHTTPServer((host, port), Handler)
    bound_host, bound_port = server.server_address[:2]
    host_text = bound_host.decode() if isinstance(bound_host, bytes) else str(bound_host)
    return server, f"http://{host_text}:{bound_port}/"
