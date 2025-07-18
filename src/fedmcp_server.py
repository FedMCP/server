"""
FedMCP Reference Server Implementation

Provides artifact storage, signing, verification, and audit capabilities
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from uuid import UUID
import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import boto3

# Import our FedMCP core library
import sys
sys.path.append(str(Path(__file__).parent.parent))
from fedmcp import (
    Artifact, ArtifactType, 
    LocalSigner, Verifier,
    AuditEvent, AuditAction
)


# --------------------------------------------------------------------------- #
#  Configuration
# --------------------------------------------------------------------------- #

# Storage configuration
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "local")  # local or s3
LOCAL_STORAGE_PATH = os.getenv("LOCAL_STORAGE_PATH", "/tmp/fedmcp")
S3_BUCKET = os.getenv("FEDMCP_ARTIFACT_BUCKET")

# Signing configuration  
SIGNING_TYPE = os.getenv("SIGNING_TYPE", "local")  # local or kms
KMS_KEY_ID = os.getenv("KMS_KEY_ID")

# Audit configuration
AUDIT_LOG_GROUP = os.getenv("AUDIT_LOG_GROUP")
AUDIT_LOG_STREAM = os.getenv("AUDIT_LOG_STREAM", "primary")

# --------------------------------------------------------------------------- #
#  FastAPI app
# --------------------------------------------------------------------------- #

app = FastAPI(
    title="FedMCP Reference Server",
    version="0.2.0",
    description="Federal Model Context Protocol reference implementation"
)

security = HTTPBearer()

# --------------------------------------------------------------------------- #
#  Models
# --------------------------------------------------------------------------- #

class CreateArtifactRequest(BaseModel):
    artifact: Dict[str, Any]
    sign: bool = True

class JWSResponse(BaseModel):
    jws: str
    artifact_id: str
    workspace_id: str

class VerifyRequest(BaseModel):
    jws: str

class VerifyResponse(BaseModel):
    valid: bool
    artifact: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# --------------------------------------------------------------------------- #
#  Storage backend
# --------------------------------------------------------------------------- #

class StorageBackend:
    """Abstract storage backend"""
    
    async def store_artifact(self, artifact_id: str, data: Dict[str, Any]) -> None:
        raise NotImplementedError
        
    async def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError
        
    async def list_artifacts(self, workspace_id: Optional[str] = None) -> List[str]:
        raise NotImplementedError


class LocalStorage(StorageBackend):
    """Local filesystem storage"""
    
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        
    async def store_artifact(self, artifact_id: str, data: Dict[str, Any]) -> None:
        file_path = self.path / f"{artifact_id}.json"
        with open(file_path, 'w') as f:
            json.dump(data, f)
            
    async def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        file_path = self.path / f"{artifact_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, 'r') as f:
            return json.load(f)
            
    async def list_artifacts(self, workspace_id: Optional[str] = None) -> List[str]:
        artifacts = []
        for file_path in self.path.glob("*.json"):
            if workspace_id:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if data.get("artifact", {}).get("workspaceId") == workspace_id:
                        artifacts.append(file_path.stem)
            else:
                artifacts.append(file_path.stem)
        return artifacts


class S3Storage(StorageBackend):
    """AWS S3 storage"""
    
    def __init__(self, bucket: str):
        self.bucket = bucket
        self.s3 = boto3.client('s3')
        
    async def store_artifact(self, artifact_id: str, data: Dict[str, Any]) -> None:
        self.s3.put_object(
            Bucket=self.bucket,
            Key=f"artifacts/{artifact_id}.json",
            Body=json.dumps(data),
            ContentType='application/json'
        )
        
    async def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.s3.get_object(
                Bucket=self.bucket,
                Key=f"artifacts/{artifact_id}.json"
            )
            return json.loads(response['Body'].read())
        except self.s3.exceptions.NoSuchKey:
            return None
            
    async def list_artifacts(self, workspace_id: Optional[str] = None) -> List[str]:
        # For workspace filtering, would need to store metadata or scan objects
        response = self.s3.list_objects_v2(
            Bucket=self.bucket,
            Prefix="artifacts/"
        )
        artifacts = []
        for obj in response.get('Contents', []):
            artifact_id = obj['Key'].split('/')[-1].replace('.json', '')
            artifacts.append(artifact_id)
        return artifacts

# --------------------------------------------------------------------------- #
#  Initialize components
# --------------------------------------------------------------------------- #

# Storage
if STORAGE_TYPE == "s3" and S3_BUCKET:
    storage = S3Storage(S3_BUCKET)
else:
    storage = LocalStorage(LOCAL_STORAGE_PATH)

# Signer
if SIGNING_TYPE == "kms" and KMS_KEY_ID:
    from fedmcp import KMSSigner
    signer = KMSSigner(KMS_KEY_ID)
else:
    # Create or load local signer
    signer = LocalSigner()

# Verifier
verifier = Verifier()
verifier.add_public_key(signer.get_key_id(), signer.private_key.public_key())

# Audit logger
audit_logs = []  # In-memory for demo, use CloudWatch in production

# --------------------------------------------------------------------------- #
#  Helper functions
# --------------------------------------------------------------------------- #

def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user from auth token (simplified for demo)"""
    return f"user:{auth.credentials[:8]}"

