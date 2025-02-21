import os
import json
import streamlit as st
from datetime import datetime, timedelta
import requests
from PIL import Image, ImageDraw, ImageFont

# Deepinfra API Configuration
DEEPINFRA_API_KEY = "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"
DEEPINFRA_API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"

# Initialize Streamlit configuration
st.set_page_config(page_title="Social Media Content Generator", page_icon="📅", layout="wide")
st.title("📅 Social Media Content Generator")
st.markdown("Generate engaging social media content for your platform.")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Settings")
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

def call_deepinfra_api(messages):
    """Make API call to Deepinfra."""
    headers = {
        "Authorization": f"Bearer {DEEPINFRA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "meta-llama/Llama-2-70b-chat-hf",  # Using Llama 2 model
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    response = None
    try:
        response = requests.post(DEEPINFRA_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_msg = ""
        if response is not None:
            if response.status_code == 401:
                error_msg = "API key authentication failed. Please check your API key."
            elif response.status_code == 404:
                error_msg = "Invalid API endpoint. Please check the API URL."
            else:
                try:
                    error_data = response.json()
                    error_msg = f"API error: {error_data.get('error', {}).get('message', str(e))}"
                except:
                    error_msg = f"HTTP error occurred: {str(e)}"
        else:
            error_msg = f"Failed to get response from API: {str(e)}"
        raise Exception(error_msg)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")

def generate_content(prompt, platform, num_posts):
    """Generate social media content using Deepinfra API."""
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
        response = call_deepinfra_api(messages)
        content = response['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")
        return None

def create_csv(posts):
    """Convert posts to CSV format."""
    csv_content = "Date,Time,Content,Hashtags,Type\n"
    for post in posts:
        # Escape any commas in the content
        content = post['content'].replace(',', '\\,')
        hashtags = ' '.join(post['hashtags'])
        csv_content += f"{post['date']},{post['time']},{content},{hashtags},{post['type']}\n"
    return csv_content

# Main application logic
if st.button("Generate Content"):
    with st.spinner("Generating content..."):
        try:
            # Generate content
            posts = generate_content(custom_prompt, platform, num_posts)
            
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