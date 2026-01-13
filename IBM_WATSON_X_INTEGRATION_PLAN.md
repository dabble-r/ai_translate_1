# IBM Watson X API Integration Plan

## Overview

This plan outlines the integration of IBM Watson X API into the translation application. Based on the README.md examples showing IBM Cloud SDK authentication patterns, we'll implement proper authentication and API calls for IBM Watson X.

## Current State Analysis

### Existing Implementation Issues:
1. **Incomplete IBM Integration**: Current code attempts to use OpenAI client for IBM endpoints, which won't work properly
2. **Authentication**: Using `IBM_API_KEY` directly instead of proper bearer token authentication
3. **No IBM SDK**: Not using IBM Cloud SDK as shown in README examples
4. **Missing Handler**: No dedicated IBM Watson X request handler

### What We Have:
- README.md shows IBM Cloud SDK authentication patterns:
  - `IAMAuthenticator` for API key-based auth
  - `BearerTokenAuthenticator` for direct bearer token
  - `BasicAuthenticator` for username/password
- Basic structure in `config/config.py` and `src/api/model_integration.py`
- IBM model listed in `AVAILABLE_MODELS` as `"ibm-translate"`

## Solution Approach

### Option 1: Use IBM Cloud SDK (Recommended)
- Install `ibm-cloud-sdk-core` and Watson X SDK
- Use `IAMAuthenticator` or `BearerTokenAuthenticator`
- Leverage official SDK for proper request handling

### Option 2: Direct HTTP with Bearer Token
- Use `requests` library with bearer token authentication
- Manual request/response handling
- More control but more implementation work

**Recommendation**: Start with Option 2 (direct HTTP) for simplicity, can migrate to SDK later if needed.

## Implementation Plan

### Phase 1: Configuration Setup

#### 1.1 Update `requirements.txt`
Add IBM Cloud SDK dependencies (optional, for future use):
```txt
ibm-cloud-sdk-core  # For authentication helpers
```

#### 1.2 Update `config/config.py`
Add IBM Watson X configuration:
- `IBM_WATSONX_URL` - Base URL for Watson X API endpoint
- `IBM_ACCESS_TOKEN` - Bearer token (preferred)
- `IBM_API_KEY` - API key (alternative, for token generation)
- `IBM_PROJECT_ID` - Watson X project ID (if required)

#### 1.3 Update `.env` file structure
Document required variables:
```bash
# IBM Watson X Configuration
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2024-05-20
IBM_ACCESS_TOKEN=your_bearer_token_here
# OR use API key to generate token:
IBM_API_KEY=your_api_key_here
IBM_PROJECT_ID=your_project_id_here
```

### Phase 2: Authentication Implementation

#### 2.1 Token Generation (if using API key)
Create helper function to generate bearer token from API key:
```python
def get_ibm_bearer_token(api_key):
    """Generate IBM bearer token from API key"""
    response = requests.post(
        'https://iam.cloud.ibm.com/identity/token',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
            'apikey': api_key
        }
    )
    response.raise_for_status()
    return response.json()['access_token']
```

#### 2.2 Update `get_api_config()` function
Modify to return IBM access token:
- Check for `IBM_ACCESS_TOKEN` first (direct bearer token)
- If not available, use `IBM_API_KEY` to generate token
- Return URL and token for IBM models

### Phase 3: IBM Watson X Request Handler

#### 3.1 Create `handle_ibm_watsonx_request()` function
Key features:
- Accept: `access_token`, `base_url`, `model_name`, `messages`, `container`
- Format request according to IBM Watson X API specification
- Handle streaming responses
- Proper error handling

#### 3.2 Request Format
IBM Watson X API typically expects:
```json
{
  "model_id": "model_name",
  "input": "user_message",
  "parameters": {
    "max_new_tokens": 100,
    "temperature": 0.7,
    "stream": true
  },
  "project_id": "project_id"
}
```

Or for chat format:
```json
{
  "model_id": "model_name",
  "input": [
    {"role": "user", "content": "message"}
  ],
  "parameters": {
    "max_new_tokens": 100,
    "temperature": 0.7,
    "stream": true
  },
  "project_id": "project_id"
}
```

