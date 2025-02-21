import os
import json
import streamlit as st
from datetime import datetime, timedelta
import requests
from PIL import Image, ImageDraw, ImageFont

# Helper functions defined at the top
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
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
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

# Page configuration with custom theme
st.set_page_config(page_title="Social Media Content Generator", page_icon="📅", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        height: 3rem;
        font-size: 1.2rem;
        margin-top: 2rem;
        background-color: #FF4B4B;
        color: white;
    }
    .stButton>button:hover {
        background-color: #FF2B2B;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #DFF0D8;
        border: 1px solid #D6E9C6;
        color: #3C763D;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'openrouter_api_key' not in st.session_state:
    st.session_state.openrouter_api_key = ""
if 'generated_posts' not in st.session_state:
    st.session_state.generated_posts = None

# Header section with better styling
st.title("📅 Social Media Content Generator")
st.markdown("""
    <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;'>
        Generate engaging social media content for your platform using advanced AI models.
    </div>
""", unsafe_allow_html=True)

# Available models configuration
available_models = {
    "Claude 3 Opus": "anthropic/claude-3-opus",
    "Claude 3 Sonnet": "anthropic/claude-3-sonnet",
    "GPT-4 Turbo": "openai/gpt-4-turbo-preview",
    "Llama 2 70B": "meta-llama/llama-2-70b-chat",
    "Mixtral 8x7B": "mistralai/mixtral-8x7b",
    "Deepseek R1": "deepseek-ai/deepseek-llm-7b-chat"
}

# Create two columns for main content and settings
main_col, settings_col = st.columns([2, 1])

with settings_col:
    st.markdown("""
        <div style='background-color: #ffffff; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <h2 style='color: #333333;'>⚙️ Settings</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # API Configuration
    st.subheader("🔑 API Configuration")
    api_key_input = st.text_input(
        "OpenRouter API Key",
        value=st.session_state.openrouter_api_key,
        type="password",
        help="Enter your OpenRouter API key"
    )
    if api_key_input != st.session_state.openrouter_api_key:
        st.session_state.openrouter_api_key = api_key_input

    # Model Settings
    st.subheader("🎯 Content Settings")
    selected_model = st.selectbox(
        "AI Model",
        list(available_models.keys()),
        index=list(available_models.keys()).index("Deepseek R1"),
        help="Choose the AI model to use"
    )
    
    platform = st.selectbox(
        "Platform",
        ["LinkedIn", "Twitter", "Instagram", "Facebook"],
        help="Select your target social media platform"
    )
    
    num_posts = st.slider(
        "Number of Posts",
        min_value=1,
        max_value=14,
        value=7,
        help="How many posts do you want to generate?"
    )

    # Visual Settings
    st.subheader("🎨 Visual Settings")
    theme_options = {
        "Professional": ("#0077B5", "#FFFFFF"),
        "Creative": ("#FF1493", "#FFF0F5"),
        "Modern": ("#000000", "#F8F9FA"),
        "Custom": (None, None)
    }
    
    selected_theme = st.selectbox("Theme", list(theme_options.keys()))
    if selected_theme == "Custom":
        border_color = st.color_picker("Border Color", "#FF5733")
        background_color = st.color_picker("Background Color", "#FFFFFF")
    else:
        border_color, background_color = theme_options[selected_theme]

with main_col:
    st.markdown("""
        <div style='background-color: #ffffff; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <h2 style='color: #333333;'>📝 Content Creation</h2>
        </div>
    """, unsafe_allow_html=True)
    
    custom_prompt = st.text_area(
        "What kind of content would you like to generate?",
        value="Create engaging social media posts for a tech startup.",
        height=100,
        help="Be specific about your content needs"
    )
    
    # Generate button with loading state
    if st.button("🚀 Generate Content", key="generate_button"):
        if not st.session_state.openrouter_api_key:
            st.error("⚠️ Please enter your OpenRouter API key in the settings panel")
        else:
            with st.spinner("🎨 Generating your social media content..."):
                try:
                    posts = generate_content(custom_prompt, platform, num_posts, selected_model)
                    if posts:
                        st.session_state.generated_posts = posts
                        st.success("✨ Content generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    # Display generated content if available
    if st.session_state.generated_posts:
        st.markdown("### 📊 Generated Content")
        
        # Create tabs for different views
        tab1, tab2 = st.tabs(["📱 Post View", "📅 Calendar View"])
        
        with tab1:
            for idx, post in enumerate(st.session_state.generated_posts):
                with st.container():
                    st.markdown(f"""
                        <div style='background-color: {background_color}; 
                             border-left: 5px solid {border_color}; 
                             padding: 1rem; 
                             margin: 1rem 0; 
                             border-radius: 0.5rem;'>
                            <h4>Post {idx + 1} - {post['date']}</h4>
                            <p><strong>📝 Content:</strong> {post['content']}</p>
                            <p><strong>⏰ Best Time:</strong> {post['time']}</p>
                            <p><strong>#️⃣ Hashtags:</strong> {' '.join(post['hashtags'])}</p>
                            <p><strong>📊 Type:</strong> {post['type']}</p>
                        </div>
                    """, unsafe_allow_html=True)
        
        with tab2:
            # Create a calendar view
            calendar_data = {}
            for post in st.session_state.generated_posts:
                date = datetime.strptime(post['date'], '%Y-%m-%d')
                calendar_data[date] = post
            
            # Display calendar grid
            st.markdown("### 📅 Content Calendar")
            cols = st.columns(7)
            for i, post in enumerate(st.session_state.generated_posts):
                with cols[i % 7]:
                    st.markdown(f"""
                        <div style='background-color: {background_color}; 
                             padding: 0.5rem; 
                             border-radius: 0.5rem; 
                             margin-bottom: 0.5rem;'>
                            <small>{post['date']}</small><br>
                            <small>{post['time']}</small>
                        </div>
                    """, unsafe_allow_html=True)
        
        # Download options
        st.markdown("### 📥 Download Options")
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = create_csv(st.session_state.generated_posts)
            st.download_button(
                label="📊 Download as CSV",
                data=csv_data,
                file_name=f"social_media_content_{platform.lower()}.csv",
                mime="text/csv"
            )
        
        with col2:
            json_data = json.dumps(st.session_state.generated_posts, indent=2)
            st.download_button(
                label="📋 Download as JSON",
                data=json_data,
                file_name=f"social_media_content_{platform.lower()}.json",
                mime="application/json"
            )