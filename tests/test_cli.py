from __future__ import annotations

import json
import threading
import urllib.request

import pytest

from qsproteome_cli.cli import build_parser, main
from qsproteome_cli.client import prepare_request
from qsproteome_cli.documentation import render_doc
from qsproteome_cli.serve import (
    build_biocyc_widget_script,
    build_complexportal_widget_script,
    build_preview_html,
    start_preview_server,
)


def test_bare_parser_has_no_command() -> None:
    parser = build_parser()
    args = parser.parse_args([])
    assert args.command is None


def test_top_level_exposes_expected_commands() -> None:
    parser = build_parser()
    subparsers = next(action for action in parser._actions if action.dest == "command")
    choices = getattr(subparsers, "choices", {})
    assert {"lookup", "serve", "doc"} <= set(choices)


def test_doc_overview_mentions_all_lookup_topics() -> None:
    doc = render_doc()
    assert "lookup-entry-by-biocyc" in doc
    assert "lookup-entry-by-complexportal" in doc
    assert "lookup-entry-by-uniprot-id" in doc
    assert "lookup-entry-by-pdb-id" in doc
    assert "lookup-entry-by-genesignature" in doc


def test_partial_lookup_path_prints_help_and_exits_zero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main(["lookup"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "biocyc" in out
    assert "gene-signature" in out


def test_partial_serve_path_prints_help_and_exits_zero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main(["serve"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "complexportal" in out


def test_prepare_request_omits_any_model_engine() -> None:
    request = prepare_request(
        "/api/lookup-entry-by-complexportal",
        query={"id": "CPX-4822", "modelEngine": None},
    )
    assert request.url == "https://qsproteome.org/api/lookup-entry-by-complexportal?id=CPX-4822"


def test_prepare_request_encodes_gene_signature_post_body() -> None:
    request = prepare_request(
        "/api/lookup-entry-by-genesignature",
        method="POST",
        query={"modelEngine": "alphafoldserver"},
        json_body={"signature": {"P01308": 1}},
    )
    assert request.method == "POST"
    assert request.url.endswith("/api/lookup-entry-by-genesignature?modelEngine=alphafoldserver")
    assert request.body is not None
    assert json.loads(request.body.decode("utf-8")) == {"signature": {"P01308": 1}}


def test_gene_signature_invalid_json_returns_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main(["lookup", "gene-signature", "{"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "Invalid signature JSON" in err


def test_biocyc_widget_script_matches_docs() -> None:
    snippet = build_biocyc_widget_script("ECOLI", "ABC-12-CPLX")
    assert "biocyc-molstar-widget.js" in snippet
    assert "orgid=ECOLI" in snippet
    assert "complexid=ABC-12-CPLX" in snippet


def test_complexportal_widget_script_matches_docs() -> None:
    snippet = build_complexportal_widget_script(
        "CPX-4822",
        model_engine="colabfold",
        parent="#viewer",
    )
    assert "complexportal-molstar-widget.js" in snippet
    assert "id=CPX-4822" in snippet
    assert "modelEngine=colabfold" in snippet


def test_doc_lookup_topic_mentions_examples() -> None:
    doc = render_doc("lookup", "gene-signature")
    assert "alphafoldserver" in doc
    assert "P01308" in doc


def test_doc_serve_topic_mentions_script_path() -> None:
    doc = render_doc("serve", "biocyc")
    assert "/js/biocyc-molstar-widget.js" in doc


def test_lookup_accepts_runtime_flags_after_subcommand(
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main(["lookup", "gene-signature", '{"P01308": 1}', "--format", "json"])
    err = capsys.readouterr().err
    assert rc in {0, 1}
    assert "unrecognized arguments" not in err


def test_preview_server_serves_embedded_page() -> None:
    html = build_preview_html(
        title="Preview",
        subtitle="Local page",
        widget_script=build_complexportal_widget_script("CPX-4822"),
    )
    server, url = start_preview_server(html, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            body = response.read().decode("utf-8")
    finally:
        server.shutdown()
        server.server_close()
    assert "qsproteome serve" in body
    assert "complexportal-molstar-widget.js" in body
