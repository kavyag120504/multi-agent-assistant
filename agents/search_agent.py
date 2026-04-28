from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

def search_web(user_message):
    api_key = os.getenv("TAVILY_API_KEY")
    client = TavilyClient(api_key=api_key)
    
    # Extract search query from user message using LLM
    from tools.llm_client import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage
    
    llm = get_llm()
    messages = [
        SystemMessage(content="""
        Extract only the search query from the user message.
        Respond with just the search query, nothing else.
        Example: "Search for latest AI news" -> latest AI news
        Example: "Find me python tutorials" -> python tutorials
        """),
        HumanMessage(content=user_message)
    ]
    
    query = llm.invoke(messages).content.strip()
    
    # Call Tavily search
    response = client.search(
        query=query,
        max_results=3
    )
    
    results = response.get("results", [])
    
    if not results:
        return "Sorry, I couldn't find any results for your query."
    
    # Format results
    output = f"🔍 Search results for: **{query}**\n\n"
    for i, result in enumerate(results, 1):
        title = result.get("title", "No title")
        url = result.get("url", "")
        content = result.get("content", "")[:150]  # first 150 chars
        output += f"{i}. **{title}**\n"
        output += f"   {content}...\n"
        output += f"   🔗 {url}\n\n"
    
    return output