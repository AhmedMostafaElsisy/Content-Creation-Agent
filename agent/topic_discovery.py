import datetime

from langchain_core.messages import HumanMessage, SystemMessage
from agent.state import ContentGenerationState


def discover_trending_topics(state: ContentGenerationState):
    """Search for trending AI topics and return a list."""
    # Import LLM and search tool here to avoid circular imports
    from main import llm, tavily_search

    # Use Tavily to search for trending AI topics
    search_results = tavily_search.invoke(f"latest trending topics in artificial intelligence and GenAI ${datetime.datetime.now().year}")

    # Process the search results to extract trending topics
    system_message = """
    You are an AI expert who can identify trending topics in artificial intelligence.
    Based on the search results provided, identify 5 distinct trending topics in LLM.
    Each topic should be specific enough for a focused blog post.
    Format your response as a numbered list from 1 to 5.
    """

    # Extract trending topics using LLM
    topics_response = llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content=f"Search results about trending LLM topics: {search_results}")
    ])

    # Extract the list of topics from the LLM response
    topics_text = topics_response.content

    # Parse the numbered list
    topics = []
    for line in topics_text.split('\n'):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("- ")):
            # Remove numbering or bullet points
            topic = line.split('.', 1)[1].strip() if '.' in line else line.replace("- ", "", 1).strip()
            topics.append(topic)

    # Ensure we have topics
    if not topics:
        topics = ["AI in healthcare", "Large Language Models advancements",
                  "Ethical considerations in AI", "AI for climate change",
                  "Multimodal AI models"]

    return {"trending_topics": topics}


def human_topic_selection(state: ContentGenerationState):
    """A no-op function that will be interrupted for human input."""
    pass