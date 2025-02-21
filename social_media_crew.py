import os
import json
import streamlit as st
from datetime import datetime, timedelta
import requests
from PIL import Image, ImageDraw, ImageFont

# Initialize constants
OPENROUTER_API_KEY = "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"  # Your API key
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Helper functions
def call_openrouter_api(messages, model_name):
    """Make API call to OpenRouter."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "localhost:8501",
        "X-Title": "Social Media Content Generator",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    data = {
        "model": available_models[model_name],
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = f"API error: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_msg = f"API error: {error_data.get('error', {}).get('message', str(e))}"
            except:
                error_msg = f"API error: {e.response.text}"
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

# Page configuration
st.set_page_config(page_title="Social Media Content Generator", page_icon="📅", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton>button {
        width: 100%;
        height: 3rem;
        font-size: 1.2rem;
        margin-top: 2rem;
        background-color: #FF4B4B;
        color: white;
    }
    .stButton>button:hover { background-color: #FF2B2B; }
    .post-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_posts' not in st.session_state:
    st.session_state.generated_posts = None

# Header
st.title("📅 Social Media Content Generator")
st.markdown("""
    <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;'>
        Generate engaging social media content using AI models
    </div>
""", unsafe_allow_html=True)

# Available models
available_models = {
    "Deepseek R1": "deepseek-ai/deepseek-llm-7b-chat",
    "Claude 3 Opus": "anthropic/claude-3-opus",
    "GPT-4 Turbo": "openai/gpt-4-turbo-preview",
    "Mixtral 8x7B": "mistralai/mixtral-8x7b"
}

# Layout
left_col, right_col = st.columns([2, 1])

with right_col:
    st.markdown("""
        <div style='background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <h3>⚙️ Settings</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Settings
    selected_model = st.selectbox(
        "AI Model",
        list(available_models.keys()),
        index=0,
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
        help="How many posts to generate"
    )

with left_col:
    st.markdown("""
        <div style='background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <h3>📝 Content Creation</h3>
        </div>
    """, unsafe_allow_html=True)
    
    prompt = st.text_area(
        "What kind of content would you like to generate?",
        value="Create engaging social media posts for a tech startup.",
        height=100
    )
    
    if st.button("🚀 Generate Content"):
        with st.spinner("Generating your social media content..."):
            try:
                posts = generate_content(prompt, platform, num_posts, selected_model)
                if posts:
                    st.session_state.generated_posts = posts
                    st.success("✨ Content generated successfully!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    # Display generated content
    if st.session_state.generated_posts:
        tab1, tab2 = st.tabs(["📱 Posts", "📅 Calendar"])
        
        with tab1:
            for idx, post in enumerate(st.session_state.generated_posts):
                with st.container():
                    st.markdown(f"""
                        <div class='post-card'>
                            <h4>Post {idx + 1} - {post['date']}</h4>
                            <p><strong>📝 Content:</strong> {post['content']}</p>
                            <p><strong>⏰ Time:</strong> {post['time']}</p>
                            <p><strong>#️⃣ Hashtags:</strong> {' '.join(post['hashtags'])}</p>
                            <p><strong>📊 Type:</strong> {post['type']}</p>
                        </div>
                    """, unsafe_allow_html=True)
        
        with tab2:
            cols = st.columns(7)
            for i, post in enumerate(st.session_state.generated_posts):
                with cols[i % 7]:
                    st.markdown(f"""
                        <div style='background-color: white; padding: 0.5rem; border-radius: 0.5rem; margin-bottom: 0.5rem;'>
                            <small>{post['date']}<br>{post['time']}</small>
                        </div>
                    """, unsafe_allow_html=True)
        
        # Download options
        st.markdown("### 📥 Download Options")
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = create_csv(st.session_state.generated_posts)
            st.download_button(
                "📊 Download CSV",
                csv_data,
                f"social_media_content_{platform.lower()}.csv",
                "text/csv"
            )
        
        with col2:
            json_data = json.dumps(st.session_state.generated_posts, indent=2)
            st.download_button(
                "📋 Download JSON",
                json_data,
                f"social_media_content_{platform.lower()}.json",
                "application/json"
            )