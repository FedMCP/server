import json, uuid, datetime
from typing import Literal

AuditAction = Literal["create", "update", "deploy", "delete"]

def emit_event(artifact_id: str, action: AuditAction, actor: str) -> None:
    evt = {
        "eventId": str(uuid.uuid4()),
        "artifactId": artifact_id,
        "action": action,
        "actor": actor,
        "timestamp": datetime.datetime.utcnow()
        .replace(tzinfo=datetime.timezone.utc)
        .isoformat(),
    }
    print(json.dumps(evt))
    # TODO: push to S3/SQS/Postgres later