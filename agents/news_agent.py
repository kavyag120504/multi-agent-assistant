from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

def get_news(user_message):
    api_key = os.getenv("TAVILY_API_KEY")
    client = TavilyClient(api_key=api_key)
    
    from tools.llm_client import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage
    
    llm = get_llm()
    messages = [
        SystemMessage(content="""
        Extract the news topic from the user message.
        Respond with just the topic, nothing else.
        Examples:
        "What is the latest news about AI?" -> AI news
        "Tell me recent cricket news" -> cricket news
        """),
        HumanMessage(content=user_message)
    ]
    
    topic = llm.invoke(messages).content.strip()
    
    response = client.search(
        query=f"latest news {topic}",
        max_results=3,
        search_depth="advanced"
    )
    
    results = response.get("results", [])
    
    if not results:
        return f"Sorry, I couldn't find any news about {topic}."
    
    output = f"📰 Latest news on: **{topic}**\n\n"
    for i, result in enumerate(results, 1):
        title = result.get("title", "No title")
        url = result.get("url", "")
        content = result.get("content", "")[:120]
        output += f"{i}. **{title}**\n"
        output += f"   {content}...\n"
        output += f"   🔗 {url}\n\n"
    
    return output