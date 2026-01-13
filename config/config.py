import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


class Config:
    """
    Simple configuration class for available models.
    """
    
    # Available models - Only IBM Watson X models
    AVAILABLE_MODELS = [
        "ibm/granite-4-h-small",
        "meta-llama/llama-3-2-11b-vision-instruct",
        "meta-llama/llama-3-2-90b-vision-instruct",
        "meta-llama/llama-3-3-70b-instruct",
        "meta-llama/llama-4-maverick-17b-128e-instruct-fp8",
        "mistralai/mistral-medium-2505"
    ]