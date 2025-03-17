"""
DockerForge AI provider plugin: OpenAI

This module provides an OpenAI provider for DockerForge.
"""

import json
import logging
from typing import Dict, Any, Optional, Callable

import openai
from openai import OpenAI
import tiktoken

from src.config.config_manager import get_config
from src.core.ai_provider import AIProvider, AIProviderError


class OpenAIProvider(AIProvider):
    """OpenAI provider for DockerForge."""
    
    def __init__(self):
        """Initialize the OpenAI provider."""
        self.api_key = get_config("ai.providers.openai.api_key")
        self.model = get_config("ai.providers.openai.model", "gpt-4o")
        self.max_tokens = get_config("ai.providers.openai.max_tokens", 4000)
        self.temperature = get_config("ai.providers.openai.temperature", 0.7)
        
        # Initialize client
        self.client = OpenAI(api_key=self.api_key)
        
        # Initialize usage tracking
        self.usage_tracker = self._init_usage_tracker()
    
    def _init_usage_tracker(self):
        """Initialize the usage tracker."""
        try:
            from src.core.ai_usage_tracker import AIUsageTracker
            return AIUsageTracker()
        except ImportError:
            return None
    
    def analyze(self, context: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        Analyze a query with context.
        
        Args:
            context: Context information
            query: Query to analyze
            
        Returns:
            Dict[str, Any]: Analysis result
        """
        if not self.api_key:
            raise AIProviderError("OpenAI API key not configured")
        
        # Prepare system prompt
        system_prompt = """
        You are DockerForge AI, an expert in Docker troubleshooting and analysis.
        Analyze the provided Docker logs, configuration, or issue description.
        Identify problems, their root causes, and suggest specific fixes.
        Be concise, technical, and actionable in your responses.
        """
        
        # Prepare user message with context
        user_message = f"Context:\n{json.dumps(context, indent=2)}\n\nQuery: {query}"
        
        try:
            # Create completion
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            
            # Extract response
            analysis = response.choices[0].message.content
            
            return {
                "provider": "openai",
                "model": self.model,
                "analysis": analysis,
                "raw_response": response.model_dump(),
            }
        except Exception as e:
            raise AIProviderError(f"OpenAI API request failed: {str(e)}")
    
    def generate_fix(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a fix for an issue.
        
        Args:
            issue: Issue information
            
        Returns:
            Dict[str, Any]: Fix information
        """
        if not self.api_key:
            raise AIProviderError("OpenAI API key not configured")
        
        # Prepare system prompt
        system_prompt = """
        You are DockerForge AI, an expert in Docker troubleshooting and fixes.
        Generate specific, actionable fixes for the provided Docker issue.
        Include commands to run, configuration changes to make, or other steps to resolve the issue.
        Be concise, technical, and ensure your fixes are safe to apply.
        """
        
        # Prepare user message with issue
        user_message = f"Issue:\n{json.dumps(issue, indent=2)}\n\nGenerate a fix for this issue."
        
        try:
            # Create completion
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            
            # Extract response
            fix = response.choices[0].message.content
            
            return {
                "provider": "openai",
                "model": self.model,
                "fix": fix,
                "raw_response": response.model_dump(),
            }
        except Exception as e:
            raise AIProviderError(f"OpenAI API request failed: {str(e)}")
    
    def validate_credentials(self) -> bool:
        """
        Validate provider credentials.
        
        Returns:
            bool: True if credentials are valid
        """
        if not self.api_key:
            return False
        
        try:
            # List models to validate API key
            self.client.models.list()
            return True
        except Exception:
            return False
    
    def estimate_cost(self, input_text: str, expected_output_length: int = 500) -> Dict[str, Any]:
        """
        Estimate the cost of an API call.
        
        Args:
            input_text: Input text for the API call
            expected_output_length: Expected length of the output in tokens
            
        Returns:
            Dict[str, Any]: Cost estimation information
        """
        # OpenAI pricing (as of 2025)
        model_pricing = {
            "gpt-4o": {
                "input_per_1m_tokens": 5.00,
                "output_per_1m_tokens": 15.00,
            },
            "gpt-4-turbo": {
                "input_per_1m_tokens": 10.00,
                "output_per_1m_tokens": 30.00,
            },
            "gpt-3.5-turbo": {
                "input_per_1m_tokens": 0.50,
                "output_per_1m_tokens": 1.50,
            },
        }
        
        # Get pricing for selected model
        pricing = model_pricing.get(self.model, model_pricing["gpt-4o"])
        
        # Count tokens
        input_tokens = self.get_token_count(input_text)
        
        # Calculate costs
        input_cost = (input_tokens / 1_000_000) * pricing["input_per_1m_tokens"]
        output_cost = (expected_output_length / 1_000_000) * pricing["output_per_1m_tokens"]
        total_cost = input_cost + output_cost
        
        return {
            "provider": "openai",
            "model": self.model,
            "input_tokens": input_tokens,
            "output_tokens": expected_output_length,
            "input_cost_usd": input_cost,
            "output_cost_usd": output_cost,
            "estimated_cost_usd": total_cost,
            "pricing_info": pricing,
        }
    
    def get_token_count(self, text: str) -> int:
        """
        Get token count using OpenAI's tokenizer.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            int: Token count
        """
        try:
            # Get encoding for model
            if self.model.startswith("gpt-4"):
                encoding = tiktoken.encoding_for_model("gpt-4")
            elif self.model.startswith("gpt-3.5"):
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            else:
                encoding = tiktoken.encoding_for_model("gpt-4")
            
            # Count tokens
            return len(encoding.encode(text))
        except Exception:
            # Fall back to approximate method
            return super().get_token_count(text)
    
    def report_capabilities(self) -> Dict[str, Any]:
        """
        Report provider capabilities.
        
        Returns:
            Dict[str, Any]: Provider capabilities
        """
        return {
            "streaming": True,
            "vision": True,
            "batching": False,
            "function_calling": True,
            "token_counting": True,
        }
    
    def streaming_analyze(self, context: Dict[str, Any], query: str, callback: Callable[[str], None]) -> Dict[str, Any]:
        """
        Analyze a query with context using streaming response.
        
        Args:
            context: Context information
            query: Query to analyze
            callback: Callback function to handle streaming chunks
            
        Returns:
            Dict[str, Any]: Complete analysis result
        """
        if not self.api_key:
            raise AIProviderError("OpenAI API key not configured")
        
        # Prepare system prompt
        system_prompt = """
        You are DockerForge AI, an expert in Docker troubleshooting and analysis.
        Analyze the provided Docker logs, configuration, or issue description.
        Identify problems, their root causes, and suggest specific fixes.
        Be concise, technical, and actionable in your responses.
        """
        
        # Prepare user message with context
        user_message = f"Context:\n{json.dumps(context, indent=2)}\n\nQuery: {query}"
        
        try:
            # Create streaming completion
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True,
            )
            
            # Process streaming response
            full_text = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_text += content
                    if callback and callable(callback):
                        callback(content)
            
            return {
                "provider": "openai",
                "model": self.model,
                "analysis": full_text,
            }
        except Exception as e:
            raise AIProviderError(f"OpenAI API streaming request failed: {str(e)}")
