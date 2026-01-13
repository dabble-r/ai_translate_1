import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Config:
    """
    A configuration class that retrieves environment variables and stores configuration settings.
    """

    # API and Model configurations
    # Note: HOSTED_BASE_URL and HOSTED_API_KEY removed - no longer using OpenAI-compatible hosted endpoints
    LOCAL_BASE_URL = os.getenv("LOCAL_BASE_URL")

    # IBM Watson X endpoint configuration
    IBM_BASE_URL = os.getenv("IBM_BASE_URL")
    IBM_API_KEY = os.getenv("IBM_API_KEY")
    IBM_PROJECT_ID = os.getenv("IBM_PROJECT_ID")
    IBM_MODEL_ID = os.getenv("IBM_MODEL_ID")  # Actual IBM model ID (e.g., "meta-llama/llama-3-70b-instruct")
    
    # Models that should use IBM Watson X (comma-separated list or specific model names)
    # If a model name is in this list, it will route to IBM Watson X instead of the default provider
    IBM_MODELS = os.getenv("IBM_MODELS", "").split(",") if os.getenv("IBM_MODELS") else []
    IBM_MODELS = [m.strip() for m in IBM_MODELS if m.strip()]  # Clean up whitespace
    
    # Default multilingual chat model (recommended for multilingual decode-encode tasks)
    # This model supports multiple languages and chat functionality
    DEFAULT_MULTILINGUAL_MODEL = os.getenv("DEFAULT_MULTILINGUAL_MODEL", "meta-llama/llama-3-3-70b-instruct")

    # Available models - Only IBM Watson X models
    # These models are available in IBM Watson X and will be routed automatically
    AVAILABLE_MODELS = [
        # Meta-Llama models (chat/instruct)
        "meta-llama/llama-3-1-8b",
        "meta-llama/llama-3-1-70b-gptq",
        "meta-llama/llama-3-3-70b-instruct",  # Multilingual chat model
        "meta-llama/llama-3-405b-instruct",
        "meta-llama/llama-3-2-11b-vision-instruct",
        "meta-llama/llama-3-2-90b-vision-instruct",
        "meta-llama/llama-4-maverick-17b-128e-instruct-fp8",
        "meta-llama/llama-guard-3-11b-vision",
        # Mistral models (multilingual chat)
        "mistralai/mistral-small-3-1-24b-instruct-2503",
        "mistralai/mistral-medium-2505",
        "mistral-large-2512",
        # IBM Granite models
        "ibm/granite-3-8b-instruct",
        "ibm/granite-3-3-8b-instruct",
        "ibm/granite-3-2-8b-instruct",
        "ibm/granite-3-1-8b-base",
        "ibm/granite-4-h-small",
        "ibm/granite-8b-code-instruct",
        "ibm/granite-guardian-3-8b",
        # Embedding models
        "intfloat/multilingual-e5-large",
        "ibm/granite-embedding-278m-multilingual",
        "sentence-transformers/all-minilm-l6-v2",
        # Other models
        "openai/gpt-oss-120b",
        "cross-encoder/ms-marco-minilm-l-12-v2"
    ]