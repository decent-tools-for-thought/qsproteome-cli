from __future__ import annotations

import argparse
import json
import sys
from typing import Any, NoReturn

from .client import ApiClient, ApiError
from .documentation import render_doc
from .formatting import render_data
from .metadata import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    LOOKUP_DOC_MAP,
    MODEL_ENGINES,
)
from .serve import (
    build_biocyc_widget_script,
    build_complexportal_widget_script,
    build_preview_html,
    start_preview_server,
)


class HelpOnErrorArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.print_help(sys.stderr)
        self.exit(2, f"{self.prog}: error: {message}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = HelpOnErrorArgumentParser(
        prog="qsproteome",
        description=(
            "Command-line client for the documented QSProteome API "
            "and widget preview servers"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--base-url", default=DEFAULT_BASE_URL, help=f"Base URL (default: {DEFAULT_BASE_URL})"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="HTTP timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--format",
        choices=("table", "json"),
        default="table",
        help="Lookup output format (default: table)",
    )
    subparsers = parser.add_subparsers(dest="command")

    lookup = subparsers.add_parser("lookup", help="Call documented lookup endpoints")
    lookup_sub = lookup.add_subparsers(dest="lookup_command")

    biocyc = lookup_sub.add_parser("biocyc", help=LOOKUP_DOC_MAP["biocyc"].summary)
    _add_lookup_runtime_arguments(biocyc)
    biocyc.add_argument("org_id")
    biocyc.add_argument("complex_id")
    biocyc.add_argument("--model-engine", choices=MODEL_ENGINES, default="any")
    biocyc.set_defaults(handler=_lookup_biocyc)

    complexportal = lookup_sub.add_parser(
        "complexportal", help=LOOKUP_DOC_MAP["complexportal"].summary
    )
    _add_lookup_runtime_arguments(complexportal)
    complexportal.add_argument("complex_id")
    complexportal.add_argument("--model-engine", choices=MODEL_ENGINES, default="any")
    complexportal.set_defaults(handler=_lookup_complexportal)

    uniprot = lookup_sub.add_parser("uniprot", help=LOOKUP_DOC_MAP["uniprot"].summary)
    _add_lookup_runtime_arguments(uniprot)
    uniprot.add_argument("uniprot_id")
    uniprot.add_argument("--iptm", type=float)
    uniprot.add_argument("--model-engine", choices=MODEL_ENGINES, default="any")
    uniprot.set_defaults(handler=_lookup_uniprot)

    pdb = lookup_sub.add_parser("pdb", help=LOOKUP_DOC_MAP["pdb"].summary)
    _add_lookup_runtime_arguments(pdb)
    pdb.add_argument("pdb_id")
    pdb.add_argument("--iptm", type=float)
    pdb.add_argument("--model-engine", choices=MODEL_ENGINES, default="any")
    pdb.set_defaults(handler=_lookup_pdb)

    gene_signature = lookup_sub.add_parser(
        "gene-signature", help=LOOKUP_DOC_MAP["gene-signature"].summary
    )
    _add_lookup_runtime_arguments(gene_signature)
    gene_signature.add_argument(
        "signature", help='JSON object string, for example \'{"P01308": 1, "Q76KP1": 1}\''
    )
    gene_signature.add_argument("--model-engine", choices=MODEL_ENGINES, default="any")
    gene_signature.set_defaults(handler=_lookup_gene_signature)

    serve = subparsers.add_parser("serve", help="Start a local preview site for documented widgets")
    serve_sub = serve.add_subparsers(dest="serve_command")

    serve_biocyc = serve_sub.add_parser("biocyc", help="Start the documented BioCyc widget preview")
    _add_serve_runtime_arguments(serve_biocyc)
    serve_biocyc.add_argument("org_id")
    serve_biocyc.add_argument("complex_id")
    serve_biocyc.add_argument("--model-engine", choices=MODEL_ENGINES, default="colabfold")
    serve_biocyc.add_argument("--host", default="127.0.0.1")
    serve_biocyc.add_argument("--port", type=int, default=8000)
    serve_biocyc.set_defaults(handler=_serve_biocyc)

    serve_complexportal = serve_sub.add_parser(
        "complexportal", help="Start the documented ComplexPortal widget preview"
    )
    _add_serve_runtime_arguments(serve_complexportal)
    serve_complexportal.add_argument("complex_id")
    serve_complexportal.add_argument("--model-engine", choices=MODEL_ENGINES, default="colabfold")
    serve_complexportal.add_argument("--host", default="127.0.0.1")
    serve_complexportal.add_argument("--port", type=int, default=8000)
    serve_complexportal.set_defaults(handler=_serve_complexportal)

    doc = subparsers.add_parser("doc", help="Describe the whole command surface or one subtree")
    doc.add_argument("surface", nargs="?", choices=("lookup", "serve"))
    doc.add_argument("topic", nargs="?")
    doc.set_defaults(handler=_doc_handler)

    return parser


def _add_lookup_runtime_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=argparse.SUPPRESS)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help=argparse.SUPPRESS)
    parser.add_argument(
        "--format", choices=("table", "json"), default="table", help=argparse.SUPPRESS
    )


