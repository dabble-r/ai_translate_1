import os
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials
import streamlit as st

# Load environment variables
load_dotenv()


def get_watsonx_client(model_id, project_id=None):
    """
    Create and return a Watson X ModelInference client.
    
    Args:
        model_id: The model identifier (e.g., "meta-llama/llama-3-3-70b-instruct")
        project_id: Optional project ID (defaults to env variable)
        
    Returns:
        ModelInference: Configured client instance
    """
    api_key = os.getenv("IBM_API_KEY")
    base_url = os.getenv("IBM_BASE_URL")
    project_id = project_id or os.getenv("IBM_PROJECT_ID")
    
    # print("key: ", api_key)
    # print("base_url: ", base_url)
    # print("project_id: ", project_id)
    
    if not api_key or not base_url or not project_id:
        raise ValueError("Missing required environment variables: IBM_API_KEY, IBM_BASE_URL, IBM_PROJECT_ID")
    
    # Clean up base URL (remove query params and paths)
    if "?" in base_url:
        base_url = base_url.split("?")[0]
    if "/ml/v1" in base_url:
        base_url = base_url.split("/ml/v1")[0]
    
    creds = Credentials(
        api_key=api_key,
        url=base_url
    )

    return ModelInference(
        model_id=model_id,
        credentials=creds,
        project_id=project_id,
        params={
            "decoding_method": "greedy",
            "max_new_tokens": 200,
            "temperature": 0
        }
    )


def chat_with_watsonx(messages, model_id, container):
    """
    Send a chat request to Watson X and display the response.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        model_id: The model identifier to use
        container: Streamlit container for displaying response
        
    Returns:
        str: The response text, or None if error
    """
    try:
        # Show processing indicator
        response_placeholder = container.empty()
        response_placeholder.info("🔄 Processing request...")
        
        # Get client
        model = get_watsonx_client(model_id)
        
        # Format messages for Watson X chat API
        formatted_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
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
        
        # Call chat API
        response = model.chat(messages=formatted_messages)
        
        # Extract response content
        if hasattr(response, 'choices') and len(response.choices) > 0:
            choice = response.choices[0]
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                full_response = choice.message.content
            elif isinstance(choice, dict) and "message" in choice:
                full_response = choice["message"].get("content", "")
            else:
                full_response = str(choice)
        elif isinstance(response, dict):
            if "choices" in response and len(response["choices"]) > 0:
                full_response = response["choices"][0].get("message", {}).get("content", "")
            else:
                full_response = str(response)
        else:
            full_response = str(response)
        
        # Display response
        if full_response:
            response_placeholder.markdown(full_response)
            return full_response
        else:
            response_placeholder.error("No response received from Watson X")
            return None
            
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        container.error(error_msg)
        print(f"Watson X error: {error_msg}")
        import traceback
        traceback.print_exc()
        return None


def stream_response(messages, container, model_name):
    """
    Main entry point for streaming responses.
    Routes to Watson X chat.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        container: Streamlit container for displaying response
        model_name: Model identifier from dropdown
        
    Returns:
        str: Response text or None
    """
    # Determine actual model ID (check for override in env)
    actual_model_id = os.getenv("IBM_MODEL_ID") or model_name
    
    return chat_with_watsonx(messages, actual_model_id, container)
