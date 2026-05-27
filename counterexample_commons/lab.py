"""Finite unit-distance lab workflow helpers."""

from __future__ import annotations

import json
import re
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from sympy import Rational

from case_studies.erdos_unit_distance_2026.rational_mesh_baseline import (
    rational_mesh_points,
)
from counterexample_commons.experiments.sanitization import sanitize_for_export
from counterexample_commons.providers import GenerationRequest
from counterexample_commons.source_map import provenance_report_section
from counterexample_commons.validators.unit_distance import (
    count_unit_edges_exact,
)


FINITE_SCOPE = (
    "Finite exact validation only; not an asymptotic theorem, "
    "not a Sawin reproduction, and not a formal proof of a new bound."
)
RATIONAL_MESH_SCOPE = (
    "Finite rational mesh baseline - not Sawin's construction. "
    "Finite exact validation only; not evidence for exponent n^1.014."
)
AI_SCOPE = (
    "Finite AI candidate validation only; not Sawin's construction, "
    "not an asymptotic theorem, and not a new proof."
)
AI_VALIDATED = "AI_GENERATED_HYPOTHESIS_VALIDATED_FINITE_ONLY"
AI_REJECTED = "AI_GENERATED_HYPOTHESIS_REJECTED_BY_EXACT_VALIDATOR"


