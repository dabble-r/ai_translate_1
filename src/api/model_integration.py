import requests
import json
from openai import OpenAI
from config.config import Config


def get_api_config(model_name):
    
    """
    Get API base URL and API key based on the model name.
    """
    if model_name.startswith("meta-llama/"):
        return Config.HOSTED_BASE_URL, Config.HOSTED_API_KEY
    elif model_name == "llama3.1:8b":
        print("local model selected")
        return Config.LOCAL_BASE_URL, None
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


def stream_response(messages, container, model_name):
    """
    This function handles the API request based on the model (hosted or local) and streams the response.
    """
    base_url, api_key = get_api_config(model_name)

    if model_name.startswith("meta-llama/"):
        client = OpenAI(api_key=api_key, base_url=base_url)
        return handle_hosted_request(client, model_name, messages, container)
    elif model_name == "llama3.1:8b":
        print("url:", base_url)
        print("model_name:", model_name)
        return handle_local_request(base_url, model_name, messages, container)
    else:
        raise ValueError("Unsupported model selected.")