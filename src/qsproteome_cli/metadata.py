from __future__ import annotations

from dataclasses import dataclass
from typing import Any

DEFAULT_BASE_URL = "https://qsproteome.org"
DEFAULT_TIMEOUT = 30.0
DEFAULT_PARENT_SELECTOR = "#your-div"
MODEL_ENGINES = ("any", "colabfold", "alphafoldserver")
API_RATE_LIMIT_NOTE = "Documented public rate limit: 2 requests per second."


@dataclass(frozen=True)
class ParameterDoc:
    name: str
    description: str
    required: bool = True
    kind: str = "string"


@dataclass(frozen=True)
class LookupDoc:
    command: str
    title: str
    method: str
    path: str
    summary: str
    details: str
    positional_parameters: tuple[ParameterDoc, ...]
    option_parameters: tuple[ParameterDoc, ...]
    body_parameters: tuple[ParameterDoc, ...] = ()
    examples: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    response_notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class WidgetDoc:
    command: str
    title: str
    script_path: str
    summary: str
    details: str
    positional_parameters: tuple[ParameterDoc, ...]
    option_parameters: tuple[ParameterDoc, ...]
    notes: tuple[str, ...] = ()


LOOKUP_DOCS: tuple[LookupDoc, ...] = (
    LookupDoc(
        command="biocyc",
        title="BioCyc lookup",
        method="GET",
        path="/api/lookup-entry-by-biocyc",
        summary="Retrieve QSProteome entries by BioCyc organism code and complex ID.",
        details=(
            "Returns the best matching model set for a BioCyc complex. The site docs say "
            "results are deduplicated by gene signature and ordered by ipTM score."
        ),
        positional_parameters=(
            ParameterDoc("org_id", "BioCyc organism code, for example ECOLI."),
            ParameterDoc("complex_id", "BioCyc complex ID, for example ABC-12-CPLX."),
        ),
        option_parameters=(
            ParameterDoc(
                "model_engine",
                "Model source filter. Docs show colabfold or any; "
                "live API also accepts alphafoldserver.",
                required=False,
            ),
        ),
        examples=(
            "qsproteome lookup biocyc ECOLI ABC-12-CPLX",
            "qsproteome lookup biocyc ECOLI ABC-12-CPLX --model-engine colabfold --format json",
        ),
        notes=("QSProteome docs show this for BioCyc references such as ECOLI / ABC-12-CPLX.",),
        response_notes=(
            "Successful responses are usually JSON arrays of entry objects.",
            "A no-match response may be a JSON object with a message field.",
        ),
    ),
    LookupDoc(
        command="complexportal",
        title="ComplexPortal lookup",
        method="GET",
        path="/api/lookup-entry-by-complexportal",
        summary="Retrieve QSProteome entries by ComplexPortal ID.",
        details=(
            "Returns the best matching model set for a ComplexPortal complex. The site docs say "
            "results are deduplicated by gene signature and ordered by ipTM score."
        ),
        positional_parameters=(
            ParameterDoc("complex_id", "ComplexPortal ID, for example CPX-4822."),
        ),
        option_parameters=(
            ParameterDoc(
                "model_engine",
                "Model source filter. Docs show colabfold or any; "
                "live API also accepts alphafoldserver.",
                required=False,
            ),
        ),
        examples=(
            "qsproteome lookup complexportal CPX-4822",
            "qsproteome lookup complexportal CPX-4822 --model-engine colabfold --format json",
        ),
        response_notes=(
            "Successful responses are usually JSON arrays of entry objects.",
            "Observed entries may include ComplexPortal-specific fields like "
            "complexportalReferenceSignature.",
        ),
    ),
    LookupDoc(
        command="uniprot",
        title="UniProt lookup",
        method="GET",
        path="/api/lookup-entry-by-uniprot-id",
        summary="Retrieve QSProteome entries by UniProt accession.",
        details=(
            "Returns models matching a UniProt accession and can filter results by minimum ipTM."
        ),
        positional_parameters=(
            ParameterDoc("uniprot_id", "UniProt accession, for example P0AEQ4."),
        ),
        option_parameters=(
            ParameterDoc("iptm", "Optional minimum ipTM threshold.", required=False, kind="float"),
            ParameterDoc(
                "model_engine",
                "Model source filter. Docs show colabfold or any; "
                "live API also accepts alphafoldserver.",
                required=False,
            ),
        ),
        examples=(
            "qsproteome lookup uniprot P0AEQ4",
            "qsproteome lookup uniprot P0AEQ4 --iptm 0.8 --format json",
        ),
        response_notes=(
            "Successful responses are usually JSON arrays of entry objects.",
            "A no-match response may be a JSON object such as "
            "{'message': 'No matching entries found ...'}.",
        ),
    ),
    LookupDoc(
        command="pdb",
        title="PDB lookup",
        method="GET",
        path="/api/lookup-entry-by-pdb-id",
        summary="Retrieve QSProteome entries by PDB identifier.",
        details=(
            "Returns deduplicated QSProteome models matching a PDB ID and can filter results by "
            "minimum ipTM. The site docs say responses include matching mmalign hits."
        ),
        positional_parameters=(ParameterDoc("pdb_id", "PDB ID, for example 2QI9."),),
        option_parameters=(
            ParameterDoc("iptm", "Optional minimum ipTM threshold.", required=False, kind="float"),
            ParameterDoc(
                "model_engine",
                "Model source filter. Docs show colabfold or any; "
                "live API also accepts alphafoldserver.",
                required=False,
            ),
        ),
        examples=(
            "qsproteome lookup pdb 2QI9",
            "qsproteome lookup pdb 2QI9 --iptm 0.6 --format json",
        ),
        response_notes=(
            "Successful responses are usually JSON arrays of entry objects.",
            "A no-match response may be a JSON object with a message field.",
        ),
    ),
    LookupDoc(
        command="gene-signature",
        title="Gene signature lookup",
        method="POST",
        path="/api/lookup-entry-by-genesignature",
        summary="Retrieve QSProteome entries by gene stoichiometry signature.",
        details=(
            "Accepts a JSON object mapping UniProt IDs or amino acid sequences to stoichiometry. "
            "Sequence values are hashed by the backend to match structure entries."
        ),
        positional_parameters=(
            ParameterDoc(
                "signature",
                "JSON object string mapping UniProt IDs or amino acid sequences to stoichiometry.",
                kind="json",
            ),
        ),
        option_parameters=(
            ParameterDoc(
                "model_engine",
                "Model source filter. Docs show colabfold or any; "
                "live API also accepts alphafoldserver.",
                required=False,
            ),
        ),
        body_parameters=(
            ParameterDoc("signature", "JSON body field sent as {'signature': ...}.", kind="json"),
        ),
        examples=(
            """qsproteome lookup gene-signature '{"P01308": 1, "Q76KP1": 1}'""",
            "qsproteome lookup gene-signature "
            """'{"P01308": 1, "Q76KP1": 1}' --model-engine alphafoldserver --format json""",
        ),
        response_notes=(
            "Successful responses are usually JSON arrays of entry objects.",
            "Observed responses can include alphafoldserver entries when requested "
            "or when model filtering is omitted.",
        ),
    ),
)


