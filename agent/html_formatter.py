import os
import datetime
import time
import re

from langchain_core.messages import HumanMessage, SystemMessage
from agent.state import ContentGenerationState


def format_html(state: ContentGenerationState):
    """Format the content and image into an HTML page with a modern minimalistic style."""
    # Import LLM here to avoid circular imports
    from main import llm

    content = state["content"]
    image_url = state["image_url"]
    selected_topic = state["selected_topic"]

    # Generate HTML from the markdown content using LLM
    system_message = """
    You are an expert in converting markdown content to clean, semantic HTML.
    Convert the provided markdown content to HTML, maintaining all headers, paragraphs, lists, and formatting.
    Use proper HTML5 elements like <article>, <section>, <h1>-<h6>, <p>, <ul>, <ol>, <li>, <blockquote>, etc.
    Use <strong> for bold text and <em> for italic text.
    For code blocks, use <pre><code> tags.

    Return only the HTML content with no explanations or markdown.
    """

    html_response = llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content=f"Convert this markdown content to HTML:\n\n{content}")
    ])

    html_content = html_response.content

    # Remove ```html at the beginning if present
    html_content = re.sub(r'^```html\s*', '', html_content)

    # Remove ``` at the end if present
    html_content = re.sub(r'\s*```$', '', html_content)
    # Clean up the title for display
    display_title = selected_topic
    if display_title.startswith('**') and display_title.endswith('**'):
        display_title = display_title[2:-2]

    display_title= display_title.replace("**", "").strip()

    # Extract a short description for meta tags
    description_system = """
    Create a concise 1-2 sentence summary (maximum 160 characters) of the following article content.
    Return only the summary text with no additional formatting or explanation.
    """

    description_response = llm.invoke([
        SystemMessage(content=description_system),
        HumanMessage(content=f"Article content: {content}")
    ])

    meta_description = description_response.content

    # Get absolute paths for better reliability
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, "output")

    # Fix image URL to use proper relative path from HTML file to image
    if image_url.startswith("images/"):
        # Make relative from output to images directory
        image_path = f"../{image_url}"
    else:
        # For placeholder or external URLs
        image_path = image_url

    # Ultra-minimalistic HTML template
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{meta_description}">
    <title>{display_title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --text-color: #191919;
            --text-light: #5f5f5f;
            --link-color: #0366d6;
            --background: #ffffff;
            --code-background: #f8f9fa;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        html {{
            font-size: 18px;
        }}

        body {{
            font-family: 'Inter', -apple-system, system-ui, sans-serif;
            line-height: 1.65;
            color: var(--text-color);
            background: var(--background);
            font-weight: 400;
            max-width: 680px;
            margin: 0 auto;
            padding: 2rem 1.3rem;
        }}

        header {{
            margin: 5rem 0 4rem;
        }}

        .title {{
            font-size: 2.4rem;
            font-weight: 300;
            line-height: 1.2;
            letter-spacing: -0.03em;
            margin-bottom: 2rem;
        }}

        .featured-image {{
            width: 100%;
            margin: 2rem 0 4rem;
            border-radius: 4px;
        }}

        h1, h2, h3, h4, h5, h6 {{
            font-weight: 500;
            line-height: 1.25;
            margin-top: 3rem;
            margin-bottom: 1.5rem;
            letter-spacing: -0.02em;
        }}

        h1 {{ font-size: 2rem; }}
        h2 {{ font-size: 1.7rem; }}
        h3 {{ font-size: 1.4rem; }}
        h4 {{ font-size: 1.2rem; }}

        p {{
            margin-bottom: 1.65rem;
        }}

        a {{
            color: var(--link-color);
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        ul, ol {{
            padding-left: 1.7rem;
            margin-bottom: 1.7rem;
        }}

        li {{
            margin-bottom: 0.5rem;
        }}

        blockquote {{
            border-left: 3px solid #eaeaea;
            padding-left: 1.4rem;
            margin-left: 0;
            margin-right: 0;
            margin-bottom: 1.7rem;
            font-style: italic;
            color: var(--text-light);
        }}

        code {{
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 0.9em;
            padding: 0.2em 0.4em;
            background: var(--code-background);
            border-radius: 3px;
        }}

        pre {{
            background: var(--code-background);
            padding: 1.2rem;
            border-radius: 4px;
            overflow-x: auto;
            margin-bottom: 1.7rem;
        }}

        pre code {{
            background: none;
            padding: 0;
        }}

        hr {{
            height: 1px;
            background: #eaeaea;
            border: none;
            margin: 3rem 0;
        }}

        .meta {{
            color: var(--text-light);
            font-size: 0.9rem;
            margin-top: 4rem;
        }}

        footer {{
            margin-top: 5rem;
            color: var(--text-light);
            font-size: 0.9rem;
            text-align: center;
        }}

        @media (max-width: 600px) {{
            html {{
                font-size: 16px;
            }}

            .title {{
                font-size: 2rem;
            }}

            body {{
                padding: 1.5rem 1rem;
            }}

            header {{
                margin: 3rem 0 2rem;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1 class="title">{display_title}</h1>
    </header>

    <img src="{image_path}" alt="{display_title}" class="featured-image">

    <main>
        {html_content}
    </main>

    <hr>

    <div class="meta">
        Published on {datetime.datetime.now().strftime("%B %d, %Y")}
    </div>

    <footer>
        <p>Generated with AI</p>
    </footer>
</body>
</html>
"""

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the HTML to a file with absolute path
    filename = os.path.join(output_dir, f"blog_{time.time()}.html")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"HTML file successfully created at: {filename}")

    return {"html_content": html}