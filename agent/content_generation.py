import datetime

from langchain_core.messages import HumanMessage, SystemMessage
from agent.state import ContentGenerationState
from agent.config import MAX_ITERATIONS


def generate_content(state: ContentGenerationState):
    """Generate initial content based on the selected topic."""
    # Import LLM and search tool here to avoid circular imports
    from main import llm, tavily_search

    selected_topic = state["selected_topic"]

    # Use Tavily to get more information about the topic
    search_results = tavily_search.invoke(f"{selected_topic} latest developments and insights ${datetime.datetime.now().year}")

    # Generate content using LLM
    system_message = """
    You are an expert AI content creator. Your task is to write a well-structured, 
    informative, and engaging blog post on the provided AI topic.

    The blog post should:
    1. Start with an engaging introduction that explains the topic and its importance
    2. Include 3-4 main sections with relevant subheadings
    3. Incorporate the latest research, developments, and insights
    4. Include technical details where appropriate, making complex concepts accessible
    5. Conclude with future implications or next steps in this area

    Use the search results provided as a source of information.
    The final post should be approximately 800-1000 words.
    """

    content_response = llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content=f"Topic: {selected_topic}\n\nSearch results: {search_results}")
    ])

    # Create an image prompt based on the content
    image_prompt_system = """
    You are an expert at creating effective prompts for AI image generation systems.
    Based on the article content provided, create a concise, descriptive prompt (maximum 50 words)
    that would generate a relevant, visually appealing featured image for the article.

    Format your response as just the prompt text, with no additional explanations.
    """

    image_prompt_response = llm.invoke([
        SystemMessage(content=image_prompt_system),
        HumanMessage(content=f"Article content: {content_response.content}")
    ])

    return {
        "content": content_response.content,
        "iteration": 1,
        "image_prompt": image_prompt_response.content
    }


def review_content(state: ContentGenerationState):
    """Review the content and identify areas for improvement."""
    # Import LLM here to avoid circular imports
    from main import llm

    content = state["content"]
    iteration = state["iteration"]
    max_iterations = state.get("max_iterations", MAX_ITERATIONS)

    if iteration > max_iterations:
        # Skip review if we've reached max iterations
        return {"review": "Maximum iterations reached. Content finalized."}

    # Generate review using LLM
    system_message = """
    You are an expert AI content editor. Your task is to critically review the provided blog post 
    and identify specific areas for improvement.

    Evaluate the content on:
    1. Clarity and coherence - Is the information presented clearly and logically?
    2. Engagement - Is the content interesting and does it maintain reader attention?
    3. Accuracy - Is the technical information correct and up-to-date?
    4. Completeness - Are there any important aspects of the topic that are missing?
    5. Structure - Is the content well-organized with appropriate headings and flow?

    For each area where improvement is needed, provide:
    - Specific feedback about what could be improved
    - Concrete suggestions for how to improve it

    Format your review in bullet points for easy implementation.
    """

    review_response = llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content=f"Current iteration: {iteration} of {max_iterations}\n\nBlog post content:\n{content}")
    ])

    return {"review": review_response.content}


def refine_content(state: ContentGenerationState):
    """Refine the content based on the review."""
    # Import LLM here to avoid circular imports
    from main import llm

    content = state["content"]
    review = state["review"]
    iteration = state["iteration"]

    # Generate refined content using LLM
    system_message = """
    You are an expert AI content creator. Your task is to improve a blog post based on editorial feedback.

    Consider each point of feedback carefully and implement the suggested improvements while maintaining 
    the overall flow and style of the original content.

    The improved content should:
    1. Address all feedback points from the review
    2. Maintain or enhance the engaging and informative tone
    3. Keep the technical accuracy and depth
    4. Ensure proper structure with clear headings and logical flow

    Return the complete revised blog post.
    """

    refined_content_response = llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content=f"Original blog post:\n{content}\n\nEditorial feedback:\n{review}")
    ])

    return {
        "content": refined_content_response.content,
        "iteration": iteration + 1
    }


def should_continue_refinement(state: ContentGenerationState):
    """Decide whether to continue refining the content or generate an image."""
    iteration = state["iteration"]
    max_iterations = state.get("max_iterations", MAX_ITERATIONS)

    if iteration > max_iterations:
        return "generate_image"
    return "review_content"