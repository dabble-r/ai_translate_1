# Quick Reference: Adding a New Endpoint

## 5-Minute Setup

### 1. Add to `.env`
```bash
NEW_ENDPOINT_URL = https://api.example.com/v1
NEW_ENDPOINT_KEY = your_api_key
```

### 2. Add to `config/config.py`
```python
NEW_ENDPOINT_URL = os.getenv("NEW_ENDPOINT_URL")
NEW_ENDPOINT_KEY = os.getenv("NEW_ENDPOINT_KEY")
```

### 3. Update `get_api_config()` in `src/api/model_integration.py`
```python
elif model_name.startswith("new-endpoint-"):
    return Config.NEW_ENDPOINT_URL, Config.NEW_ENDPOINT_KEY
```

### 4. Update `stream_response()` in `src/api/model_integration.py`
```python
elif model_name.startswith("new-endpoint-"):
    client = OpenAI(api_key=api_key, base_url=base_url)
    return handle_hosted_request(client, model_name, messages, container)
```

### 5. Add to `AVAILABLE_MODELS` in `config/config.py`
```python
AVAILABLE_MODELS = [
    # ... existing models ...
    "new-endpoint-model-name",
]
```

## Handler Selection

- **OpenAI-compatible**: Use `handle_hosted_request()`
- **Ollama-compatible**: Use `handle_local_request()`
- **Custom format**: Create custom handler

## Current Endpoints

| Endpoint | Pattern | Handler | Config Variables |
|----------|---------|---------|------------------|
| Hosted (AIML) | `meta-llama/*` | `handle_hosted_request()` | `HOSTED_BASE_URL`, `HOSTED_API_KEY` |
| Local Ollama | `llama3.1:8b` | `handle_local_request()` | `LOCAL_BASE_URL` |
| IBM Cloud | `ibm-*` | `handle_hosted_request()` | `IBM_BASE_URL`, `IBM_API_KEY` |
