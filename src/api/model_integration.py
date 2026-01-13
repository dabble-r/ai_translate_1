import requests
import json
from openai import OpenAI
from config.config import Config

# IBM Watson X SDK imports
try:
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    IBM_SDK_AVAILABLE = True
except ImportError:
    IBM_SDK_AVAILABLE = False
    print("Warning: ibm-watsonx-ai SDK not installed. Install with: pip install ibm-watsonx-ai")


def get_ibm_bearer_token(api_key):
    """
    Generate IBM bearer token from API key.
    Args:
        api_key: IBM Cloud API key
        
    Returns:
        str: Bearer token (access token)
    """
    try:
        response = requests.post(
            'https://iam.cloud.ibm.com/identity/token',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
                'apikey': api_key
            }
        )
        response.raise_for_status()
        token_data = response.json()
        return token_data['access_token']
    except requests.RequestException as e:
        raise Exception(f"Failed to generate IBM bearer token: {str(e)}")


def get_api_config(model_name):
    
    """
    Get API base URL and API key based on the model name.
    
    To add a new endpoint:
    1. Add variables to .env file (e.g., NEW_ENDPOINT_URL, NEW_ENDPOINT_KEY)
    2. Add properties to Config class (e.g., Config.NEW_ENDPOINT_URL)
    3. Add elif condition here to return the new endpoint
    """
    if model_name.startswith("meta-llama/"):
        return Config.HOSTED_BASE_URL, Config.HOSTED_API_KEY, None
    elif model_name == "llama3.1:8b":
        print("local model selected")
        return Config.LOCAL_BASE_URL, None, None
    elif model_name.startswith("ibm"):
        # IBM Watson X endpoint - returns (base_url, api_key, project_id)
        # Note: model_id is handled separately in handle_ibm_watsonx_request
        return Config.IBM_BASE_URL, Config.IBM_API_KEY, Config.IBM_PROJECT_ID
    else:
        raise ValueError(f"Invalid model name: {model_name}")


def handle_hosted_request(client, model_name, messages, container):
    """
    Handles the hosted Llama 3.1 model requests via OpenAI's API.
    """
    try:
        stream = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True,
        )
        response_placeholder = container.empty()
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(full_response + "▌")
        response_placeholder.markdown(full_response)
        return full_response
    except Exception as e:
        error_message = f"API Error: {str(e)}"
        container.error(error_message)
        return None


def handle_local_request(base_url, model_name, messages, container):
    """
    Handles requests to the locally hosted Llama 3.1 model.
    """
    try:
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": True,
        }
        headers = {"Content-Type": "application/json"}

        response_placeholder = container.empty()
        response_placeholder.info("🔄 Processing request...")
        full_response = ""

        with requests.post(
            base_url, json=payload, headers=headers, stream=True
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        # Decode bytes to string if needed
                        if isinstance(line, bytes):
                            line = line.decode('utf-8')
                        
                        chunk = json.loads(line)
                        
                        # Check if done
                        if chunk.get("done", False):
                            break
                        
                        # Extract content if available
                        if "message" in chunk and "content" in chunk["message"]:
                            content = chunk["message"]["content"]
                            if content:  # Only add non-empty content
                                full_response += content
                                # Update the display with streaming cursor
                                response_placeholder.markdown(full_response + "▌")
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}, line: {line}")
                        pass
                    except Exception as e:
                        print(f"Error processing chunk: {e}")
                        pass
        
        # Final update without cursor
        if full_response:
            response_placeholder.markdown(full_response)
        else:
            response_placeholder.error("No response received from the model")
        
        return full_response
    except requests.RequestException as e:
        error_message = f"API Error: {str(e)}"
        container.error(error_message)
        print(f"Request exception: {error_message}")
        return None
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        container.error(error_message)
        print(f"Unexpected exception: {error_message}")
        return None


