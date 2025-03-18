from typing import TypedDict, List

class ContentGenerationState(TypedDict):
    trending_topics: List[str]  # List of trending AI topics
    selected_topic: str  # The topic selected by the user
    content: str  # The generated content
    review: str  # Review of the content
    iteration: int  # Current iteration of refinement
    max_iterations: int  # Maximum number of refinement iterations
    image_prompt: str  # Prompt for image generation
    image_url: str  # URL or path to the generated image
    html_content: str  # Final HTML content