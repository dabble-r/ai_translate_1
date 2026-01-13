## Project Layout
```
meta-llama3.1-boilerplate/
│
├── config/
│   ├── __init__.py
│   └── config.py
│
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── model_integration.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── prompt_templates.py
│   │
│   └── __init__.py
│
├── .env (create from env.template)
├── env.template (template for .env file)
├── ENV_SETUP_GUIDE.md (detailed setup instructions)
├── app.py
├── main.py
├── README.md
└── requirements.txt
```

## Quick Setup

1. **Copy the environment template:**
   ```bash
   cp env.template .env
   ```

2. **Edit `.env` and add your IBM Watson X credentials:**
   ```bash
   IBM_BASE_URL=https://us-south.ml.cloud.ibm.com
   IBM_API_KEY=your_api_key_here
   IBM_PROJECT_ID=your_project_id_here
   ```

3. **See `ENV_SETUP_GUIDE.md` for detailed configuration options**

## API Request Sample

```from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from <sdk-package-name>.example_service_v1 import *

# Create the authenticator.
authenticator = IAMAuthenticator('myapikey')

# Construct the service instance.
service = ExampleServiceV1(authenticator=authenticator)

# Use 'service' to invoke operations.
```

## Expected Response 
```
{
  "access_token": "eyJhbGciOiJIUz......sgrKIi8hdFs",
  "refresh_token": "not_supported",
  "ims_user_id": 118...90,
  "token_type": "Bearer",
  "expires_in": 3600,
  "expiration": 1473188353,
  "scope": "ibm openid"
}
```

## Bearer Token
```
from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator

authenticator = BearerTokenAuthenticator(<your_bearer_token>)
service = ExampleService(authenticator=authenticator)

# after getting a new access token...
service.get_authenticator().set_bearer_token('54321');
```

## Basic Authenticator 
```
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator

authenticator = BasicAuthenticator(<your_username>, <your_password>)
service = ExampleService(authenticator=authenticator)
```