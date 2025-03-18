from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph, END

from agent.state import ContentGenerationState
from agent.topic_discovery import discover_trending_topics, human_topic_selection
from agent.content_generation import generate_content, review_content, refine_content, should_continue_refinement
from agent.image_generation import generate_image
from agent.html_formatter import format_html
from agent.config import MAX_ITERATIONS


def build_content_generation_graph():
    """Build and return the content generation workflow graph."""

    # Initialize the graph
    builder = StateGraph(ContentGenerationState)

    # Add nodes
    builder.add_node("discover_trending_topics", discover_trending_topics)
    builder.add_node("human_topic_selection", human_topic_selection)
    builder.add_node("generate_content", generate_content)
    builder.add_node("review_content", review_content)
    builder.add_node("refine_content", refine_content)
    builder.add_node("generate_image", generate_image)
    builder.add_node("format_html", format_html)

    # Add edges
    builder.add_edge(START, "discover_trending_topics")
    builder.add_edge("discover_trending_topics", "human_topic_selection")
    builder.add_edge("human_topic_selection", "generate_content")
    builder.add_edge("generate_content", "review_content")
    builder.add_edge("review_content", "refine_content")
    builder.add_conditional_edges("refine_content", should_continue_refinement, ["review_content", "generate_image"])
    builder.add_edge("generate_image", "format_html")
    builder.add_edge("format_html", END)

    # Compile the graph
    memory = MemorySaver()
    graph = builder.compile(interrupt_before=["human_topic_selection"], checkpointer=memory)

    # Generate and save visualization
    png_data = graph.get_graph().draw_mermaid_png()
    with open("graph_visualization.png", "wb") as f:
        f.write(png_data)
    print("Graph saved to 'graph_visualization.png'")

    return graph


def run_content_generation_workflow(graph):
    """Execute the content generation workflow."""

    # Initialize thread for state tracking
    thread = {"configurable": {"thread_id": "content_generation_1"}}

    # Set initial state with max iterations
    initial_state = {"max_iterations": MAX_ITERATIONS}

    # Run the graph until the first interruption (for human topic selection)
    for event in graph.stream(initial_state, thread, stream_mode="values"):
        trending_topics = event.get('trending_topics', [])
        if trending_topics:
            print("Discovered Trending AI Topics:")
            for i, topic in enumerate(trending_topics, 1):
                print(f"{i}. {topic}")

    # Get state and check next node
    state = graph.get_state(thread)
    print("\nPlease select a topic (enter the number):")
    topic_num = int(input()) - 1

    # Update state with selected topic
    selected_topic = state.values["trending_topics"][topic_num]
    print(f"\nSelected topic: {selected_topic}")

    # Update the state as if from the human_topic_selection node
    graph.update_state(thread, {"selected_topic": selected_topic}, as_node="human_topic_selection")

    # Continue the graph execution
    for event in graph.stream(None, thread, stream_mode="updates"):
        node_name = next(iter(event.keys()))
        print(f"Processing: {node_name}")

        # For content generation and refinement, show progress
        if node_name == "generate_content":
            print("Generating initial content...")
        elif node_name == "review_content":
            state = graph.get_state(thread)
            iteration = state.values.get("iteration", 0)
            max_iterations = state.values.get("max_iterations", MAX_ITERATIONS)
            print(f"Reviewing content (iteration {iteration} of {max_iterations})...")
        elif node_name == "refine_content":
            print("Refining content based on review...")
        elif node_name == "generate_image":
            print("Generating image for the blog post...")
        elif node_name == "format_html":
            print("Formatting final HTML output...")

    # Get the final state
    final_state = graph.get_state(thread)

    # Print completion message and output location
    print("\nContent generation complete!")
    html_file = f"../output/blog.html"
    print(f"HTML output saved to: {html_file}")

    return final_state.values