#### 3.3 Response Handling
- Parse streaming response (SSE or JSON lines)
- Extract content from response chunks
- Update UI with streaming content
- Handle completion and errors

### Phase 4: Integration Updates

#### 4.1 Update `stream_response()` function
- Add IBM Watson X routing
- Call `handle_ibm_watsonx_request()` for IBM models
- Ensure proper error propagation

#### 4.2 Update model name pattern
- Ensure `get_api_config()` correctly identifies IBM models
- Update model name in `AVAILABLE_MODELS` if needed

### Phase 5: Error Handling & Edge Cases

#### 5.1 Authentication Errors
- Handle 401 Unauthorized (token expired)
- Handle 403 Forbidden (invalid permissions)
- Provide clear error messages

#### 5.2 Token Management
- Cache bearer token (with expiration tracking)
- Auto-refresh if token expires
- Fallback to API key if token unavailable

#### 5.3 API Errors
- Handle rate limiting (429)
- Handle service errors (500+)
- Network timeout handling

## Files to Modify

1. **`requirements.txt`**
   - Add `ibm-cloud-sdk-core` (optional)

2. **`config/config.py`**
   - Add `IBM_BASE_URL`
   - Add `IBM_ACCESS_TOKEN`
   - Add `IBM_API_KEY` (optional, for token generation)
   - Add `IBM_PROJECT_ID` (if required)

3. **`src/api/model_integration.py`**
   - Add `get_ibm_bearer_token()` helper function
   - Update `get_api_config()` for IBM models
   - Create `handle_ibm_watsonx_request()` function
   - Update `stream_response()` to route IBM requests

4. **`.env`** (user configuration)
   - Add IBM Watson X variables

5. **`ENDPOINT_SETUP_GUIDE.md`** (optional)
   - Update with IBM Watson X specific instructions

## Technical Details

### Authentication Flow
1. **Option A - Direct Bearer Token**:
   - User provides `IBM_ACCESS_TOKEN` in `.env`
   - Use token directly in `Authorization: Bearer <token>` header

2. **Option B - API Key to Token**:
   - User provides `IBM_API_KEY` in `.env`
   - Generate bearer token via IAM endpoint
   - Cache token for subsequent requests
   - Refresh when expired

### Request Headers
```python
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
```

### Streaming Response Format
IBM Watson X may use:
- Server-Sent Events (SSE)
- JSON lines (newline-delimited JSON)
- Standard JSON with streaming flag

Need to handle based on actual API response format.

## Testing Checklist

- [ ] Test with direct bearer token authentication
- [ ] Test with API key authentication (token generation)
- [ ] Test streaming response parsing
- [ ] Test error handling (401, 403, 500)
- [ ] Test token expiration and refresh
- [ ] Verify UI updates correctly during streaming
- [ ] Test with different model names
- [ ] Verify project ID handling (if required)

## Next Steps

1. **Research**: Confirm exact IBM Watson X API endpoint format and request/response structure
2. **Implement**: Start with Phase 1 (configuration)
3. **Test**: Use actual IBM Watson X credentials to test
4. **Iterate**: Adjust based on actual API behavior
5. **Document**: Update setup guide with IBM-specific instructions

## Alternative: Using IBM Cloud SDK

If we want to use the official SDK (as shown in README examples):

1. Install: `ibm-watson-machine-learning` or `ibm-watsonx-ai`
2. Use SDK's authentication and request methods
3. Leverage SDK's built-in streaming support
4. Follow SDK documentation for exact usage

This approach is more robust but requires understanding the specific SDK.

## Questions to Resolve

1. What is the exact IBM Watson X API endpoint format?
2. What is the exact request body structure?
3. What is the streaming response format (SSE, JSON lines, etc.)?
4. Is project_id required for all requests?
5. What models are available in the user's Watson X instance?

## References

- README.md authentication examples
- IBM Cloud IAM token endpoint: `https://iam.cloud.ibm.com/identity/token`
- IBM Watson X API documentation (to be consulted)
