from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

def get_news(user_message, context: str = ""):
    from tools.llm_client import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return "❌ `TAVILY_API_KEY` is missing from your `.env` file. Please add it and restart."

    try:
        client       = TavilyClient(api_key=api_key)
        llm          = get_llm()
        context_hint = f"\nConversation so far:\n{context}\n" if context else ""

        # ── Extract topic ────────────────────────────────────────────────────
        topic_messages = [
            SystemMessage(content=f"""
            Extract the news topic from the user message.
            Respond with just the topic, nothing else.
            If no topic is found but the conversation history mentions one, use that topic.
            If still unknown, respond with: UNKNOWN
            {context_hint}
            Examples:
            "What is the latest news about AI?" -> AI
            "Tell me recent cricket news"       -> cricket
            "More on that topic"  (with AI in history) -> AI
            """),
            HumanMessage(content=user_message)
        ]
        topic = llm.invoke(topic_messages).content.strip()

        if not topic or topic.upper() == "UNKNOWN":
            return "❓ I couldn't find a topic in your message. Try: *\"Latest news on AI\"* or *\"Cricket news\"*"

        # ── Detect result count ──────────────────────────────────────────────
        count_messages = [
            SystemMessage(content="""
            Does the user want more than 3 news results?
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

        # ── Fetch news ───────────────────────────────────────────────────────
        response = client.search(
            query=f"latest news {topic}",
            max_results=max_results,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=False,
        )

        results    = response.get("results", [])
        ai_summary = response.get("answer", "")

        if not results:
            return f"🔍 No news found for **{topic}**. Try a different keyword."

        output = f"📰 **Latest News: {topic}**\n\n"

        if ai_summary:
            output += f"🧠 **Summary:** {ai_summary[:300]}{'...' if len(ai_summary) > 300 else ''}\n\n"
            output += "─" * 40 + "\n\n"

        for i, result in enumerate(results, 1):
            title     = result.get("title", "No title")
            url       = result.get("url", "")
            content   = result.get("content", "")[:180]
            published = result.get("published_date", "")

            output += f"**{i}. {title}**\n"
            if published:
                output += f"   🕐 {published[:10]}\n"
            output += f"   {content}...\n"
            output += f"   🔗 [Read more]({url})\n\n"

        return output

    except Exception as e:
        err = str(e).lower()
        if "401" in err or "unauthorized" in err or "invalid api" in err:
            return "❌ Invalid Tavily API key. Please check your `.env` file."
        if "429" in err or "rate limit" in err:
            return "⚠️ News API rate limit reached. Please wait a moment and try again."
        if "connection" in err or "network" in err:
            return "🌐 No internet connection. Please check your network and try again."
        return f"⚠️ Error fetching news: {str(e)}"
