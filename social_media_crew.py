import os
import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv
from crewai import Agent, Task, Crew

# Load environment variables
load_dotenv()

# Custom CSS styling
st.markdown("""
<style>
.generated-post {
    border: 2px solid #e0e0e0;
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
    background: white;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}
.generated-post:hover {
    transform: translateY(-2px);
}
.download-btn {
    background: #4CAF50 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

class DeepseekManager:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
    
    def generate_content(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-1.3b-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None

def main():
    st.title("📱 AI Social Media Manager")
    st.subheader("Generate Engaging Content with Deepseek")
    
    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Settings")
        topic = st.text_input("Main Topic", placeholder="AI in Healthcare")
        num_posts = st.slider("Number of Posts", 1, 10, 5)
        default_prompt = "Create a social media post about {topic} that is engaging and under 280 characters."
        custom_prompt = st.text_area("Prompt Template", value=default_prompt, height=100)
    
    # Main content
    if st.button("Generate Posts"):
        if not topic:
            st.warning("Please enter a topic!")
        else:
            with st.spinner("Generating content..."):
                # Initialize components
                manager = DeepseekManager()
                agent = Agent(
                    role="Social Media Expert",
                    goal="Create viral content",
                    backstory="Expert in digital marketing",
                    verbose=True
                )
                
                # Generate content
                final_prompt = custom_prompt.format(topic=topic)
                task = Task(
                    description=f"Create {num_posts} posts about {topic}",
                    expected_output=f"{num_posts} social media posts",
                    agent=agent
                )
                
                crew = Crew(agents=[agent], tasks=[task])
                result = crew.kickoff()
                
                # Process and display results
                if result:
                    posts = [p.strip() for p in result.split("\n") if p.strip()]
                    df = pd.DataFrame({
                        "Post": posts,
                        "Length": [len(p) for p in posts]
                    })
                    
                    # Display posts
                    for idx, post in enumerate(posts, 1):
                        st.markdown(f"""
                        <div class="generated-post">
                            <h4>Post #{idx}</h4>
                            <p>{post}</p>
                            <small>Characters: {len(post)}</small>
                        </div>
                        """, unsafe_allow_html=True)import os
import json
import streamlit as st
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from PIL import Image, ImageDraw, ImageFont

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Streamlit UI Configuration
st.set_page_config(
    page_title="Social Media Content Generator",
    page_icon="📅",
    layout="wide"
)
st.title("📅 Social Media Content Generator")
st.markdown("Generate engaging social media content through a multi-agent pipeline that includes research, writing, hashtag generation, and final QA output as a downloadable spreadsheet.")

# Sidebar for user inputs
with st.sidebar:
    st.header("⚙️ Settings")
    custom_prompt = st.text_area(
        "Custom Prompt",
        value="Create engaging social media posts for a tech startup.",
        help="Customize the prompt for the AI agent."
    )
    border_color = st.color_picker("Border Color", "#FF5733")
    overlay_color = st.color_picker("Overlay Color", "#00000080")
    num_posts = st.slider("Number of Posts", 1, 14, 7)

# Initialize CrewAI with a chain of agents
class SocialMediaCrew:
    def __init__(self):
        self.deepseek = ChatOpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat"
        )

    def create_agents(self):
        return [
            Agent(
                role='Research Specialist',
                goal='Conduct comprehensive research on social media trends, competitor analysis, and audience behavior to gather insights for content creation.',
                backstory="""A detail-oriented researcher with deep expertise in social media analytics and market trends, capable of synthesizing vast amounts of data.""",
                verbose=True,
                llm=self.deepseek
            ),
            Agent(
                role='Content Writer',
                goal='Craft engaging social media posts based on research insights, ensuring the tone aligns with the brand voice and platform best practices.',
                backstory="""An experienced writer with a knack for turning data-driven insights into compelling narratives tailored for various social media platforms.""",
                verbose=True,
                llm=self.deepseek
            ),
            Agent(
                role='Hashtag Generator',
                goal='Generate trending and relevant hashtags that boost visibility and engagement on social media platforms.',
                backstory="""An expert in social media trends, adept at identifying the most effective hashtags for maximum reach and engagement.""",
                verbose=True,
                llm=self.deepseek
            ),
            Agent(
                role='QA Specialist',
                goal='Review and finalize the content generated by previous agents. Ensure quality, consistency, and prepare a final output in spreadsheet (CSV) format.',
                backstory="""A meticulous QA professional with years of experience in content verification and data formatting for social media strategies.""",
                verbose=True,
                llm=self.deepseek
            )
        ]

    def create_tasks(self, custom_prompt, num_posts):
        dates = [datetime.now() + timedelta(days=i) for i in range(num_posts)]
        return [
            Task(
                description=f"""Conduct in-depth research for a {num_posts}-day social media content strategy.
Analyze current trends, competitor activities, and audience preferences.
Custom Prompt: {custom_prompt}""",
                agent=self.agents[0],
                expected_output="Research report with insights and data for content creation."
            ),
            Task(
                description=f"""Based on the research report, craft {num_posts} engaging social media posts for Facebook and Instagram.
Include content themes, calls-to-action, and platform-specific nuances.
Posting Dates: {[d.strftime('%Y-%m-%d') for d in dates]}
Custom Prompt: {custom_prompt}""",
                agent=self.agents[1],
                expected_output="JSON array of post objects with date, platform, content, and visual cues."
            ),
            Task(
                description=f"""Generate trending and relevant hashtags for the generated posts.
Ensure hashtags are optimized for both Facebook and Instagram.
Custom Prompt: {custom_prompt}""",
                agent=self.agents[2],
                expected_output="List of trending hashtags for each platform."
            ),
            Task(
                description=f"""Review and finalize the generated social media posts and hashtags.
Format the final output into a spreadsheet (CSV format) including columns: Date, Platform, Content, Hashtags.
Custom Prompt: {custom_prompt}""",
                agent=self.agents[3],
                expected_output="Final CSV data as a string representing the spreadsheet content."
            )
        ]

    def run(self, custom_prompt, num_posts):
        self.agents = self.create_agents()
        self.tasks = self.create_tasks(custom_prompt, num_posts)

        crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=2,
            process=Process.sequential
        )

        result = crew.kickoff()
        return result

# Function to add border and overlay to an image (if needed)
def add_border_and_overlay(image_path, border_color, overlay_color):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # Add border
    border_width = 10
    draw.rectangle([(0, 0), (width, height)], outline=border_color, width=border_width)

    # Add overlay
    overlay = Image.new("RGBA", image.size, overlay_color)
    image = Image.alpha_composite(image.convert("RGBA"), overlay)

    return image

# Main Streamlit App
def main():
    if st.button("Generate Content"):
        with st.spinner("Generating content..."):
            social_media_crew = SocialMediaCrew()
            result = social_media_crew.run(custom_prompt, num_posts)

            st.success("Content generated successfully!")
            st.subheader("Generated Content")

            # Assuming Crew returns a dict keyed by agent roles:
            research_output = result.get("Research Specialist", "No research report generated.")
            writer_output = result.get("Content Writer", "No content generated.")
            hashtag_output = result.get("Hashtag Generator", "No hashtags generated.")
            final_csv = result.get("QA Specialist", "")

            st.markdown("### Research Report")
            st.write(research_output)
            st.divider()

            st.markdown("### Generated Social Media Posts")
            st.write(writer_output)
            st.divider()

            st.markdown("### Generated Hashtags")
            st.write(hashtag_output)
            st.divider()

            if final_csv:
                st.markdown("### Finalized Content Spreadsheet (CSV)")
                st.download_button(
                    label="Download Spreadsheet (CSV)",
                    data=final_csv,
                    file_name="social_media_content.csv",
                    mime="text/csv"
                )
            else:
                st.write("No final spreadsheet generated.")

if __name__ == "__main__":
    main()

                    
                    # Download button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="social_posts.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

if __name__ == "__main__":
    main()