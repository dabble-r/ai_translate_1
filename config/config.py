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

    # IBM Cloud endpoint (example of adding a new endpoint)
    IBM_BASE_URL = os.getenv("IBM_BASE_URL")
    IBM_API_KEY = os.getenv("IBM_API_KEY")

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