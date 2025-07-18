# FedMCP Server

Reference FastAPI server implementation for FedMCP (Federal Model Context Protocol).

## Overview

The FedMCP server provides:
- RESTful API for artifact management
- Cryptographic signature verification
- Audit trail logging
- PII detection and redaction
- Multi-tenant workspace support
- S3 and local storage backends

## Quick Start

### Using Docker

```bash
docker run -p 8090:8090 fedmcp/server:latest
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python -m src.main

# Server starts at http://localhost:8090
```

## API Endpoints

### Artifact Management

- `POST /artifacts` - Create and sign artifact
- `GET /artifacts/{id}` - Retrieve artifact
- `GET /artifacts` - List artifacts
- `POST /artifacts/{id}/verify` - Verify signature
- `DELETE /artifacts/{id}` - Delete artifact

### Audit Trail

- `GET /audit/events` - Query audit events
- `GET /audit/events/{artifact_id}` - Get artifact history

### Key Management

- `GET /jwks/{workspace_id}` - Get public keys

## Configuration

Environment variables:

```bash
# Storage backend (local or s3)
STORAGE_BACKEND=local
STORAGE_PATH=/var/fedmcp/artifacts

# S3 configuration
S3_BUCKET=fedmcp-artifacts
AWS_REGION=us-gov-west-1

# Audit logging
AUDIT_LOG_GROUP=FedMCP-Audit
AUDIT_LOG_STREAM=primary

# Server settings
PORT=8090
HOST=0.0.0.0
WORKERS=4
```

## Features

### PII Detection

The server automatically scans artifacts for PII using Presidio:
- Social Security Numbers
- Credit card numbers
- Email addresses
- Phone numbers
- Medical record numbers

### Audit Logging

All operations are logged with:
- Actor identification
- Timestamp
- Operation type
- Artifact metadata
- Signature details

### Multi-Workspace Support

Isolate artifacts by workspace:
```bash
# Create artifact in workspace
POST /artifacts
{
  "workspace_id": "prod-team",
  "type": "ssp-fragment",
  ...
}
```

## API Examples

### Create Artifact

```bash
curl -X POST http://localhost:8090/artifacts \
  -H "Content-Type: application/json" \
  -d '{
    "type": "ssp-fragment",
    "name": "ML Pipeline Controls",
    "content": {
      "controls": ["AC-2", "AU-3"]
    },
    "workspace_id": "ml-team"
  }'
```

### Verify Signature

```bash
curl -X POST http://localhost:8090/artifacts/{id}/verify
```

### Query Audit Trail

```bash
curl "http://localhost:8090/audit/events?artifact_id={id}"
```

## Development

### Running Tests

```bash
pytest tests/
```

### Building Docker Image

```bash
docker build -t fedmcp/server .
```

### OpenAPI Documentation

Visit http://localhost:8090/docs for interactive API documentation.

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.
