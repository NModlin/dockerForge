#!/usr/bin/env python3
"""
Script to list available Gemini models.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY environment variable not set")
    exit(1)

genai.configure(api_key=api_key)

# List available models
print("Available Gemini models:")
for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(f"- {model.name}")
        print(f"  Supported methods: {model.supported_generation_methods}")
