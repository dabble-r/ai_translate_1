# Endpoint Setup Guide

This guide explains how to add new API endpoints and API keys to the translation application.

## Overview

The application supports multiple API endpoints through environment variables and configuration classes. Currently supported:
- **Hosted endpoints** (OpenAI-compatible APIs like AIML API)
- **Local Ollama** (self-hosted models)
- **IBM Cloud** (example of custom endpoint)

---

## Step-by-Step: Adding a New Endpoint

### Step 1: Add Variables to `.env` File

Open the `.env` file in the project root and add your endpoint configuration:

```bash
# Existing endpoints
HOSTED_BASE_URL = https://api.aimlapi.com/v1
HOSTED_API_KEY = your_api_key_here
LOCAL_BASE_URL = http://localhost:11434/api/chat

# New endpoint example (replace with your actual values)
NEW_ENDPOINT_URL = https://api.example.com/v1
NEW_ENDPOINT_KEY = your_new_api_key_here
```

**Important Notes:**
- Use descriptive names (e.g., `IBM_BASE_URL`, `ANTHROPIC_API_KEY`)
- No spaces around the `=` sign
- No quotes needed (unless the value contains special characters)
- Keep API keys secure - never commit `.env` to version control

---

### Step 2: Update `config/config.py`

Add properties to the `Config` class to read your new environment variables:

```python
class Config:
    # Existing configurations
    HOSTED_BASE_URL = os.getenv("HOSTED_BASE_URL")
    HOSTED_API_KEY = os.getenv("HOSTED_API_KEY")
    LOCAL_BASE_URL = os.getenv("LOCAL_BASE_URL")
    
    # Add your new endpoint here
    NEW_ENDPOINT_URL = os.getenv("NEW_ENDPOINT_URL")
    NEW_ENDPOINT_KEY = os.getenv("NEW_ENDPOINT_KEY")
```

**Example (IBM Cloud):**
```python
IBM_BASE_URL = os.getenv("IBM_BASE_URL")
IBM_API_KEY = os.getenv("IBM_API_KEY")
```

---

### Step 3: Update `get_api_config()` Function

Edit `src/api/model_integration.py` and add a condition in `get_api_config()` to return your new endpoint:

```python
def get_api_config(model_name):
    if model_name.startswith("meta-llama/"):
        return Config.HOSTED_BASE_URL, Config.HOSTED_API_KEY
    elif model_name == "llama3.1:8b":
        return Config.LOCAL_BASE_URL, None
    elif model_name.startswith("new-endpoint-"):
        # Add your new endpoint here
        return Config.NEW_ENDPOINT_URL, Config.NEW_ENDPOINT_KEY
    else:
        raise ValueError(f"Invalid model name: {model_name}")
```

**Example (IBM Cloud):**
```python
elif model_name.startswith("ibm-"):
    return Config.IBM_BASE_URL, Config.IBM_API_KEY
```

**Model Name Patterns:**
- Use prefixes (e.g., `"ibm-"`, `"anthropic-"`) to group related models
- Or use exact matches (e.g., `model_name == "specific-model-name"`)

---

### Step 4: Update `stream_response()` Function

Add handling for your new endpoint in `stream_response()`:

```python
def stream_response(messages, container, model_name):
    base_url, api_key = get_api_config(model_name)

    if model_name.startswith("meta-llama/"):
        # OpenAI-compatible API
        client = OpenAI(api_key=api_key, base_url=base_url)
        return handle_hosted_request(client, model_name, messages, container)
    elif model_name == "llama3.1:8b":
        # Ollama-compatible API
        return handle_local_request(base_url, model_name, messages, container)
    elif model_name.startswith("new-endpoint-"):
        # Choose the appropriate handler:
        # - handle_hosted_request() for OpenAI-compatible APIs
        # - handle_local_request() for Ollama-compatible APIs
        # - Or create a custom handler for unique formats
        client = OpenAI(api_key=api_key, base_url=base_url)
        return handle_hosted_request(client, model_name, messages, container)
    else:
        raise ValueError("Unsupported model selected.")
```

**Handler Selection:**
- **`handle_hosted_request()`**: Use for OpenAI-compatible APIs (most hosted services)
- **`handle_local_request()`**: Use for Ollama-compatible streaming APIs
- **Custom handler**: Create if your API has a unique response format

