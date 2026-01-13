import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Config:
    """
    A configuration class that retrieves environment variables and stores configuration settings.
    """

    # API and Model configurations
    HOSTED_BASE_URL = os.getenv("HOSTED_BASE_URL")
    HOSTED_API_KEY = os.getenv("HOSTED_API_KEY")
    LOCAL_BASE_URL = os.getenv("LOCAL_BASE_URL")

    # IBM Watson X endpoint configuration
    IBM_BASE_URL = os.getenv("IBM_BASE_URL")
    IBM_API_KEY = os.getenv("IBM_API_KEY")
    IBM_PROJECT_ID = os.getenv("IBM_PROJECT_ID")
    IBM_MODEL_ID = os.getenv("IBM_MODEL_ID")  # Actual IBM model ID (e.g., "meta-llama/llama-3-70b-instruct")

    # Available models
    AVAILABLE_MODELS = [
        "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "llama3.1:8b",
        "ibm-translate"
        # Add new model names here when adding new endpoints
        # Example: "ibm-translate-model",
    ]