#!/usr/bin/env python3
"""
Test script for verifying the Gemini API implementation in DockerForge.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Load environment variables from .env file
load_dotenv()

from src.config.config_manager import get_config, set_config
from src.core.ai_provider import GeminiProvider, AIProviderError

def test_api_key_validation():
    """Test API key validation."""
    print("\n=== Testing API Key Validation ===")

    # Test with invalid API key
    set_config("ai.providers.gemini.api_key", "invalid_key")
    provider = GeminiProvider()

    valid = provider.validate_credentials()
    print(f"Credentials valid with invalid key: {valid}")

    # Test with environment variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        set_config("ai.providers.gemini.api_key", api_key)
        provider = GeminiProvider()
        valid = provider.validate_credentials()
        print(f"Credentials valid with environment key: {valid}")
    else:
        print("GEMINI_API_KEY environment variable not set")

def test_text_generation():
    """Test text generation functionality."""
    print("\n=== Testing Text Generation ===")

    # Use environment variable for API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY environment variable not set")
        return

    set_config("ai.providers.gemini.api_key", api_key)
    provider = GeminiProvider()

    prompt = "Explain Docker volumes in one paragraph."
    print(f"Prompt: {prompt}")

    try:
        response = provider.generate_text(prompt)
        print(f"Response: {response}")
    except AIProviderError as e:
        print(f"Error: {e}")

def test_analyze_method():
    """Test analyze method implementation."""
    print("\n=== Testing Analyze Method ===")

    # Use environment variable for API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY environment variable not set")
        return

    set_config("ai.providers.gemini.api_key", api_key)
    provider = GeminiProvider()

    context = {
        "container_logs": [
            "2023-05-15 12:34:56 ERROR: Connection refused to database at postgres:5432",
            "2023-05-15 12:35:01 ERROR: Retrying connection in 5 seconds",
            "2023-05-15 12:35:06 ERROR: Connection refused to database at postgres:5432"
        ],
        "container_info": {
            "name": "web-app",
            "image": "my-web-app:latest",
            "status": "running",
            "networks": ["app-network"]
        }
    }

    query = "What might be causing the database connection errors?"

    try:
        result = provider.analyze(context, query)
        print(f"Analysis result:")
        print(json.dumps(result, indent=2))
    except AIProviderError as e:
        print(f"Error: {e}")

def test_error_handling():
    """Test error handling."""
    print("\n=== Testing Error Handling ===")

    # Create a mock provider with a deliberate error
    class MockErrorProvider(GeminiProvider):
        def analyze(self, context, query):
            raise AIProviderError("This is a test error")

    provider = MockErrorProvider()

    # Test the analyze method which should raise an error
    try:
        context = {"test": "data"}
        query = "This should fail"
        provider.analyze(context, query)
        print("Error: Expected an error but none was raised")
    except AIProviderError as e:
        print(f"Expected error correctly raised: {e}")

def main():
    """Main function."""
    print("=== Gemini API Implementation Verification ===")

    # Run tests
    test_api_key_validation()
    test_text_generation()
    test_analyze_method()
    test_error_handling()

if __name__ == "__main__":
    main()
