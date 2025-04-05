"""
AI provider module for DockerForge.

This module provides functionality to interact with AI providers
for troubleshooting and analysis.
"""

import os
import json
import logging
import requests
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Tuple, Callable

from src.config.config_manager import get_config
from src.utils.logging_manager import get_logger

logger = get_logger("ai_provider")


class AIProviderError(Exception):
    """Exception raised for AI provider errors."""
    pass


class AIProvider(ABC):
    """Abstract base class for AI providers with enhanced capabilities."""

    @abstractmethod
    def analyze(self, context: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        Analyze a query with context.

        Args:
            context: Context information
            query: Query to analyze

        Returns:
            Dict[str, Any]: Analysis result
        """
        pass

    @abstractmethod
    def generate_fix(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a fix for an issue.

        Args:
            issue: Issue information

        Returns:
            Dict[str, Any]: Fix information
        """
        pass

    @abstractmethod
    def validate_credentials(self) -> bool:
        """
        Validate provider credentials.

        Returns:
            bool: True if credentials are valid
        """
        pass

    @abstractmethod
    def estimate_cost(self, input_text: str, expected_output_length: int = 500) -> Dict[str, Any]:
        """
        Estimate the cost of an API call.

        Args:
            input_text: Input text for the API call
            expected_output_length: Expected length of the output in tokens

        Returns:
            Dict[str, Any]: Cost estimation information
        """
        pass

    def generate_text(self, prompt: str) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: The prompt text

        Returns:
            str: Generated text
        """
        # Default implementation uses analyze with empty context
        result = self.analyze({}, prompt)
        return result.get("analysis", "I'm sorry, I couldn't generate a response.")

    def report_capabilities(self) -> Dict[str, Any]:
        """
        Report provider capabilities.

        Returns:
            Dict[str, Any]: Provider capabilities
        """
        return {
            "streaming": False,
            "vision": False,
            "batching": False,
            "function_calling": False,
            "token_counting": False,
        }

    def get_token_count(self, text: str) -> int:
        """
        Get token count for text (approximate if not supported).

        Args:
            text: Text to count tokens for

        Returns:
            int: Approximate token count
        """
        # Fallback implementation using simple approximation
        # Average English words are ~1.3 tokens
        words = len(text.split())
        return int(words * 1.3)

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
        # Default implementation for providers that don't support streaming
        result = self.analyze(context, query)
        # Call callback with the complete result
        if callback and callable(callback):
            callback(result["analysis"])
        return result

    def confirm_cost(self, cost_info: Dict[str, Any]) -> bool:
        """
        Check if the estimated cost is within budget limits.

        Args:
            cost_info: Cost estimation information

        Returns:
            bool: True if the cost is acceptable, False otherwise
        """
        # Get budget thresholds from config
        require_confirmation = get_config("ai.cost_management.require_confirmation", True)
        confirmation_threshold = get_config("ai.cost_management.confirmation_threshold_usd", 0.5)
        daily_budget = get_config("ai.cost_management.max_daily_cost_usd", 10.0)

        # If confirmation is not required, just check against the budget limit
        if not require_confirmation:
            return cost_info["estimated_cost_usd"] <= daily_budget

        # Check if cost exceeds threshold
        if cost_info["estimated_cost_usd"] > confirmation_threshold:
            # Log a warning about the high cost
            logger.warning(
                f"Estimated cost ${cost_info['estimated_cost_usd']:.4f} exceeds "
                f"confirmation threshold ${confirmation_threshold:.2f}"
            )

            # In CLI mode, we would ask for confirmation here
            # For now, just check against the budget limit
            return cost_info["estimated_cost_usd"] <= daily_budget

        return True


class ClaudeProvider(AIProvider):
    """Claude AI provider."""

    def __init__(self):
        """Initialize the Claude provider."""
        self.api_key = get_config("ai.providers.claude.api_key")
        self.model = get_config("ai.providers.claude.model", "claude-3-opus")
        self.max_tokens = get_config("ai.providers.claude.max_tokens", 4000)
        self.temperature = get_config("ai.providers.claude.temperature", 0.7)
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        # Initialize usage tracking
        self.usage_tracker = self._init_usage_tracker()

    def _init_usage_tracker(self):
        """Initialize the usage tracker."""
        try:
            from src.core.ai_usage_tracker import AIUsageTracker
            return AIUsageTracker()
        except ImportError:
            logger.debug("AIUsageTracker not available, usage tracking disabled")
            return None

    def analyze(self, context: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Analyze a query with context using Claude."""
        if not self.api_key:
            raise AIProviderError("Claude API key not configured")

        # Prepare system prompt
        system_prompt = """
        You are DockerForge AI, an expert in Docker troubleshooting and analysis.
        Analyze the provided Docker logs, configuration, or issue description.
        Identify problems, their root causes, and suggest specific fixes.
        Be concise, technical, and actionable in your responses.
        """

        # Prepare user message with context
        user_message = f"Context:\n{json.dumps(context, indent=2)}\n\nQuery: {query}"

        # Prepare request payload
        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()

            return {
                "provider": "claude",
                "model": self.model,
                "analysis": result["content"][0]["text"],
                "raw_response": result,
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Claude API request failed: {str(e)}")
            raise AIProviderError(f"Claude API request failed: {str(e)}")

    def generate_fix(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fix for an issue using Claude."""
        if not self.api_key:
            raise AIProviderError("Claude API key not configured")

        # Prepare system prompt
        system_prompt = """
        You are DockerForge AI, an expert in Docker troubleshooting and fixes.
        Generate specific, actionable fixes for the provided Docker issue.
        Include commands to run, configuration changes to make, or other steps to resolve the issue.
        Be concise, technical, and ensure your fixes are safe to apply.
        """

        # Prepare user message with issue
        user_message = f"Issue:\n{json.dumps(issue, indent=2)}\n\nGenerate a fix for this issue."

        # Prepare request payload
        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()

            return {
                "provider": "claude",
                "model": self.model,
                "fix": result["content"][0]["text"],
                "raw_response": result,
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Claude API request failed: {str(e)}")
            raise AIProviderError(f"Claude API request failed: {str(e)}")

    def validate_credentials(self) -> bool:
        """Validate Claude API credentials."""
        if not self.api_key:
            return False

        try:
            # Simple request to validate API key
            response = requests.get(
                "https://api.anthropic.com/v1/models",
                headers=self.headers,
                timeout=10,
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def estimate_cost(self, input_text: str, expected_output_length: int = 500) -> Dict[str, Any]:
        """Estimate the cost of an API call to Claude."""
        # Claude pricing (as of 2025)
        model_pricing = {
            "claude-3-opus": {
                "input_per_1m_tokens": 15.00,
                "output_per_1m_tokens": 75.00,
            },
            "claude-3-sonnet": {
                "input_per_1m_tokens": 3.00,
                "output_per_1m_tokens": 15.00,
            },
            "claude-3-haiku": {
                "input_per_1m_tokens": 0.25,
                "output_per_1m_tokens": 1.25,
            }
        }

        # Get pricing for selected model
        pricing = model_pricing.get(self.model, model_pricing["claude-3-opus"])

        # Count tokens
        input_tokens = self.get_token_count(input_text)

        # Calculate costs
        input_cost = (input_tokens / 1_000_000) * pricing["input_per_1m_tokens"]
        output_cost = (expected_output_length / 1_000_000) * pricing["output_per_1m_tokens"]
        total_cost = input_cost + output_cost

        return {
            "provider": "claude",
            "model": self.model,
            "input_tokens": input_tokens,
            "output_tokens": expected_output_length,
            "input_cost_usd": input_cost,
            "output_cost_usd": output_cost,
            "estimated_cost_usd": total_cost,
            "pricing_info": pricing,
        }

    def get_token_count(self, text: str) -> int:
        """Get token count using Claude's tokenizer if available."""
        try:
            # Try to use tiktoken or anthropic's tokenizer if available
            import tiktoken
            enc = tiktoken.encoding_for_model("cl100k_base")  # Claude uses cl100k
            return len(enc.encode(text))
        except ImportError:
            # Fall back to the approximate method
            return super().get_token_count(text)

    def report_capabilities(self) -> Dict[str, Any]:
        """Report Claude provider capabilities."""
        return {
            "streaming": True,
            "vision": True,
            "batching": False,
            "function_calling": True,
            "token_counting": True,
        }

    def streaming_analyze(self, context: Dict[str, Any], query: str, callback: Callable[[str], None]) -> Dict[str, Any]:
        """Analyze a query with context using streaming response."""
        if not self.api_key:
            raise AIProviderError("Claude API key not configured")

        # Prepare system prompt
        system_prompt = """
        You are DockerForge AI, an expert in Docker troubleshooting and analysis.
        Analyze the provided Docker logs, configuration, or issue description.
        Identify problems, their root causes, and suggest specific fixes.
        Be concise, technical, and actionable in your responses.
        """

        # Prepare user message with context
        user_message = f"Context:\n{json.dumps(context, indent=2)}\n\nQuery: {query}"

        # Prepare request payload
        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": True,
        }

        try:
            # Use streaming response
            with requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60,
                stream=True,
            ) as response:
                response.raise_for_status()

                # Process streaming response
                full_text = ""
                for line in response.iter_lines():
                    if line:
                        # Parse the JSON data
                        try:
                            data = json.loads(line.decode("utf-8").lstrip("data: "))
                            if "content" in data and data["content"]:
                                chunk = data["content"][0]["text"]
                                full_text += chunk
                                if callback and callable(callback):
                                    callback(chunk)
                        except (json.JSONDecodeError, KeyError, IndexError) as e:
                            logger.debug(f"Error parsing streaming response: {str(e)}")

                return {
                    "provider": "claude",
                    "model": self.model,
                    "analysis": full_text,
                }
        except requests.exceptions.RequestException as e:
            logger.error(f"Claude API streaming request failed: {str(e)}")
            # Fall back to non-streaming request
            return self.analyze(context, query)


class GeminiProvider(AIProvider):
    """Gemini AI provider."""

    def __init__(self):
        """Initialize the Gemini provider."""
        self.api_key = get_config("ai.providers.gemini.api_key")
        self.model = get_config("ai.providers.gemini.model", "gemini-pro")
        self.max_tokens = get_config("ai.providers.gemini.max_tokens", 2048)
        self.temperature = get_config("ai.providers.gemini.temperature", 0.7)

        # Import here to avoid dependency issues
        try:
            import google.generativeai as genai
            self.genai = genai
            self.genai.configure(api_key=self.api_key)
            self.model_obj = self.genai.GenerativeModel(model_name=self.model)
            self.initialized = True
            logger.info(f"Successfully initialized Gemini provider with model {self.model}")
        except ImportError:
            logger.error("Failed to import google.generativeai. Please install it with 'pip install google-generativeai'")
            self.initialized = False
        except Exception as e:
            logger.error(f"Failed to initialize Gemini provider: {str(e)}")
            self.initialized = False

        # Initialize usage tracking
        self.usage_tracker = self._init_usage_tracker()

    def _init_usage_tracker(self):
        """Initialize the usage tracker."""
        try:
            from src.core.ai_usage_tracker import AIUsageTracker
            return AIUsageTracker()
        except ImportError:
            logger.debug("AIUsageTracker not available, usage tracking disabled")
            return None

    def generate_text(self, prompt: str) -> str:
        """
        Generate text using the Gemini API.

        Args:
            prompt: Prompt to generate text from

        Returns:
            str: Generated text
        """
        if not hasattr(self, 'initialized') or not self.initialized:
            return "Error: Gemini AI provider is not properly initialized. Please check your API key and network connection."

        try:
            generation_config = {
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
                "top_p": 0.95,
                "top_k": 40,
            }

            response = self.model_obj.generate_content(
                prompt,
                generation_config=generation_config
            )

            if response.text:
                return response.text.strip()
            else:
                return "No response generated. The content may have been filtered."

        except Exception as e:
            logger.error(f"Error generating text with Gemini: {str(e)}")
            return f"Error generating response: {str(e)}"

    def analyze(self, context: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Analyze a query with context using Gemini."""
        if not hasattr(self, 'initialized') or not self.initialized:
            raise AIProviderError("Gemini AI provider is not properly initialized")

        # Prepare system prompt
        system_prompt = """
        You are DockerForge AI, an expert in Docker troubleshooting and analysis.
        Analyze the provided Docker logs, configuration, or issue description.
        Identify problems, their root causes, and suggest specific fixes.
        Be concise, technical, and actionable in your responses.
        """

        # Prepare user message with context
        user_message = f"Context:\n{json.dumps(context, indent=2)}\n\nQuery: {query}"

        # Combine system prompt and user message
        prompt = f"{system_prompt}\n\n{user_message}"

        try:
            generation_config = {
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
                "top_p": 0.95,
                "top_k": 40,
            }

            response = self.model_obj.generate_content(
                prompt,
                generation_config=generation_config
            )

            if not response.text:
                raise AIProviderError("No response generated. The content may have been filtered.")

            analysis_text = response.text.strip()

            # Track usage if available
            if self.usage_tracker:
                self.usage_tracker.track_usage(
                    provider="gemini",
                    model=self.model,
                    input_tokens=self.get_token_count(prompt),
                    output_tokens=self.get_token_count(analysis_text),
                    request_type="analyze"
                )

            return {
                "provider": "gemini",
                "model": self.model,
                "analysis": analysis_text,
                "raw_response": {"text": analysis_text}
            }
        except Exception as e:
            logger.error(f"Gemini API request failed: {str(e)}")
            raise AIProviderError(f"Gemini API request failed: {str(e)}")

    def generate_fix(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fix for an issue using Gemini."""
        if not self.api_key:
            raise AIProviderError("Gemini API key not configured")

        # Prepare system prompt
        system_prompt = """
        You are DockerForge AI, an expert in Docker troubleshooting and fixes.
        Generate specific, actionable fixes for the provided Docker issue.
        Include commands to run, configuration changes to make, or other steps to resolve the issue.
        Be concise, technical, and ensure your fixes are safe to apply.
        """

        # Prepare user message with issue
        user_message = f"Issue:\n{json.dumps(issue, indent=2)}\n\nGenerate a fix for this issue."

        # Prepare request payload
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": system_prompt + "\n\n" + user_message}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": self.max_tokens,
                "temperature": self.temperature,
            },
        }

        try:
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()

            return {
                "provider": "gemini",
                "model": self.model,
                "fix": result["candidates"][0]["content"]["parts"][0]["text"],
                "raw_response": result,
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API request failed: {str(e)}")
            raise AIProviderError(f"Gemini API request failed: {str(e)}")

    def validate_credentials(self) -> bool:
        """Validate Gemini API credentials."""
        if not self.api_key:
            return False

        try:
            # Simple request to validate API key
            response = requests.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}",
                timeout=10,
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def estimate_cost(self, input_text: str, expected_output_length: int = 500) -> Dict[str, Any]:
        """Estimate the cost of an API call to Gemini."""
        # Gemini pricing (as of 2025)
        model_pricing = {
            "gemini-pro": {
                "input_per_1m_tokens": 0.50,
                "output_per_1m_tokens": 1.50,
            },
            "gemini-ultra": {
                "input_per_1m_tokens": 2.50,
                "output_per_1m_tokens": 7.50,
            },
        }

        # Get pricing for selected model
        pricing = model_pricing.get(self.model, model_pricing["gemini-pro"])

        # Count tokens
        input_tokens = self.get_token_count(input_text)

        # Calculate costs
        input_cost = (input_tokens / 1_000_000) * pricing["input_per_1m_tokens"]
        output_cost = (expected_output_length / 1_000_000) * pricing["output_per_1m_tokens"]
        total_cost = input_cost + output_cost

        return {
            "provider": "gemini",
            "model": self.model,
            "input_tokens": input_tokens,
            "output_tokens": expected_output_length,
            "input_cost_usd": input_cost,
            "output_cost_usd": output_cost,
            "estimated_cost_usd": total_cost,
            "pricing_info": pricing,
        }

    def get_token_count(self, text: str) -> int:
        """Get token count for Gemini."""
        try:
            # Try to use tiktoken for approximation
            import tiktoken
            enc = tiktoken.encoding_for_model("gpt-3.5-turbo")  # Close enough approximation
            return len(enc.encode(text))
        except ImportError:
            # Fall back to the approximate method
            return super().get_token_count(text)

    def report_capabilities(self) -> Dict[str, Any]:
        """Report Gemini provider capabilities."""
        return {
            "streaming": True,
            "vision": True,
            "batching": False,
            "function_calling": True,
            "token_counting": False,  # No official tokenizer
        }

    def streaming_analyze(self, context: Dict[str, Any], query: str, callback: Callable[[str], None]) -> Dict[str, Any]:
        """Analyze a query with context using streaming response."""
        if not self.api_key:
            raise AIProviderError("Gemini API key not configured")

        # Prepare system prompt
        system_prompt = """
        You are DockerForge AI, an expert in Docker troubleshooting and analysis.
        Analyze the provided Docker logs, configuration, or issue description.
        Identify problems, their root causes, and suggest specific fixes.
        Be concise, technical, and actionable in your responses.
        """

        # Prepare user message with context
        user_message = f"Context:\n{json.dumps(context, indent=2)}\n\nQuery: {query}"

        # Prepare request payload
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": system_prompt + "\n\n" + user_message}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": self.max_tokens,
                "temperature": self.temperature,
            },
            "stream": True,
        }

        try:
            # Use streaming response
            with requests.post(
                f"{self.api_url}?key={self.api_key}&alt=sse",  # Server-sent events
                headers=self.headers,
                json=payload,
                timeout=60,
                stream=True,
            ) as response:
                response.raise_for_status()

                # Process streaming response
                full_text = ""
                for line in response.iter_lines():
                    if line:
                        # Parse the SSE data
                        try:
                            line_text = line.decode("utf-8")
                            if line_text.startswith("data: "):
                                data = json.loads(line_text[6:])  # Skip "data: "
                                if "candidates" in data and data["candidates"]:
                                    chunk = data["candidates"][0]["content"]["parts"][0]["text"]
                                    full_text += chunk
                                    if callback and callable(callback):
                                        callback(chunk)
                        except (json.JSONDecodeError, KeyError, IndexError) as e:
                            logger.debug(f"Error parsing streaming response: {str(e)}")

                return {
                    "provider": "gemini",
                    "model": self.model,
                    "analysis": full_text,
                }
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API streaming request failed: {str(e)}")
            # Fall back to non-streaming request
            return self.analyze(context, query)


