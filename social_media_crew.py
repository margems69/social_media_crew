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

# Model selection
available_models = {
    "Claude 3 Opus": "anthropic/claude-3-opus",
    "Claude 3 Sonnet": "anthropic/claude-3-sonnet",
    "GPT-4 Turbo": "openai/gpt-4-turbo-preview",
    "Llama 2 70B": "meta-llama/llama-2-70b-chat",
    "Mixtral 8x7B": "mistralai/mixtral-8x7b",
    "Deepseek R1 Distil": "deepseek-ai/deepseek-llm-7b-chat"
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
        help="Choose the AI model to use"
    )
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

def generate_content(prompt, platform, num_posts, model_name):
    """Generate social media content using OpenRouter API."""
    dates = [datetime.now() + timedelta(days=i) for i in range(num_posts)]
    date_strings = [d.strftime('%Y-%m-%d') for d in dates]
    
    system_prompt = f"""You are a professional social media content creator. 
    Create {num_posts} engaging {platform} posts based on this prompt: {prompt}
    
    For each post, provide:
    1. Post content (appropriate length for {platform})
    2. Best posting time
    3. 3-5 relevant hashtags
    4. Type of content (text, image, video, poll, etc.)
    
    Format the response as JSON with the following structure for each post:
    {{
        "date": "YYYY-MM-DD",
        "content": "post content",
        "time": "HH:MM",
        "hashtags": ["tag1", "tag2", "tag3"],
        "type": "content type"
    }}
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    try:
        response = call_openrouter_api(messages, model_name)
        content = response['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")
        return None

def create_csv(posts):
    """Convert posts to CSV format."""
    csv_content = "Date,Time,Content,Hashtags,Type\n"
    for post in posts:
        content = post['content'].replace(',', '\\,')
        hashtags = ' '.join(post['hashtags'])
        csv_content += f"{post['date']},{post['time']},{content},{hashtags},{post['type']}\n"
    return csv_content

# Main application logic
if st.button("Generate Content"):
    if not st.session_state.openrouter_api_key:
        st.error("Please enter your OpenRouter API key in the sidebar settings.")
    else:
        with st.spinner("Generating content..."):
            try:
                # Generate content
                posts = generate_content(custom_prompt, platform, num_posts, selected_model)
                
                if posts:
                    st.success("Content generated successfully!")
                    
                    # Display generated posts
                    st.subheader("Generated Posts")
                    for post in posts:
                        with st.expander(f"Post for {post['date']}"):
                            st.write("**Content:**")
                            st.write(post['content'])
                            st.write("**Best Time to Post:**", post['time'])
                            st.write("**Hashtags:**", ' '.join(post['hashtags']))
                            st.write("**Content Type:**", post['type'])
                    
                    # Create and offer CSV download
                    csv_data = create_csv(posts)
                    st.download_button(
                        label="Download Content Schedule (CSV)",
                        data=csv_data,
                        file_name=f"social_media_content_{platform.lower()}.csv",
                        mime="text/csv"
                    )
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")