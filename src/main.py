#!/usr/bin/env python3
"""
FedMCP Server Entry Point
"""

import uvicorn
from fedmcp_server import app

if __name__ == "__main__":
    uvicorn.run(
        "fedmcp_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
