# OpenAI Provider Plugin for DockerForge

This plugin adds OpenAI API support to DockerForge, allowing you to use GPT models for Docker troubleshooting and analysis.

## Features

- Support for GPT-4o, GPT-4-turbo, and GPT-3.5-turbo models
- Streaming responses for real-time analysis
- Accurate token counting and cost estimation
- Full integration with DockerForge's cost management system

## Installation

1. Copy this directory to your DockerForge plugins directory:
   ```
   cp -r openai_plugin ~/.dockerforge/plugins/
   ```

2. Install the required dependencies:
   ```
   pip install openai>=1.0.0 tiktoken
   ```

3. Add your OpenAI API key to your DockerForge configuration:
   ```yaml
   ai:
     providers:
       openai:
         enabled: true
         api_key: "your-api-key-here"
         model: "gpt-4o"  # or "gpt-4-turbo", "gpt-3.5-turbo"
         max_tokens: 4000
         temperature: 0.7
   ```

4. Restart DockerForge or reload plugins.

## Usage

Once installed, you can use the OpenAI provider like any other AI provider in DockerForge:

```bash
# Set OpenAI as the default provider
dockerforge config set ai.default_provider openai

# Use OpenAI for troubleshooting
dockerforge troubleshoot container my-container

# Use OpenAI for analyzing a Dockerfile
dockerforge analyze dockerfile ./Dockerfile
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `api_key` | Your OpenAI API key | None (required) |
| `model` | The model to use | "gpt-4o" |
| `max_tokens` | Maximum tokens in the response | 4000 |
| `temperature` | Randomness of the output (0.0-1.0) | 0.7 |

## Cost Management

This plugin fully integrates with DockerForge's cost management system. You can set budget limits in your configuration:

```yaml
ai:
  cost_management:
    require_confirmation: true
    confirmation_threshold_usd: 0.5
    max_daily_cost_usd: 10.0
    max_monthly_cost_usd: 50.0
```

## Pricing Information

| Model | Input Cost (per 1M tokens) | Output Cost (per 1M tokens) |
|-------|----------------------------|------------------------------|
| gpt-4o | $5.00 | $15.00 |
| gpt-4-turbo | $10.00 | $30.00 |
| gpt-3.5-turbo | $0.50 | $1.50 |

*Note: Pricing is as of 2025 and may change. The plugin will be updated to reflect current pricing.*

## Troubleshooting

If you encounter issues with the plugin:

1. Verify your API key is correct
2. Check that you have the required dependencies installed
3. Look at the DockerForge logs for error messages
4. Ensure you have sufficient credits in your OpenAI account

## Development

To modify this plugin, edit the `plugin.py` file. The main class is `OpenAIProvider`, which implements the `AIProvider` interface.

Key methods you might want to customize:
- `analyze`: Analyzes Docker issues
- `generate_fix`: Generates fixes for issues
- `streaming_analyze`: Provides streaming analysis