class OllamaProvider(AIProvider):
    """Ollama AI provider."""

    def __init__(self):
        """Initialize the Ollama provider."""
        self.endpoint = get_config("ai.providers.ollama.endpoint", "http://localhost:11434")
        self.model = get_config("ai.providers.ollama.model", "llama3")
        self.api_url = f"{self.endpoint}/api/generate"
        self.headers = {
            "Content-Type": "application/json",
        }

        # Initialize usage tracking
        self.usage_tracker = self._init_usage_tracker()

        # Check for auto-discovery
        auto_discover = get_config("ai.providers.ollama.auto_discover", True)
        container_discovery = get_config("ai.providers.ollama.container_discovery", True)

        if auto_discover and container_discovery:
            self._discover_ollama_container()

    def _init_usage_tracker(self):
        """Initialize the usage tracker."""
        try:
            from src.core.ai_usage_tracker import AIUsageTracker
            return AIUsageTracker()
        except ImportError:
            logger.debug("AIUsageTracker not available, usage tracking disabled")
            return None

    def _discover_ollama_container(self):
        """Discover Ollama running in a Docker container."""
        try:
            from src.docker.connection_manager import get_docker_connection_manager

            # Get Docker connection manager
            manager = get_docker_connection_manager()

            # Try to detect Ollama container
            try:
                # Connect to Docker
                docker_client = manager.connect()

                # Look for containers with Ollama image or name
                containers = docker_client.containers.list(
                    filters={"status": "running"}
                )

                # Get container name patterns from config
                name_patterns = get_config("ai.providers.ollama.container_name_patterns", ["ollama", "llama"])

                for container in containers:
                    # Check image name
                    image_name = container.image.tags[0] if container.image.tags else ""
                    container_name = container.name

                    # Check if container matches patterns
                    matches = False
                    for pattern in name_patterns:
                        if (pattern.lower() in image_name.lower() or
                            pattern.lower() in container_name.lower()):
                            matches = True
                            break

                    if not matches:
                        continue

                    # Get container IP address
                    networks = container.attrs['NetworkSettings']['Networks']
                    ip_address = None
                    for network in networks.values():
                        ip_address = network.get('IPAddress')
                        if ip_address:
                            break

                    # Get port mappings
                    port_bindings = container.attrs['NetworkSettings']['Ports']
                    api_port = None

                    # Look for the Ollama API port (default 11434)
                    for port, bindings in port_bindings.items():
                        if port.startswith('11434'):
                            if bindings:
                                for binding in bindings:
                                    host_ip = binding['HostIp'] or 'localhost'
                                    host_port = binding['HostPort']
                                    api_port = f"http://{host_ip}:{host_port}"
                                    break

                    # If exposed port not found, try internal IP
                    if not api_port and ip_address:
                        api_port = f"http://{ip_address}:11434"

                    # If we found a potential endpoint
                    if api_port:
                        # Test the endpoint
                        try:
                            response = requests.get(f"{api_port}/api/tags", timeout=2)
                            if response.status_code == 200:
                                logger.info(f"Discovered Ollama container endpoint: {api_port}")
                                self.endpoint = api_port
                                self.api_url = f"{self.endpoint}/api/generate"

                                # Check available models
                                try:
                                    models = response.json().get("models", [])
                                    if models and self.model not in [m["name"] for m in models]:
                                        # Use first available model as fallback
                                        self.model = models[0]["name"]
                                        logger.info(f"Using available model from container: {self.model}")
                                except (KeyError, IndexError, json.JSONDecodeError):
                                    pass

                                return
                        except requests.exceptions.RequestException:
                            # Try next container if this one doesn't respond
                            continue
            except Exception as e:
                logger.debug(f"Error discovering Ollama container: {str(e)}")
        except ImportError:
            logger.debug("Docker connection manager not available, container discovery disabled")

    def analyze(self, context: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Analyze a query with context using Ollama."""
        # Prepare system prompt
        system_prompt = """
        You are DockerForge AI, an expert in Docker troubleshooting and analysis.
        Analyze the provided Docker logs, configuration, or issue description.
        Identify problems, their root causes, and suggest specific fixes.
        Be concise, technical, and actionable in your responses.
        """

        # Prepare user message with context
        user_message = f"Context:\n{json.dumps(context, indent=2)}\n\nQuery: {query}"

        # Prepare request payload
        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\n{user_message}",
            "stream": False,
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()

            return {
                "provider": "ollama",
                "model": self.model,
                "analysis": result["response"],
                "raw_response": result,
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {str(e)}")
            raise AIProviderError(f"Ollama API request failed: {str(e)}")

    def generate_fix(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fix for an issue using Ollama."""
        # Prepare system prompt
        system_prompt = """
        You are DockerForge AI, an expert in Docker troubleshooting and fixes.
        Generate specific, actionable fixes for the provided Docker issue.
        Include commands to run, configuration changes to make, or other steps to resolve the issue.
        Be concise, technical, and ensure your fixes are safe to apply.
        """

        # Prepare user message with issue
        user_message = f"Issue:\n{json.dumps(issue, indent=2)}\n\nGenerate a fix for this issue."

        # Prepare request payload
        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\n{user_message}",
            "stream": False,
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()

            return {
                "provider": "ollama",
                "model": self.model,
                "fix": result["response"],
                "raw_response": result,
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {str(e)}")
            raise AIProviderError(f"Ollama API request failed: {str(e)}")

    def validate_credentials(self) -> bool:
        """Validate Ollama API credentials."""
        try:
            # Simple request to validate API endpoint
            response = requests.get(
                f"{self.endpoint}/api/tags",
                timeout=10,
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def estimate_cost(self, input_text: str, expected_output_length: int = 500) -> Dict[str, Any]:
        """Estimate the cost of an API call to Ollama."""
        # Ollama is free to use, so the cost is always 0
        return {
            "provider": "ollama",
            "model": self.model,
            "input_tokens": self.get_token_count(input_text),
            "output_tokens": expected_output_length,
            "input_cost_usd": 0.0,
            "output_cost_usd": 0.0,
            "estimated_cost_usd": 0.0,
            "pricing_info": {
                "input_per_1m_tokens": 0.0,
                "output_per_1m_tokens": 0.0,
                "notes": "Ollama is free to use locally or in containers"
            },
        }

    def get_token_count(self, text: str) -> int:
        """Get token count for Ollama."""
        # Try to get token count from Ollama API if available
        try:
            payload = {
                "model": self.model,
                "prompt": text,
            }
            response = requests.post(
                f"{self.endpoint}/api/tokenize",
                headers=self.headers,
                json=payload,
                timeout=10,
            )
            if response.status_code == 200:
                result = response.json()
                return len(result.get("tokens", []))
        except requests.exceptions.RequestException:
            pass

        # Fall back to the approximate method
        return super().get_token_count(text)

    def report_capabilities(self) -> Dict[str, Any]:
        """Report Ollama provider capabilities."""
        return {
            "streaming": True,
            "vision": False,  # Depends on model, but most don't support it yet
            "batching": False,
            "function_calling": False,
            "token_counting": True,
            "free_to_use": True,
            "local_execution": True,
        }

    def streaming_analyze(self, context: Dict[str, Any], query: str, callback: Callable[[str], None]) -> Dict[str, Any]:
        """Analyze a query with context using streaming response."""
        # Prepare system prompt
        system_prompt = """
        You are DockerForge AI, an expert in Docker troubleshooting and analysis.
        Analyze the provided Docker logs, configuration, or issue description.
        Identify problems, their root causes, and suggest specific fixes.
        Be concise, technical, and actionable in your responses.
        """

        # Prepare user message with context
        user_message = f"Context:\n{json.dumps(context, indent=2)}\n\nQuery: {query}"

        # Prepare request payload
        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\n{user_message}",
            "stream": True,
        }

        try:
            # Use streaming response
            with requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60,
                stream=True,
            ) as response:
                response.raise_for_status()

                # Process streaming response
                full_text = ""
                for line in response.iter_lines():
                    if line:
                        # Parse the JSON data
                        try:
                            data = json.loads(line.decode("utf-8"))
                            if "response" in data:
                                chunk = data["response"]
                                full_text += chunk
                                if callback and callable(callback):
                                    callback(chunk)

                            # Check if done
                            if data.get("done", False):
                                break
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.debug(f"Error parsing streaming response: {str(e)}")

                return {
                    "provider": "ollama",
                    "model": self.model,
                    "analysis": full_text,
                }
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API streaming request failed: {str(e)}")
            # Fall back to non-streaming request
            return self.analyze(context, query)


class MockAIProvider(AIProvider):
    """Mock AI provider for testing."""

    def __init__(self):
        """Initialize the mock AI provider."""
        self.logger = get_logger("core.ai_provider.mock")

    def analyze(self, context: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Mock implementation of analyze."""
        self.logger.info(f"Mock analyze called with query: {query[:50]}...")
        return {
            "analysis": f"This is a mock response to: {query[:50]}...",
            "confidence": 0.95,
            "model": "mock-model",
            "tokens": {"input": len(query.split()), "output": 20}
        }

    def generate_fix(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Mock implementation of generate_fix."""
        self.logger.info(f"Mock generate_fix called for issue: {issue.get('id', 'unknown')}")
        return {
            "fix": f"Mock fix for issue {issue.get('id', 'unknown')}",
            "steps": ["Step 1: Mock step", "Step 2: Another mock step"],
            "confidence": 0.9,
            "model": "mock-model"
        }

    def validate_credentials(self) -> bool:
        """Mock implementation of validate_credentials."""
        return True

    def estimate_cost(self, input_text: str, expected_output_length: int = 500) -> Dict[str, Any]:
        """Mock implementation of estimate_cost."""
        return {
            "estimated_cost": 0.0,
            "input_tokens": len(input_text.split()),
            "output_tokens": expected_output_length,
            "currency": "USD"
        }

    def generate_text(self, prompt: str) -> str:
        """Mock implementation of generate_text."""
        self.logger.info(f"Mock generate_text called with prompt: {prompt[:50]}...")
        return f"This is a mock response to your question about Docker. The prompt was: {prompt[:50]}..."


class AIProviderFactory:
    """Factory for creating AI providers with plugin support."""

    @staticmethod
    def create_provider(provider_name: Optional[str] = None) -> AIProvider:
        """
        Create an AI provider.

        Args:
            provider_name: Provider name (default: from config)

        Returns:
            AIProvider: AI provider

        Raises:
            AIProviderError: If provider is not supported or not configured
        """
        if provider_name is None:
            provider_name = get_config("ai.default_provider", "mock")

        # Check built-in providers first
        if provider_name == "claude":
            if get_config("ai.providers.claude.enabled", False):
                return ClaudeProvider()
            else:
                # Fall back to mock provider for testing
                return MockAIProvider()
        elif provider_name == "gemini":
            if get_config("ai.providers.gemini.enabled", False):
                return GeminiProvider()
            else:
                # Fall back to mock provider for testing
                return MockAIProvider()
        elif provider_name == "ollama":
            if get_config("ai.providers.ollama.enabled", False):
                return OllamaProvider()
            else:
                # Fall back to mock provider for testing
                return MockAIProvider()
        elif provider_name == "mock":
            return MockAIProvider()

        # Check for plugin providers
        try:
            from src.core.plugin_manager import get_plugin_provider

            # Try to get provider from plugin
            try:
                return get_plugin_provider(provider_name)
            except Exception as e:
                logger.debug(f"Plugin provider not found: {str(e)}")
        except ImportError:
            logger.debug("Plugin manager not available")

        # If we get here, the provider is not supported
        raise AIProviderError(f"Unsupported AI provider: {provider_name}")

    @staticmethod
    def list_available_providers() -> Dict[str, Any]:
        """
        List available AI providers.

        Returns:
            Dict[str, Any]: Available providers and their status
        """
        providers = {
            "mock": {
                "enabled": True,
                "available": True,
                "type": "built-in",
                "description": "Mock provider for testing"
            },
            "claude": {
                "enabled": get_config("ai.providers.claude.enabled", False),
                "available": get_config("ai.providers.claude.api_key") is not None,
                "type": "built-in",
            },
            "gemini": {
                "enabled": get_config("ai.providers.gemini.enabled", False),
                "available": get_config("ai.providers.gemini.api_key") is not None,
                "type": "built-in",
            },
            "ollama": {
                "enabled": get_config("ai.providers.ollama.enabled", False),
                "available": True,  # Ollama is always potentially available
                "type": "built-in",
            }
        }

        # Check for plugins
        try:
            from src.core.plugin_manager import get_plugin_manager

            # Get plugin manager
            plugin_manager = get_plugin_manager()

            # Add plugins to providers
            for plugin_info in plugin_manager.list_plugins():
                providers[plugin_info["name"]] = {
                    "enabled": True,  # Plugins are enabled by default
                    "available": True,
                    "type": "plugin",
                    "version": plugin_info["version"],
                    "author": plugin_info["author"],
                    "description": plugin_info["description"],
                }
        except ImportError:
            logger.debug("Plugin manager not available")

        return providers


def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """
    Get an AI provider.

    Args:
        provider_name: Provider name (default: from config)

    Returns:
        AIProvider: AI provider

    Raises:
        AIProviderError: If provider is not supported or not configured
    """
    return AIProviderFactory.create_provider(provider_name)
