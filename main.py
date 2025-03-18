from dotenv import load_dotenv, find_dotenv
from langchain_community.tools import TavilySearchResults
from langchain_openai import ChatOpenAI
from openai import OpenAI

from agent.config import LLM_MODEL, MAX_SEARCH_RESULTS
from agent.graph_builder import build_content_generation_graph, run_content_generation_workflow

# Load environment variables
load_dotenv(find_dotenv())

# Initialize the LLM
llm = ChatOpenAI(model_name=LLM_MODEL)

# Initialize OpenAI client for image generation
client = OpenAI()

# Initialize search tool
tavily_search = TavilySearchResults(max_results=MAX_SEARCH_RESULTS)


def main():
    # Build the graph
    graph = build_content_generation_graph()

    # Run the workflow
    run_content_generation_workflow(graph)


if __name__ == "__main__":
    main()