---

### Step 5: Add Model to Available Models List

Update `config/config.py` to include your new model in `AVAILABLE_MODELS`:

```python
AVAILABLE_MODELS = [
    "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "llama3.1:8b",
    "new-endpoint-model-name",  # Add your model name here
]
```

**Model Name Convention:**
- Use the same name pattern you used in `get_api_config()`
- Make it descriptive and user-friendly
- Example: `"ibm-translate-v1"`, `"anthropic-claude-3"`

---

## Complete Example: IBM Cloud Endpoint

Here's a complete example of adding an IBM Cloud endpoint:

### 1. `.env` file:
```bash
IBM_BASE_URL = https://private.us-south.ml.cloud.ibm.com/ml/v1/deployments/translate_1/text/chat_stream?version=2021-05-01
IBM_API_KEY = your_ibm_api_key_here
```

### 2. `config/config.py`:
```python
IBM_BASE_URL = os.getenv("IBM_BASE_URL")
IBM_API_KEY = os.getenv("IBM_API_KEY")

AVAILABLE_MODELS = [
    # ... existing models ...
    "ibm-translate-v1",
]
```

### 3. `src/api/model_integration.py` - `get_api_config()`:
```python
elif model_name.startswith("ibm-"):
    return Config.IBM_BASE_URL, Config.IBM_API_KEY
```

### 4. `src/api/model_integration.py` - `stream_response()`:
```python
elif model_name.startswith("ibm-"):
    # If IBM uses OpenAI-compatible format:
    client = OpenAI(api_key=api_key, base_url=base_url)
    return handle_hosted_request(client, model_name, messages, container)
    # OR if IBM uses custom format, create a custom handler
```

---

## API Format Compatibility

### OpenAI-Compatible APIs
If your endpoint follows OpenAI's API format:
- Use `handle_hosted_request()`
- Requires: `base_url` and `api_key`
- Example: AIML API, most hosted LLM services

### Ollama-Compatible APIs
If your endpoint follows Ollama's streaming format:
- Use `handle_local_request()`
- Requires: `base_url` only (no API key)
- Response format: JSON lines with `{"message": {"content": "..."}, "done": false}`

### Custom API Formats
If your endpoint has a unique format:
1. Create a new handler function (similar to `handle_local_request()`)
2. Parse the response according to your API's format
3. Update the display using `response_placeholder.markdown()`

---

## Testing Your New Endpoint

1. **Set environment variables** in `.env`
2. **Restart Streamlit**: `streamlit run main.py`
3. **Select your model** from the dropdown in the UI
4. **Make a test request** and check:
   - Console output for any errors
   - Streamlit UI for response display
   - Network tab (if using browser dev tools) for API calls

---

## Troubleshooting

### Issue: "Invalid model name" error
**Solution**: Check that:
- Model name in `AVAILABLE_MODELS` matches the pattern in `get_api_config()`
- The condition in `get_api_config()` correctly identifies your model

### Issue: API returns 401/403 errors
**Solution**: Verify:
- API key is correctly set in `.env`
- API key has proper permissions
- API key is being read correctly (check `Config.YOUR_API_KEY`)

### Issue: No output displayed
**Solution**: Check:
- Response format matches the handler you're using
- Error handling is working (check console for exceptions)
- Container is being updated correctly

### Issue: Wrong response format
**Solution**: 
- Verify your API's response format
- Use the correct handler (hosted vs local)
- Or create a custom handler for unique formats

---

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use environment variables** for sensitive data
3. **Rotate API keys** regularly
4. **Use least-privilege** API keys when possible
5. **Validate API keys** before making requests (optional)

---

## Summary Checklist

When adding a new endpoint, ensure you:

- [ ] Added variables to `.env` file
- [ ] Updated `Config` class in `config/config.py`
- [ ] Updated `get_api_config()` function
- [ ] Updated `stream_response()` function
- [ ] Added model name to `AVAILABLE_MODELS`
- [ ] Tested the endpoint with a sample request
- [ ] Verified error handling works correctly

---

## Need Help?

If you encounter issues:
1. Check the console output for error messages
2. Verify all configuration steps were completed
3. Test the API endpoint directly (using `curl` or Postman)
4. Review the existing endpoint implementations as examples