def _add_serve_runtime_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=argparse.SUPPRESS)


def _lookup_biocyc(client: ApiClient, args: argparse.Namespace) -> Any:
    return client.request(
        "/api/lookup-entry-by-biocyc",
        query={
            "orgId": args.org_id,
            "complexId": args.complex_id,
            "modelEngine": _filter_any(args.model_engine),
        },
    )


def _lookup_complexportal(client: ApiClient, args: argparse.Namespace) -> Any:
    return client.request(
        "/api/lookup-entry-by-complexportal",
        query={"id": args.complex_id, "modelEngine": _filter_any(args.model_engine)},
    )


def _lookup_uniprot(client: ApiClient, args: argparse.Namespace) -> Any:
    return client.request(
        "/api/lookup-entry-by-uniprot-id",
        query={
            "uniprotId": args.uniprot_id,
            "iptm": _normalize_float(args.iptm),
            "modelEngine": _filter_any(args.model_engine),
        },
    )


def _lookup_pdb(client: ApiClient, args: argparse.Namespace) -> Any:
    return client.request(
        "/api/lookup-entry-by-pdb-id",
        query={
            "pdbId": args.pdb_id,
            "iptm": _normalize_float(args.iptm),
            "modelEngine": _filter_any(args.model_engine),
        },
    )


def _lookup_gene_signature(client: ApiClient, args: argparse.Namespace) -> Any:
    try:
        signature = json.loads(args.signature)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid signature JSON: {exc}") from exc
    if not isinstance(signature, dict) or not signature:
        raise ValueError("Signature JSON must be a non-empty object.")
    return client.request(
        "/api/lookup-entry-by-genesignature",
        method="POST",
        query={"modelEngine": _filter_any(args.model_engine)},
        json_body={"signature": signature},
    )


def _serve_biocyc(_: ApiClient | None, args: argparse.Namespace) -> None:
    script = build_biocyc_widget_script(
        args.org_id,
        args.complex_id,
        model_engine=args.model_engine,
        parent="#viewer",
        base_url=args.base_url,
    )
    html = build_preview_html(
        title=f"QSProteome BioCyc Preview: {args.org_id} / {args.complex_id}",
        subtitle="Local preview page for the documented QSProteome BioCyc Mol* widget.",
        widget_script=script,
    )
    _run_server(html, host=args.host, port=args.port)


def _serve_complexportal(_: ApiClient | None, args: argparse.Namespace) -> None:
    script = build_complexportal_widget_script(
        args.complex_id,
        model_engine=args.model_engine,
        parent="#viewer",
        base_url=args.base_url,
    )
    html = build_preview_html(
        title=f"QSProteome ComplexPortal Preview: {args.complex_id}",
        subtitle="Local preview page for the documented QSProteome ComplexPortal Mol* widget.",
        widget_script=script,
    )
    _run_server(html, host=args.host, port=args.port)


def _doc_handler(_: ApiClient | None, args: argparse.Namespace) -> str:
    return render_doc(args.surface, args.topic)


def _filter_any(value: str) -> str | None:
    return None if value == "any" else value


def _normalize_float(value: float | None) -> str | None:
    return None if value is None else str(value)


def _print_contextual_help(parser: argparse.ArgumentParser, args: argparse.Namespace) -> bool:
    if args.command is None:
        parser.print_help()
        return True
    subparsers_action = next(
        action for action in parser._actions if action.dest == "command"
    )
    if args.command in {"lookup", "serve"} and getattr(args, f"{args.command}_command") is None:
        choices = getattr(subparsers_action, "choices", {})
        choices[args.command].print_help()
        return True
    return False


def _run_server(html: str, *, host: str, port: int) -> None:
    server, url = start_preview_server(html, host=host, port=port)
    print(f"Serving QSProteome preview at {url} (Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if _print_contextual_help(parser, args):
        return 0

    client = (
        None
        if args.command in {"doc", "serve"}
        else ApiClient(base_url=args.base_url, timeout=args.timeout)
    )
    try:
        result = args.handler(client, args)
    except (ApiError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if result is None:
        return 0
    if isinstance(result, str):
        print(result)
    else:
        print(render_data(result, args.format))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
