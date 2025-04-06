# Google Gemini API Integration

This document provides information on how to set up and use the Google Gemini API integration in DockerForge.

## API Key Setup

To use the Google Gemini API, you need to obtain an API key from Google:

1. Go to the [Google AI Studio](https://ai.google.dev/) and sign in with your Google account.
2. Navigate to the API keys section.
3. Create a new API key.
4. Copy the API key.

Once you have the API key, you can configure DockerForge to use it in one of the following ways:

### Option 1: Environment Variable

Set the `GEMINI_API_KEY` environment variable:

```bash
export GEMINI_API_KEY=your-api-key
```

### Option 2: Configuration File

Edit the `config/dockerforge.yaml` file and set the API key:

```yaml
ai:
  providers:
    gemini:
      api_key: "your-api-key"
```

### Option 3: .env File

Create or edit the `.env` file in the project root directory:

```
GEMINI_API_KEY=your-api-key
```

## Usage Examples

### Using the Gemini API in Python Code

```python
from src.core.ai_provider import get_ai_provider

# Get the Gemini provider
provider = get_ai_provider("gemini")

# Generate text
response = provider.generate_text("Explain Docker volumes in one paragraph.")
print(response)

# Analyze Docker logs
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
result = provider.analyze(context, query)
print(result["analysis"])

# Estimate cost
cost_info = provider.estimate_cost("Some input text", 500)
print(f"Estimated cost: ${cost_info['estimated_cost_usd']:.4f}")
```

### Using the Gemini API in CLI

```bash
# Analyze container logs with Gemini
dockerforge analyze --provider gemini my-container

# Troubleshoot Docker Compose issues with Gemini
dockerforge compose troubleshoot --provider gemini ./docker-compose.yml

# Chat with Gemini about Docker
dockerforge chat --provider gemini
```

## Configuration Options

The following configuration options are available for the Gemini API integration:

```yaml
ai:
  default_provider: gemini  # Set Gemini as the default AI provider
  providers:
    gemini:
      enabled: true  # Enable the Gemini provider
      api_key: "${GEMINI_API_KEY}"  # API key (can use environment variable)
      model: "models/gemini-1.5-pro"  # Model to use
      max_tokens: 2048  # Maximum number of tokens in the response
      temperature: 0.7  # Temperature for text generation (0.0 to 1.0)
```

### Available Models

The following Gemini models are available:

- `models/gemini-1.5-pro`: General-purpose model with good performance
- `models/gemini-1.5-flash`: Faster, more efficient model
- `models/gemini-pro-vision`: Model with vision capabilities

To list all available models, you can use the `list_gemini_models.py` script:

```bash
python list_gemini_models.py
```

## Troubleshooting

### API Key Issues

If you encounter issues with the API key, check the following:

1. Verify that the API key is correct.
2. Ensure that the API key has the necessary permissions.
3. Check if the API key has reached its quota limit.

### Model Issues

If you encounter issues with the model, check the following:

1. Verify that the model name is correct.
2. Ensure that the model is available in your region.
3. Check if the model has any specific requirements or limitations.

### Network Issues

If you encounter network issues, check the following:

1. Verify that your network connection is working.
2. Check if your network has any firewall rules that might block the API calls.
3. Ensure that your network can reach the Google Gemini API endpoints.

## Cost Management

The Gemini API integration includes cost management features to help you control your API usage costs:

```yaml
ai:
  cost_management:
    require_confirmation: true  # Require confirmation for expensive API calls
    confirmation_threshold_usd: 0.5  # Threshold for confirmation (in USD)
    max_daily_cost_usd: 10.0  # Maximum daily cost (in USD)
    max_monthly_cost_usd: 50.0  # Maximum monthly cost (in USD)
```

These settings help prevent unexpected costs by requiring confirmation for expensive API calls and setting limits on daily and monthly usage.
