from tools.llm_client import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

_VALID_INTENTS = {
    "weather", "search", "email", "news",
    "calendar", "reminder", "todo", "code", "general"
}


def parse_intent(user_message: str) -> str:
    llm = get_llm()

    messages = [
        SystemMessage(content="""
        You are an intent classifier. Given a user message,
        respond with ONLY one of these words:
        - weather
        - search
        - email
        - news
        - calendar
        - reminder
        - todo
        - code
        - general

        Examples:
        "What is the weather in Delhi?"          -> weather
        "5 day forecast for Mumbai"              -> weather
        "Search for Python tutorials"            -> search
        "Send email to john@gmail.com"           -> email
        "Read my inbox"                          -> email
        "Reply to John's email"                  -> email
        "What did John say in his last email?"   -> email
        "What is the latest news about AI?"      -> news
        "Schedule a meeting tomorrow at 3pm"     -> calendar
        "What are my events today?"              -> calendar
        "Reschedule my 3pm meeting to 5pm"       -> calendar
        "Remind me to call John at 5pm"          -> reminder
        "Set a reminder to submit report by 3pm" -> reminder
        "Show my reminders"                      -> reminder
        "What reminders did I miss?"             -> reminder
        "Add task buy groceries"                 -> todo
        "Add high priority task call client"     -> todo
        "Show my pending tasks"                  -> todo
        "Show done tasks"                        -> todo
        "Complete task 3"                        -> todo
        "Delete task 5"                          -> todo
        "What tasks do I have?"                  -> todo
        "Run: print('hello world')"              -> code
        "Execute: for i in range(5): print(i)"  -> code
        "Write a fibonacci function and run it"  -> code
        "Run this code: x = [1,2,3]; print(sum(x))" -> code
        "What is 25 times 4?"                    -> general
        "Calculate sqrt(144)"                    -> general

        Respond with just the single word, nothing else.
        """),
        HumanMessage(content=user_message)
    ]

    response = llm.invoke(messages)
    intent   = response.content.strip().lower()

    # Validate — fall back to general if LLM returns something unexpected
    return intent if intent in _VALID_INTENTS else "general"