def handle_ibm_watsonx_request(base_url, api_key, project_id, model_name, messages, container):
    """
    Handles requests to IBM Watson X API using the official SDK.
    
    Args:
        base_url: IBM Watson X API base URL (e.g., https://us-south.ml.cloud.ibm.com)
        api_key: IBM Cloud API key
        project_id: IBM Watson X project ID
        model_name: Name of the model to use
        messages: List of message dictionaries with 'role' and 'content'
        container: Streamlit container for displaying response
        
    Returns:
        str: Full response text, or None if error occurred
    """
    try:
        # Check if SDK is available
        if not IBM_SDK_AVAILABLE:
            container.error("IBM Watson X SDK not installed. Please install with: pip install ibm-watsonx-ai")
            return None
        
        # Validate required configuration
        if not api_key:
            container.error("IBM API key is required. Please set IBM_API_KEY in your .env file.")
            return None
        
        if not base_url:
            container.error("IBM Base URL is required. Please set IBM_BASE_URL in your .env file.")
            return None
        
        # Extract base URL (remove query parameters and path if present)
        # SDK expects just the base URL like: https://us-south.ml.cloud.ibm.com
        if "?" in base_url:
            base_url = base_url.split("?")[0]
        if "/ml/v1" in base_url:
            # Extract just the base domain
            base_url = base_url.split("/ml/v1")[0]
        
        # Ensure we have the correct base URL format
        if "ml.cloud.ibm.com" not in base_url and "cloud.ibm.com" in base_url:
            base_url = base_url.replace(".cloud.ibm.com", ".ml.cloud.ibm.com")
        
        if not project_id:
            container.error("IBM Project ID is required. Please set IBM_PROJECT_ID in your .env file.")
            return None
        
        # Determine the actual IBM model ID to use
        actual_model_id = Config.IBM_MODEL_ID if Config.IBM_MODEL_ID else model_name
        
        if not actual_model_id:
            container.error("IBM Model ID is required. Please set IBM_MODEL_ID in your .env file or ensure model_name is set.")
            return None
        
        # Convert messages to IBM Watson X chat format
        formatted_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Format message according to IBM Watson X chat API
            if role == "user":
                formatted_messages.append({
                    "role": "user",
                    "content": [{"type": "text", "text": content}]
                })
            elif role == "assistant":
                formatted_messages.append({
                    "role": "assistant",
                    "content": content
                })
            elif role == "system":
                formatted_messages.append({
                    "role": "system",
                    "content": content
                })
        
        # Initialize IBM Watson X client using SDK
        credentials = Credentials(url=base_url, api_key=api_key)
        client = APIClient(credentials=credentials, project_id=project_id)
        
        # Initialize ModelInference
        params = {"project_id": project_id, "max_tokens": 1000, "time_limit": 1000}
        model_inference = ModelInference(model_id=actual_model_id, params=params, client=client)
        
        response_placeholder = container.empty()
        response_placeholder.info("🔄 Processing request...")
        full_response = ""
        
        # Use the SDK's chat method
        try:
            # Try chat completion with SDK
            response = model_inference.chat(messages=formatted_messages, params=params)
            
            # Handle response - SDK may return different formats
            if hasattr(response, 'choices') and len(response.choices) > 0:
                choice = response.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    full_response = choice.message.content
                elif isinstance(choice, dict) and "message" in choice:
                    full_response = choice["message"].get("content", "")
            elif isinstance(response, dict):
                if "choices" in response and len(response["choices"]) > 0:
                    full_response = response["choices"][0].get("message", {}).get("content", "")
            
            if full_response:
                response_placeholder.markdown(full_response)
            else:
                container.error("Unexpected response format from IBM Watson X SDK")
                print(f"Response: {response}")
                return None
                
        except Exception as e:
            container.error(f"IBM Watson X SDK error: {str(e)}")
            print(f"SDK error details: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # Final update without cursor
        if full_response:
            response_placeholder.markdown(full_response)
        else:
            response_placeholder.error("No response received from IBM Watson X")
        
        return full_response
        
    except Exception as e:
        # Handle SDK and general exceptions
        error_type = type(e).__name__
        error_message = f"IBM Watson X Error ({error_type}): {str(e)}"
        
        # Provide helpful messages for common errors
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str or "authentication" in error_str:
            error_message = "IBM Authentication failed. Please check your API key and credentials."
        elif "403" in error_str or "forbidden" in error_str:
            error_message = "IBM Access forbidden. Please check your permissions and project_id."
        elif "404" in error_str or "not found" in error_str:
            error_message = f"IBM Endpoint Not Found (404).\n\n"
            error_message += "Common issues:\n"
            error_message += f"1. Check if the base URL is correct: {base_url}\n"
            error_message += "2. Verify the region (us-south, eu-gb, etc.) matches your IBM Cloud instance\n"
            error_message += "3. Ensure project_id is correct\n"
            error_message += "4. Verify model_id is correct\n"
        elif "400" in error_str or "bad request" in error_str:
            error_message = f"IBM Bad Request (400): {str(e)}\n\n"
            error_message += "Please check:\n"
            error_message += "1. Model ID format is correct\n"
            error_message += "2. Messages format is correct\n"
            error_message += "3. Project ID is valid\n"
        
        container.error(error_message)
        print(f"IBM Watson X error: {error_message}")
        import traceback
        traceback.print_exc()
        return None


def stream_response(messages, container, model_name):
    """
    This function handles the API request based on the model (hosted or local) and streams the response.
    
    To add support for a new endpoint:
    1. Update get_api_config() to return the new endpoint URL and key
    2. Add a condition here to handle the new endpoint
    3. Use handle_hosted_request() for OpenAI-compatible APIs
    4. Use handle_local_request() for Ollama-compatible APIs
    5. Or create a custom handler for unique API formats
    """
    base_url, api_key, project_id = get_api_config(model_name)

    if model_name.startswith("meta-llama/"):
        # OpenAI-compatible API
        client = OpenAI(api_key=api_key, base_url=base_url)
        return handle_hosted_request(client, model_name, messages, container)
    elif model_name == "llama3.1:8b":
        # Ollama-compatible API
        print("url:", base_url)
        print("model_name:", model_name)
        return handle_local_request(base_url, model_name, messages, container)
    elif model_name.startswith("ibm"):
        # IBM Watson X API with bearer token authentication
        return handle_ibm_watsonx_request(
            base_url, api_key, project_id, model_name, messages, container
        )
    else:
        raise ValueError("Unsupported model selected.")