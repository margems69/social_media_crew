import os
import json
import streamlit as st
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew, Process
import openai
from PIL import Image, ImageDraw, ImageFont

# Set OpenAI API key
openai.api_key = "your-api-key-here"

# Initialize Streamlit configuration
st.set_page_config(page_title="Social Media Content Generator", page_icon="📅", layout="wide")
st.title("📅 Social Media Content Generator")
st.markdown("Generate engaging social media content through a multi-agent pipeline.")

# Sidebar configuration
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

class SocialMediaCrew:
    def __init__(self):
        # Simple OpenAI wrapper class
        class SimpleGPT:
            def invoke(self, prompt):
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                return response.choices[0].message.content

        self.llm = SimpleGPT()
        self.agents = None
        self.tasks = None

    def create_agents(self):
        return [
            Agent(
                role='Research Specialist',
                goal='Conduct comprehensive research on social media trends and analysis.',
                backstory="A detail-oriented researcher with expertise in social media analytics.",
                verbose=True,
                llm=self.llm
            ),
            Agent(
                role='Content Writer',
                goal='Craft engaging social media posts based on research insights.',
                backstory="An experienced writer specializing in social media content.",
                verbose=True,
                llm=self.llm
            ),
            Agent(
                role='Hashtag Generator',
                goal='Generate trending and relevant hashtags for social platforms.',
                backstory="An expert in social media trends and hashtag optimization.",
                verbose=True,
                llm=self.llm
            ),
            Agent(
                role='QA Specialist',
                goal='Review and finalize the content for quality and consistency.',
                backstory="A meticulous QA professional with content verification expertise.",
                verbose=True,
                llm=self.llm
            )
        ]

    def create_tasks(self, custom_prompt, num_posts):
        dates = [datetime.now() + timedelta(days=i) for i in range(num_posts)]
        date_strings = [d.strftime('%Y-%m-%d') for d in dates]
        
        tasks = [
            Task(
                description=f"Research {num_posts}-day social media strategy. Prompt: {custom_prompt}",
                agent=self.agents[0],
                expected_output="Research report with insights"
            ),
            Task(
                description=f"Create {num_posts} posts for dates: {date_strings}. Prompt: {custom_prompt}",
                agent=self.agents[1],
                expected_output="JSON array of posts"
            ),
            Task(
                description=f"Generate hashtags for posts. Prompt: {custom_prompt}",
                agent=self.agents[2],
                expected_output="List of hashtags"
            ),
            Task(
                description=f"Review and create final CSV. Prompt: {custom_prompt}",
                agent=self.agents[3],
                expected_output="CSV data string"
            )
        ]
        return tasks

    def run(self, custom_prompt, num_posts):
        self.agents = self.create_agents()
        self.tasks = self.create_tasks(custom_prompt, num_posts)
        
        crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=2,
            process=Process.sequential
        )
        
        return crew.kickoff()

# Main application logic
if st.button("Generate Content"):
    if not openai.api_key.startswith("sk-"):
        st.error("Please enter a valid OpenAI API key!")
    else:
        with st.spinner("Generating content..."):
            try:
                social_media_crew = SocialMediaCrew()
                result = social_media_crew.run(custom_prompt, num_posts)
                
                st.success("Content generated successfully!")
                st.subheader("Generated Content")
                
                # Display results
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
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")