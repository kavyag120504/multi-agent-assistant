from agents.orchestrator_agent import run_assistant

tests = [
    "What is the weather in Delhi?",
    "Tell me latest AI news",
    "What is 15 multiplied by 8?",
    "Search for Python tutorials",
]

for query in tests:
    print(f"\nQ: {query}")
    response, intent = run_assistant(query)
    print(f"Intent: {intent}")
    print(f"A: {response[:150]}")
    print("-" * 50)