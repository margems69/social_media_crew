import os
import json
import streamlit as st
from datetime import datetime, timedelta
import requests
from PIL import Image, ImageDraw, ImageFont

# Initialize session state for API key if not exists
if 'openrouter_api_key' not in st.session_state:
    st.session_state.openrouter_api_key = ""

# Default OpenRouter API URL
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Initialize Streamlit configuration
st.set_page_config(page_title="Social Media Content Generator", page_icon="📅", layout="wide")
st.title("📅 Social Media Content Generator")
st.markdown("Generate engaging social media content for your platform.")

# Model selection - Updated to include DeepSeek R1
available_models = {
    "Claude 3 Opus": "anthropic/claude-3-opus",
    "Claude 3 Sonnet": "anthropic/claude-3-sonnet",
    "GPT-4 Turbo": "openai/gpt-4-turbo-preview",
    "Llama 2 70B": "meta-llama/llama-2-70b-chat",
    "Mixtral 8x7B": "mistralai/mixtral-8x7b",
    "Deepseek R1": "deepseek-ai/deepseek-llm-7b-chat"  # Updated model identifier
}

# Sidebar configuration with API key input
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Key configuration section
    st.subheader("API Configuration")
    api_key_input = st.text_input(
        "OpenRouter API Key",
        value=st.session_state.openrouter_api_key,
        type="password",
        help="Enter your OpenRouter API key. Get one at https://openrouter.ai/keys"
    )
    
    # Save API key to session state when changed
    if api_key_input != st.session_state.openrouter_api_key:
        st.session_state.openrouter_api_key = api_key_input
    
    # Model and content settings
    st.subheader("Content Settings")
    selected_model = st.selectbox(
        "Select Model",
        list(available_models.keys()),
        index=list(available_models.keys()).index("Deepseek R1"),  # Set DeepSeek R1 as default
        help="Choose the AI model to use"
    )
    
    # Rest of the code remains the same...
    custom_prompt = st.text_area(
        "Custom Prompt",
        value="Create engaging social media posts for a tech startup.",
        help="Customize the prompt for content generation."
    )
    platform = st.selectbox(
        "Platform",
        ["LinkedIn", "Twitter", "Instagram", "Facebook"],
        help="Select the target social media platform"
    )
    border_color = st.color_picker("Border Color", "#FF5733")
    background_color = st.color_picker("Background Color", "#000000")
    background_opacity = st.slider("Background Opacity", 0.0, 1.0, 0.5)
    num_posts = st.slider("Number of Posts", 1, 14, 7)

def call_openrouter_api(messages, model_name):
    """Make API call to OpenRouter."""
    if not st.session_state.openrouter_api_key:
        raise Exception("Please enter your OpenRouter API key in the sidebar settings.")
        
    headers = {
        "Authorization": f"Bearer {st.session_state.openrouter_api_key}",
        "HTTP-Referer": "https://localhost:8501",
        "X-Title": "Social Media Content Generator",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": available_models[model_name],
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = f"API error: {str(e)}"
        if hasattr(e.response, 'json'):
            try:
                error_data = e.response.json()
                error_msg = f"API error: {error_data.get('error', {}).get('message', str(e))}"
            except:
                pass
        raise Exception(error_msg)

# Rest of the functions (generate_content, create_csv) and main application logic remain the same...