WIDGET_DOCS: tuple[WidgetDoc, ...] = (
    WidgetDoc(
        command="biocyc",
        title="BioCyc Mol* preview",
        script_path="/js/biocyc-molstar-widget.js",
        summary="Serve a local preview page for the documented BioCyc Mol* widget.",
        details=(
            "Embeds the BioCyc Mol* viewer shown on the QSProteome API usage page "
            "into a local preview site."
        ),
        positional_parameters=(
            ParameterDoc("org_id", "BioCyc organism code, for example ECOLI."),
            ParameterDoc("complex_id", "BioCyc complex ID, for example ABC-12-CPLX."),
        ),
        option_parameters=(
            ParameterDoc("model_engine", "Widget model source filter.", required=False),
            ParameterDoc(
                "host", "Host/interface to bind for the local preview server.", required=False
            ),
            ParameterDoc("port", "Port to bind for the local preview server.", required=False),
        ),
        notes=(
            "Widget notes on the site: click genes to highlight chains and "
            "toggle AlphaFold/default color schemes.",
        ),
    ),
    WidgetDoc(
        command="complexportal",
        title="ComplexPortal Mol* preview",
        script_path="/js/complexportal-molstar-widget.js",
        summary="Serve a local preview page for the documented ComplexPortal Mol* widget.",
        details=(
            "Embeds the ComplexPortal Mol* viewer shown on the QSProteome API "
            "usage page into a local preview site."
        ),
        positional_parameters=(
            ParameterDoc("complex_id", "ComplexPortal ID, for example CPX-4822."),
        ),
        option_parameters=(
            ParameterDoc("model_engine", "Widget model source filter.", required=False),
            ParameterDoc(
                "host", "Host/interface to bind for the local preview server.", required=False
            ),
            ParameterDoc("port", "Port to bind for the local preview server.", required=False),
        ),
        notes=(
            "Widget notes on the site: click genes to highlight chains and "
            "toggle AlphaFold/default color schemes.",
        ),
    ),
)


LOOKUP_DOC_MAP = {doc.command: doc for doc in LOOKUP_DOCS}
WIDGET_DOC_MAP = {doc.command: doc for doc in WIDGET_DOCS}


def entry_summary_fields() -> tuple[str, ...]:
    return (
        "entryId",
        "model_engine",
        "format",
        "iptm",
        "submitted",
        "author_first",
        "author_last",
        "qsproteomeUrl",
    )


def build_common_response_notes() -> tuple[str, ...]:
    return (
        "Observed entry objects include fields such as entryId, qsproteomeUrl, "
        "imageUrl, structureUrl, format, iptm, geneSignature, stoichiometry, "
        "submitted, author metadata, model_engine, and usage_terms.",
        "Stoichiometry items are nested objects and may expose chain_ids plus "
        "name and stoich. Some endpoints also expose UniProt identifiers there.",
    )


def command_inventory() -> dict[str, Any]:
    return {
        "lookups": [doc.command for doc in LOOKUP_DOCS],
        "serve": [doc.command for doc in WIDGET_DOCS],
    }
