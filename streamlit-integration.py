# Add these imports at the top of your Streamlit app
from crew_integration import SocialMediaCrew, initialize_crew, generate_crew_content

# Add this after your existing constants
CREW_API_KEY = "your-crew-ai-api-key"  # Replace with your actual API key

# Initialize Crew AI in session state
if 'crew' not in st.session_state:
    st.session_state.crew = initialize_crew(CREW_API_KEY)

# Modify the sidebar to add Crew AI option
with right_col:
    generation_method = st.radio(
        "Content Generation Method",
        ["OpenRouter", "Crew AI"],
        help="Choose whether to use OpenRouter or Crew AI for content generation"
    )

# Modify the generate button logic
if st.button("🚀 Generate Content"):
    with st.spinner("Generating your social media content..."):
        try:
            if generation_method == "OpenRouter":
                posts = generate_content(prompt, platform, num_posts, selected_model)
            else:
                posts = generate_crew_content(st.session_state.crew, prompt, platform, num_posts)
                
            if posts:
                st.session_state.generated_posts = posts
                st.success("✨ Content generated successfully!")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
