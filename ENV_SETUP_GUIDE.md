# .env File Setup Guide

This guide explains how to configure your `.env` file for IBM Watson X model selection.

## Required Configuration

Create a `.env` file in the project root with the following variables:

```bash
# IBM Watson X Base URL (region-specific)
# Replace {region} with your IBM Cloud region (e.g., us-south, eu-gb, jp-tok)
IBM_BASE_URL=https://us-south.ml.cloud.ibm.com

# IBM Cloud API Key
# Get this from: IBM Cloud Console > Manage > Access (IAM) > API keys
IBM_API_KEY=your_ibm_api_key_here

# IBM Watson X Project ID
# Get this from your IBM Watson X project settings
IBM_PROJECT_ID=your_project_id_here
```

## Optional Configuration

### Override Model ID

If you want to force a specific model for all requests (regardless of dropdown selection):

```bash
IBM_MODEL_ID=meta-llama/llama-3-3-70b-instruct
```

**Note**: If `IBM_MODEL_ID` is set, it will override the model selected from the dropdown.

### Specify Models for IBM Watson X

If you want to explicitly list which models should use IBM Watson X (comma-separated):

```bash
IBM_MODELS=meta-llama/llama-3-3-70b-instruct,mistral-large-2512,ibm/granite-3-8b-instruct
```

**Note**: By default, all models in `AVAILABLE_MODELS` automatically route to IBM Watson X, so this is usually not needed.

### Default Multilingual Model

Set a default multilingual chat model:

```bash
DEFAULT_MULTILINGUAL_MODEL=meta-llama/llama-3-3-70b-instruct
```

## Complete .env Example

```bash
# ============================================
# IBM Watson X Configuration
# ============================================

# Required: IBM Watson X Base URL
IBM_BASE_URL=https://us-south.ml.cloud.ibm.com

# Required: IBM Cloud API Key
IBM_API_KEY=your_ibm_api_key_here

# Required: IBM Watson X Project ID
IBM_PROJECT_ID=your_project_id_here

# Optional: Override model ID (if set, overrides dropdown selection)
# IBM_MODEL_ID=meta-llama/llama-3-3-70b-instruct

# Optional: Explicit list of models to use with IBM Watson X
# IBM_MODELS=meta-llama/llama-3-3-70b-instruct,mistral-large-2512

# Optional: Default multilingual model
DEFAULT_MULTILINGUAL_MODEL=meta-llama/llama-3-3-70b-instruct
```

## Model Selection

### How Model Selection Works

1. **Dropdown Selection**: Users select a model from the dropdown menu
2. **Model Routing**: All models automatically route to IBM Watson X
3. **Model ID Resolution**:
   - If `IBM_MODEL_ID` is set in `.env`, it overrides the dropdown selection
   - Otherwise, the model name from the dropdown is used as the IBM model ID

### Available Models

All models in the dropdown are IBM Watson X models. See `config/config.py` for the complete list of `AVAILABLE_MODELS`.

## Getting Your Credentials

### IBM API Key

1. Log in to [IBM Cloud Console](https://cloud.ibm.com)
2. Navigate to **Manage** > **Access (IAM)** > **API keys**
3. Click **Create an IBM Cloud API key**
4. Copy the API key and add it to your `.env` file

### IBM Project ID

1. Log in to [IBM Cloud Console](https://cloud.ibm.com)
2. Navigate to your Watson X project
3. Find the Project ID in the project settings/details
4. Copy the Project ID and add it to your `.env` file

### IBM Base URL

The base URL depends on your IBM Cloud region:

- **US South**: `https://us-south.ml.cloud.ibm.com`
- **EU Great Britain**: `https://eu-gb.ml.cloud.ibm.com`
- **Japan Tokyo**: `https://jp-tok.ml.cloud.ibm.com`
- **Other regions**: Check your IBM Cloud console for the correct URL

## Security Notes

- **Never commit `.env` files** to version control
- Keep your API keys secure
- Rotate API keys regularly
- Use least-privilege API keys when possible

## Troubleshooting

### Issue: "IBM API key is required"
**Solution**: Make sure `IBM_API_KEY` is set in your `.env` file

### Issue: "IBM Project ID is required"
**Solution**: Make sure `IBM_PROJECT_ID` is set in your `.env` file

### Issue: "IBM Base URL is required"
**Solution**: Make sure `IBM_BASE_URL` is set in your `.env` file

### Issue: Model not available
**Solution**: Check that the model name matches exactly what's available in your IBM Watson X environment