async def log_audit_event(
    action: AuditAction,
    actor: str,
    artifact_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """Log an audit event"""
    event = AuditEvent(
        action=action,
        actor=actor,
        artifactId=UUID(artifact_id) if artifact_id else None,
        workspaceId=UUID(workspace_id) if workspace_id else UUID("00000000-0000-0000-0000-000000000000"),
        metadata=metadata or {}
    )
    
    audit_logs.append(event.model_dump(by_alias=True))
    
    # Optionally send to CloudWatch
    if AUDIT_LOG_GROUP:
        # Implementation would go here
        pass

# --------------------------------------------------------------------------- #
#  API Endpoints
# --------------------------------------------------------------------------- #

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.2.0"}


@app.post("/artifacts", response_model=JWSResponse)
async def create_artifact(
    request: CreateArtifactRequest,
    current_user: str = Depends(get_current_user)
):
    """Create and optionally sign a new artifact"""
    try:
        # Create artifact from request
        artifact = Artifact(**request.artifact)
        
        # Validate
        artifact.validate()
        
        # Sign if requested
        if request.sign:
            jws_token = signer.sign(artifact)
            
            # Store the signed artifact
            await storage.store_artifact(
                str(artifact.id),
                {
                    "artifact": artifact.model_dump(by_alias=True),
                    "jws": jws_token
                }
            )
        else:
            # Store unsigned artifact
            await storage.store_artifact(
                str(artifact.id),
                {"artifact": artifact.model_dump(by_alias=True)}
            )
            jws_token = None
        
        # Audit
        await log_audit_event(
            action=AuditAction.CREATE,
            actor=current_user,
            artifact_id=str(artifact.id),
            workspace_id=str(artifact.workspaceId)
        )
        
        return JWSResponse(
            jws=jws_token or "",
            artifact_id=str(artifact.id),
            workspace_id=str(artifact.workspaceId)
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/artifacts/{artifact_id}")
async def get_artifact(
    artifact_id: str,
    current_user: str = Depends(get_current_user)
):
    """Retrieve an artifact by ID"""
    data = await storage.get_artifact(artifact_id)
    
    if not data:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    # Audit
    await log_audit_event(
        action=AuditAction.READ,
        actor=current_user,
        artifact_id=artifact_id,
        workspace_id=data["artifact"].get("workspaceId")
    )
    
    return data


@app.post("/artifacts/verify", response_model=VerifyResponse)
async def verify_artifact(
    request: VerifyRequest,
    current_user: str = Depends(get_current_user)
):
    """Verify a JWS-signed artifact"""
    try:
        # Verify the JWS
        artifact = verifier.verify(request.jws)
        
        # Audit
        await log_audit_event(
            action=AuditAction.VERIFY,
            actor=current_user,
            artifact_id=str(artifact.id),
            workspace_id=str(artifact.workspaceId)
        )
        
        return VerifyResponse(
            valid=True,
            artifact=artifact.model_dump(by_alias=True)
        )
        
    except Exception as e:
        return VerifyResponse(
            valid=False,
            error=str(e)
        )


@app.get("/artifacts")
async def list_artifacts(
    workspace_id: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """List artifacts, optionally filtered by workspace"""
    artifact_ids = await storage.list_artifacts(workspace_id)
    
    return {
        "artifacts": artifact_ids,
        "count": len(artifact_ids)
    }


@app.get("/audit/events")
async def get_audit_events(
    artifact_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    limit: int = 100
):
    """Query audit events"""
    events = audit_logs[-limit:]
    
    # Filter if requested
    if artifact_id:
        events = [e for e in events if e.get("artifactId") == artifact_id]
    if workspace_id:
        events = [e for e in events if e.get("workspaceId") == workspace_id]
    
    return {"events": events}


@app.get("/jwks")
async def get_jwks():
    """Get public keys for verification"""
    return {
        "keys": [signer.get_public_key_jwk()]
    }


# --------------------------------------------------------------------------- #
#  Run server
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)