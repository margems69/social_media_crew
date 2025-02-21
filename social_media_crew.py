from crewai import Agent, Task, Crew, Process
from langchain.tools import DuckDuckGoSearchRun
from datetime import datetime, timedelta
import json

class SocialMediaCrew:
    def __init__(self, api_key):
        self.search_tool = DuckDuckGoSearchRun()
        self.api_key = api_key

    def create_agents(self):
        """Create specialized agents for social media management"""
        
        content_strategist = Agent(
            role='Content Strategist',
            goal='Research and plan engaging social media content',
            backstory="""You are an experienced content strategist who understands
            social media trends and audience behavior.""",
            tools=[self.search_tool],
            verbose=True
        )

        copywriter = Agent(
            role='Caption & Copywriting Specialist',
            goal='Create engaging and converting social media copy',
            backstory="""You are a creative copywriter who specializes in
            social media content that drives engagement.""",
            verbose=True
        )

        seo_specialist = Agent(
            role='SEO & Hashtag Specialist',
            goal='Optimize content for maximum reach and engagement',
            backstory="""You are an SEO expert who knows how to maximize
            content visibility through strategic hashtag and keyword use.""",
            verbose=True
        )

        qa_agent = Agent(
            role='Quality Assurance Specialist',
            goal='Ensure content meets brand standards and quality guidelines',
            backstory="""You are a detail-oriented QA specialist who ensures
            all content is polished and error-free.""",
            verbose=True
        )

        scheduler = Agent(
            role='Content Scheduler',
            goal='Optimize post timing for maximum engagement',
            backstory="""You are a scheduling expert who knows the best
            times to post for different platforms and audiences.""",
            verbose=True
        )

        engagement_manager = Agent(
            role='Engagement & Community Manager',
            goal='Foster community engagement and interaction',
            backstory="""You are a community manager who excels at
            building relationships and driving engagement.""",
            verbose=True
        )

        analytics_specialist = Agent(
            role='Analytics & Reporting Specialist',
            goal='Track and analyze content performance',
            backstory="""You are a data analyst who specializes in
            social media metrics and performance optimization.""",
            verbose=True
        )

        return {
            'strategist': content_strategist,
            'copywriter': copywriter,
            'seo': seo_specialist,
            'qa': qa_agent,
            'scheduler': scheduler,
            'engagement': engagement_manager,
            'analytics': analytics_specialist
        }

    def create_tasks(self, agents, prompt, platform, num_posts):
        """Create sequential tasks for content creation workflow"""
        
        research_task = Task(
            description=f"""Research trending topics and content ideas for {platform} 
            related to: {prompt}. Suggest {num_posts} content ideas.""",
            agent=agents['strategist']
        )

        writing_task = Task(
            description="""Create engaging captions and copy for the suggested content ideas.
            Format should match platform requirements.""",
            agent=agents['copywriter']
        )

        seo_task = Task(
            description=f"""Optimize the content with relevant hashtags and keywords for {platform}.
            Provide 3-5 targeted hashtags per post.""",
            agent=agents['seo']
        )

        qa_task = Task(
            description="""Review all content for quality, accuracy, and brand consistency.
            Check grammar, tone, and messaging.""",
            agent=agents['qa']
        )

        scheduling_task = Task(
            description=f"""Determine optimal posting times for {num_posts} posts on {platform}.
            Consider timezone and audience activity patterns.""",
            agent=agents['scheduler']
        )

        analytics_task = Task(
            description="""Create a preliminary performance prediction and measurement plan
            for the content. Include KPIs and success metrics.""",
            agent=agents['analytics']
        )

        return [research_task, writing_task, seo_task, qa_task, scheduling_task, analytics_task]

    def generate_content(self, prompt, platform, num_posts):
        """Execute the content generation workflow using Crew AI"""
        
        # Create agents and tasks
        agents = self.create_agents()
        tasks = self.create_tasks(agents, prompt, platform, num_posts)
        
        # Initialize and run the crew
        crew = Crew(
            agents=list(agents.values()),
            tasks=tasks,
            verbose=2,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        
        # Parse and format results
        try:
            posts = self._format_results(result, num_posts)
            return posts
        except Exception as e:
            raise Exception(f"Error formatting results: {str(e)}")

    def _format_results(self, crew_result, num_posts):
        """Format crew results into structured post data"""
        
        # Generate dates for posts
        dates = [datetime.now() + timedelta(days=i) for i in range(num_posts)]
        date_strings = [d.strftime('%Y-%m-%d') for d in dates]
        
        # Parse crew results and create structured posts
        posts = []
        
        # Extract content, hashtags, and times from crew results
        content_lines = crew_result.split('\n')
        current_post = {}
        
        for i in range(num_posts):
            posts.append({
                'date': date_strings[i],
                'content': content_lines[i] if i < len(content_lines) else "Content pending",
                'time': "09:00",  # Default time, should be replaced with scheduler agent output
                'hashtags': ["#placeholder"],  # Should be replaced with SEO agent output
                'type': "text"  # Default type
            })
        
        return posts

# Integration with existing Streamlit app
def initialize_crew(api_key):
    return SocialMediaCrew(api_key)

def generate_crew_content(crew, prompt, platform, num_posts):
    try:
        return crew.generate_content(prompt, platform, num_posts)
    except Exception as e:
        raise Exception(f"Error generating content with Crew AI: {str(e)}")