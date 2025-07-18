
"""Light‑weight FastAPI reference server for FedMCP demo."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from functools import lru_cache

import boto3
from fastapi import FastAPI, Request, Response
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import SpacyNlpEngine

# --------------------------------------------------------------------------- #
#  FastAPI app
# --------------------------------------------------------------------------- #

app = FastAPI(title="FedMCP reference server")

# --------------------------------------------------------------------------- #
#  Presidio analyzer — cached to avoid model reload on every request
# --------------------------------------------------------------------------- #


@lru_cache
def get_analyzer() -> AnalyzerEngine:
    """Return a cached Presidio AnalyzerEngine with a small English model."""
    nlp_engine = SpacyNlpEngine()
    nlp_engine.load({"en": "en_core_web_sm"})
    return AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])


# --------------------------------------------------------------------------- #
#  Optional CloudWatch audit sink
# --------------------------------------------------------------------------- #

LOG_GROUP = os.getenv("AUDIT_LOG_GROUP")
LOG_STREAM = os.getenv("AUDIT_LOG_STREAM", "primary")
_logs = boto3.client("logs") if LOG_GROUP else None


def _emit_audit(record: dict) -> None:
    """Send a single audit record to CloudWatch (if configured)."""
    if not _logs:
        return
    _logs.put_log_events(
        logGroupName=LOG_GROUP,
        logStreamName=LOG_STREAM,
        logEvents=[
            {
                "timestamp": int(datetime.utcnow().timestamp() * 1000),
                "message": json.dumps(record),
            }
        ],
    )


# --------------------------------------------------------------------------- #
#  Middleware – hashes body + optional PII scan & audit
# --------------------------------------------------------------------------- #


@app.middleware("http")
async def audit_middleware(request: Request, call_next):  # type: ignore[return-value]
    raw_body = await request.body()
    sha256 = hashlib.sha256(raw_body).hexdigest()

    try:
        contains_pii = bool(
            get_analyzer().analyze(raw_body.decode("utf-8", "ignore"), language="en")
        )
    except Exception:
        contains_pii = False

    _emit_audit(
        {
            "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "path": request.url.path,
            "method": request.method,
            "pii": contains_pii,
            "sha256": sha256,
        }
    )

    response: Response = await call_next(request)
    response.headers["X-Content-SHA256"] = sha256
    return response


# --------------------------------------------------------------------------- #
#  Simple health endpoint
# --------------------------------------------------------------------------- #


@app.get("/health", tags=["internal"])
def health() -> dict[str, str]:
    """Basic liveness probe."""
    return {"status": "ok"}
