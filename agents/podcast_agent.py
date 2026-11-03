from google.adk.agents import Agent
from tools.audio_tools import generate_podcast_audio

podcast_agent = Agent(
    name="podcast_producer_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a specialized Financial Audio Podcast Specialist. Your sole responsibility
    is to receive a structured dialogue script between Brenda (Bull analyst) and Sam (Bear skeptic)
    and convert it into a dual-speaker WAV audio file using the `generate_podcast_audio` tool.

    Required Workflow:
    1. Receive the debate script text.
    2. Immediately call `generate_podcast_audio` passing the complete conversation.
    3. Report the generated audio file path and status back to the coordinator.
    """,
    tools=[generate_podcast_audio]
)
