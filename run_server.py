#!/usr/bin/env python3
"""
Script to start the FastAPI server for testing.
"""
import os
import sys
import uvicorn

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    # Start the FastAPI server
    port = int(os.getenv("PORT", 54321))
    uvicorn.run("src.web.api.main:app", host="0.0.0.0", port=port, reload=True)
