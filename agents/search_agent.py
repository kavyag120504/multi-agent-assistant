from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

def search_web(user_message, context: str = ""):
    from tools.llm_client import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return "❌ `TAVILY_API_KEY` is missing from your `.env` file. Please add it and restart."

    try:
        client       = TavilyClient(api_key=api_key)
        llm          = get_llm()
        context_hint = f"\nConversation so far:\n{context}\n" if context else ""

        # ── Extract search query ─────────────────────────────────────────────
        query_messages = [
            SystemMessage(content=f"""
            Extract only the search query from the user message.
            Respond with just the search query, nothing else.
            If no query is found but the conversation history has a relevant topic, use that.
            If still unknown, respond with: UNKNOWN
            {context_hint}
            Example: "Search for latest AI news"   -> latest AI news
            Example: "Find me python tutorials"    -> python tutorials
            Example: "Tell me more about it" (with LangChain in history) -> LangChain
            """),
            HumanMessage(content=user_message)
        ]
        query = llm.invoke(query_messages).content.strip()

        if not query or query.upper() == "UNKNOWN":
            return "❓ I couldn't find a search query. Try: *\"Search for Python tutorials\"*"

        # ── Detect result count ──────────────────────────────────────────────
        count_messages = [
            SystemMessage(content="""
            Does the user want more than 3 search results?
            If they say "more", "detailed", "top 5", "5 results", etc., respond: 5
            Otherwise respond: 3
            Respond with just the number.
            """),
            HumanMessage(content=user_message)
        ]
        try:
            max_results = int(llm.invoke(count_messages).content.strip())
            max_results = min(max(max_results, 3), 7)
        except Exception:
            max_results = 3

        # ── Perform search ───────────────────────────────────────────────────
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=False,
        )

        results   = response.get("results", [])
        ai_answer = response.get("answer", "")

        if not results:
            return f"🔍 No results found for **{query}**. Try rephrasing your search."

        output = f"🔍 **Search: {query}**\n\n"

        if ai_answer:
            output += f"💡 **Quick Answer:** {ai_answer[:350]}{'...' if len(ai_answer) > 350 else ''}\n\n"
            output += "─" * 40 + "\n\n"

        for i, result in enumerate(results, 1):
            title   = result.get("title", "No title")
            url     = result.get("url", "")
            content = result.get("content", "")[:200]
            score   = result.get("score", 0)

            relevance = "🟢" if score > 0.7 else "🟡" if score > 0.4 else "🔴"

            output += f"**{i}. {title}** {relevance}\n"
            output += f"   {content}...\n"
            output += f"   🔗 [Visit]({url})\n\n"

        return output

    except Exception as e:
        err = str(e).lower()
        if "401" in err or "unauthorized" in err or "invalid api" in err:
            return "❌ Invalid Tavily API key. Please check your `.env` file."
        if "429" in err or "rate limit" in err:
            return "⚠️ Search API rate limit reached. Please wait a moment and try again."
        if "connection" in err or "network" in err:
            return "🌐 No internet connection. Please check your network and try again."
        return f"⚠️ Error performing search: {str(e)}"
