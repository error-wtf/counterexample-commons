"""Experiment run manager — creates and manages experiment directories."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class ExperimentStatus(Enum):
    PASS_FINITE_CONFIGURATION_VALIDATED = (
        "PASS_FINITE_CONFIGURATION_VALIDATED"
    )
    FAIL_CLAIMED_COUNT_INCORRECT = "FAIL_CLAIMED_COUNT_INCORRECT"
    FAIL_INVALID_COORDINATES = "FAIL_INVALID_COORDINATES"
    INCONCLUSIVE_EXTRACTION_FAILED = "INCONCLUSIVE_EXTRACTION_FAILED"
    INCONCLUSIVE_PROVIDER_ERROR = "INCONCLUSIVE_PROVIDER_ERROR"


class RunManager:
    """Manages experiment run directories and artifacts."""

    def __init__(self, runs_dir: str | Path) -> None:
        self._runs_dir = Path(runs_dir)

    def create_run(
        self,
        provider: str,
        model: str,
        research_question: str,
    ) -> RunDirectory:
        """Create a new timestamped run directory."""
        now = datetime.now(timezone.utc)
        run_id = (
            f"{now.strftime('%Y-%m-%d')}_{uuid.uuid4().hex[:8]}"
        )
        run_dir = self._runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "run_id": run_id,
            "provider": provider,
            "model": model,
            "created_utc": now.isoformat(),
            "status": "CREATED",
        }
        (run_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2), encoding="utf-8"
        )
        (run_dir / "research_question.md").write_text(
            research_question, encoding="utf-8"
        )
        return RunDirectory(run_dir, metadata)

    def list_runs(self) -> list[str]:
        """List all run directory names."""
        if not self._runs_dir.exists():
            return []
        return sorted(
            d.name for d in self._runs_dir.iterdir() if d.is_dir()
        )


class RunDirectory:
    """Wrapper around a single experiment run directory."""

    def __init__(
        self, path: Path, metadata: dict[str, Any]
    ) -> None:
        self.path = path
        self.metadata = metadata

    @property
    def run_id(self) -> str:
        return self.metadata["run_id"]

    def save_preregistration(self, claim: str, falsifier: str) -> None:
        (self.path / "preregistered_claim.md").write_text(
            claim, encoding="utf-8"
        )
        (self.path / "falsifier.md").write_text(
            falsifier, encoding="utf-8"
        )

    def save_prompt(self, prompt: str) -> None:
        (self.path / "prompt.md").write_text(
            prompt, encoding="utf-8"
        )

    def save_raw_output(self, raw_text: str) -> None:
        (self.path / "raw_model_output.md").write_text(
            raw_text, encoding="utf-8"
        )

    def save_candidate(self, candidate: dict) -> None:
        (self.path / "extracted_candidate.json").write_text(
            json.dumps(candidate, indent=2), encoding="utf-8"
        )

    def save_validation(
        self,
        stdout: str,
        stderr: str,
        command: str,
    ) -> None:
        (self.path / "validation_command.txt").write_text(
            command, encoding="utf-8"
        )
        (self.path / "validation_stdout.txt").write_text(
            stdout, encoding="utf-8"
        )
        (self.path / "validation_stderr.txt").write_text(
            stderr, encoding="utf-8"
        )

    def save_result(self, status: ExperimentStatus, details: dict) -> None:
        result = {
            "status": status.value,
            **details,
        }
        (self.path / "result.json").write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )
        self.metadata["status"] = status.value
        (self.path / "metadata.json").write_text(
            json.dumps(self.metadata, indent=2), encoding="utf-8"
        )

    def save_assessment(self, text: str) -> None:
        (self.path / "assessment.md").write_text(
            text, encoding="utf-8"
        )