@dataclass
class ValidationRecord:
    """A finite exact validation result suitable for UI, plots, reports."""

    source: str
    configuration: str
    points: list[tuple[str, str]]
    edges: list[tuple[int, int]]
    status: str
    scientific_scope: str
    claimed_edges: int | None = None
    exact_edges: int = 0
    message: str = ""
    raw: dict[str, Any] | None = None

    @property
    def n_points(self) -> int:
        """Number of finite points in the record."""
        return len(self.points)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dict."""
        return asdict(self)


def points_to_strings(
    points: Sequence[tuple[Rational, Rational]],
) -> list[tuple[str, str]]:
    """Serialize exact rational points."""
    return [(str(x), str(y)) for x, y in points]


def parse_rational_points(text: str) -> list[tuple[Rational, Rational]]:
    """Parse one rational coordinate pair per line."""
    points: list[tuple[Rational, Rational]] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 2:
            raise ValueError(f"Line {line_number}: expected 'x, y'")
        try:
            point = (Rational(parts[0]), Rational(parts[1]))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Line {line_number}: invalid rational coordinate"
            ) from exc
        points.append(point)
    ensure_distinct(points)
    return points


def ensure_distinct(points: Sequence[tuple[Rational, Rational]]) -> None:
    """Reject duplicate finite points."""
    seen = set()
    for index, point in enumerate(points):
        if point in seen:
            raise ValueError(f"Duplicate point at index {index}: {point}")
        seen.add(point)


def validate_points(
    configuration: str,
    points: Sequence[tuple[Rational, Rational]],
    source: str,
    scientific_scope: str = FINITE_SCOPE,
    status: str = "LOCALLY_REPRODUCED_EXACT",
    claimed_edges: int | None = None,
    message: str = "",
) -> ValidationRecord:
    """Validate exact unit-distance edges for rational points."""
    ensure_distinct(points)
    exact_edges, edges = count_unit_edges_exact(points)
    if claimed_edges is not None and claimed_edges != exact_edges:
        status = AI_REJECTED
        message = (
            f"AI claimed {claimed_edges} unit-distance edges. "
            f"Exact validator found {exact_edges}. "
            "Candidate rejected as stated."
        )
    return ValidationRecord(
        source=source,
        configuration=configuration,
        points=points_to_strings(points),
        edges=edges,
        status=status,
        scientific_scope=scientific_scope,
        claimed_edges=claimed_edges,
        exact_edges=exact_edges,
        message=message,
        raw=None,
    )


def line_record(n: int) -> ValidationRecord:
    """Build and validate a line baseline."""
    points = [(Rational(i), Rational(0)) for i in range(n)]
    return validate_points("Line Configuration", points, "baseline")


def grid_record(k: int) -> ValidationRecord:
    """Build and validate a square grid baseline."""
    points = [
        (Rational(i), Rational(j))
        for i in range(k)
        for j in range(k)
    ]
    return validate_points("Square Grid Configuration", points, "baseline")


def rational_345_record() -> ValidationRecord:
    """Build a non-axis-aligned rational unit-distance example."""
    points = [
        (Rational(0), Rational(0)),
        (Rational(3, 5), Rational(4, 5)),
        (Rational(1), Rational(0)),
    ]
    return validate_points(
        "Rational 3/5-4/5 Example",
        points,
        "baseline",
    )


def rational_mesh_record(m: int) -> ValidationRecord:
    """Build and validate the finite rational mesh baseline."""
    return validate_points(
        "Finite Rational Mesh Baseline",
        rational_mesh_points(m),
        "baseline",
        scientific_scope=RATIONAL_MESH_SCOPE,
        status="LOCALLY_REPRODUCED_EXACT",
    )


def baseline_records(line_n: int, grid_k: int, mesh_m: int) -> list[dict]:
    """Return UI table rows for all baseline types."""
    records = [
        line_record(line_n),
        grid_record(grid_k),
        rational_345_record(),
        rational_mesh_record(mesh_m),
    ]
    return [record.to_dict() for record in records]


def record_summary(record: dict[str, Any] | None) -> str:
    """Format a concise scientific summary."""
    if not record:
        return "No validated result available in this session."
    lines = [
        f"Configuration: {record['configuration']}",
        f"Number of points: {len(record['points'])}",
        "Exactly validated unit-distance edges: "
        f"{record['exact_edges']}",
        f"Validation status: {record['status']}",
        f"Scientific scope: {record['scientific_scope']}",
    ]
    if record.get("message"):
        lines.append(record["message"])
    return "\n".join(lines)


def explorer_preset(name: str) -> str:
    """Return preset coordinate text."""
    presets = {
        "Unit Square": "0, 0\n1, 0\n0, 1\n1, 1",
        "Rational 3/5-4/5 Example": "0, 0\n3/5, 4/5\n1, 0",
        "Small Rational Mesh": (
            "0, 0\n1/2, 0\n1, 0\n"
            "0, 1/2\n1/2, 1/2\n1, 1/2\n"
            "0, 1\n1/2, 1\n1, 1"
        ),
    }
    return presets.get(name, presets["Unit Square"])


def validate_explorer_text(text: str) -> tuple[dict | None, str, dict]:
    """Validate user-entered rational points."""
    try:
        points = parse_rational_points(text)
        record = validate_points(
            "Explorer Configuration",
            points,
            "explorer",
            scientific_scope=FINITE_SCOPE,
        )
        data = record.to_dict()
        return data, record_summary(data), data
    except ValueError as exc:
        error = {"status": "INVALID_INPUT", "error": str(exc)}
        return None, str(exc), error


def parse_candidate_json(raw_text: str) -> dict[str, Any]:
    """Parse strict JSON from a provider or pasted candidate."""
    data = json.loads(raw_text)
    if not isinstance(data, dict):
        raise ValueError("Candidate must be a JSON object")
    return data


def validate_ai_candidate_data(data: dict[str, Any]) -> ValidationRecord:
    """Validate an AI finite candidate schema and exact edge count."""
    forbidden_text = json.dumps(data, ensure_ascii=False).lower()
    forbidden = ["sawin", "asymptotic", "theorem", "proof", "n^1.014"]
    if any(term in forbidden_text for term in forbidden):
        raise ValueError("Candidate contains forbidden overclaim language")
    points_raw = data.get("points")
    if not isinstance(points_raw, list) or not 3 <= len(points_raw) <= 8:
        raise ValueError("AI candidate must contain 3-8 finite points")
    points = []
    for item in points_raw:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError("Each point must be a two-item list")
        points.append((Rational(str(item[0])), Rational(str(item[1]))))
    ensure_distinct(points)
    claimed = int(data.get("claimed_unit_distance_edges", -1))
    exact_count, _ = count_unit_edges_exact(points)
    status = AI_VALIDATED if claimed == exact_count else AI_REJECTED
    message = (
        "AI claim matched the exact finite validator."
        if status == AI_VALIDATED
        else (
            f"AI claimed {claimed} unit-distance edges. "
            f"Exact validator found {exact_count}. "
            "Candidate rejected as stated."
        )
    )
    record = validate_points(
        data.get("candidate_name", "AI Candidate"),
        points,
        "ai_candidate",
        scientific_scope=AI_SCOPE,
        status=status,
        claimed_edges=claimed,
        message=message,
    )
    record.raw = {"candidate_name": data.get("candidate_name", "")}
    return record


def validate_ai_candidate_json(raw_text: str) -> tuple[dict | None, str, dict]:
    """Parse and validate strict AI candidate JSON."""
    try:
        record = validate_ai_candidate_data(parse_candidate_json(raw_text))
        data = record.to_dict()
        return data, record_summary(data), data
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        error = {"status": AI_REJECTED, "error": str(exc)}
        return None, str(exc), error


def candidate_prompt() -> str:
    """Return the strict finite candidate prompt for providers."""
    return (
        "Return strict JSON only with keys candidate_name, points, "
        "claimed_unit_distance_edges, scope. Use 3-8 distinct rational "
        "points as strings. Scope must be finite candidate hypothesis only. "
        "Do not mention Sawin, asymptotic claims, theorem, or proof."
    )


def test_provider_connection(provider: Any) -> dict[str, str]:
    """Run an explicit provider connection test."""
    if provider is None or not provider.is_available():
        return {"status": "NOT_CONFIGURED", "message": "No request sent."}
    request = GenerationRequest(
        prompt="Return exactly the string: PROVIDER_LIVE_TEST_OK",
        model="default",
        max_tokens=16,
    )
    try:
        response = provider.generate(request)
    except NotImplementedError:
        return {
            "status": "LIVE_ADAPTER_NOT_IMPLEMENTED",
            "message": "Provider is configured, but live adapter is pending.",
        }
    except Exception as exc:
        return {"status": "ERROR", "message": type(exc).__name__}
    ok = response.raw_text.strip() == "PROVIDER_LIVE_TEST_OK"
    message = (
        "Provider returned expected string."
        if ok
        else "Unexpected response."
    )
    return {
        "status": "PASS" if ok else "FAIL",
        "message": message,
    }


def generate_and_validate(provider: Any) -> tuple[dict | None, str, dict]:
    """Generate one finite candidate and validate it exactly."""
    if provider is None or not provider.is_available():
        error = {"status": "NOT_CONFIGURED", "message": "No request sent."}
        return None, "NOT_CONFIGURED: no live provider is configured.", error
    request = GenerationRequest(
        prompt=candidate_prompt(),
        model="default",
        temperature=0.0,
        max_tokens=1200,
    )
    try:
        response = provider.generate(request)
    except NotImplementedError:
        error = {
            "status": "LIVE_ADAPTER_NOT_IMPLEMENTED",
            "message": "Provider is configured, but live adapter is pending.",
        }
        return None, error["message"], error
    except Exception as exc:
        error = {"status": "ERROR", "message": type(exc).__name__}
        return None, error["message"], error
    return validate_ai_candidate_json(response.raw_text)


def build_finite_report(record: dict[str, Any] | None) -> tuple[str, dict]:
    """Build a sanitized finite validation report."""
    if not record:
        return "No validated result available.", {"available": False}
    now = datetime.now(timezone.utc).isoformat()
    ai_extra = ""
    if record.get("source") == "ai_candidate":
        ai_extra = (
            "\nAI-generated candidate independently checked by the finite "
            "exact validator. Validation applies only to this finite point "
            "configuration.\n"
        )
    report = (
        "# Counterexample Commons Finite Validation Report\n\n"
        f"Timestamp: {now}\n\n"
        f"Configuration: {record['configuration']}\n"
        f"Points: {record['points']}\n"
        "Exactly validated unit-distance edge count: "
        f"{record['exact_edges']}\n"
        f"Validation status: {record['status']}\n"
        f"Scientific scope: {record['scientific_scope']}\n"
        f"{ai_extra}\n"
        "Finite exact validation export only; not an asymptotic theorem, "
        "not a Sawin reproduction, and not a formal proof of a new bound.\n"
        f"\n{provenance_report_section()}"
    )
    safe_report = sanitize_for_export(report)
    payload = {"available": True, "record": record, "report": safe_report}
    return safe_report, payload


def write_report_files(
    record: dict[str, Any] | None,
    directory: Path | None = None,
) -> tuple[str | None, str | None, str, dict]:
    """Write sanitized Markdown and JSON report artifacts."""
    report, payload = build_finite_report(record)
    if not payload.get("available"):
        return None, None, report, payload
    out_dir = directory or Path(tempfile.mkdtemp(prefix="cc_report_"))
    out_dir.mkdir(parents=True, exist_ok=True)
    name = re.sub(
        r"[^a-z0-9]+",
        "_",
        record["configuration"].lower(),
    ).strip("_")
    md_path = out_dir / f"{name}_finite_validation_report.md"
    json_path = out_dir / f"{name}_finite_validation_report.json"
    md_path.write_text(report, encoding="utf-8")
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return str(md_path), str(json_path), report, payload
