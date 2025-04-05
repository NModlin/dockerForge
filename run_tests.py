#!/usr/bin/env python3
"""
Script to run the chat API tests.
"""
import os
import sys
import subprocess
import time
import signal
import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main():
    """Run the tests."""
    # Start the FastAPI server in a separate process
    server_process = subprocess.Popen(
        ["python", "run_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    
    try:
        # Wait for the server to start
        print("Waiting for server to start...")
        time.sleep(5)
        
        # Run the tests
        print("Running tests...")
        pytest.main(["-v", "examples/test_chat_phase3.py"])
    finally:
        # Stop the server
        print("Stopping server...")
        server_process.send_signal(signal.SIGTERM)
        server_process.wait()
        
        # Print server output
        stdout, stderr = server_process.communicate()
        if stdout:
            print("Server stdout:")
            print(stdout)
        if stderr:
            print("Server stderr:")
            print(stderr)

if __name__ == "__main__":
    main()
