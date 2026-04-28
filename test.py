from agents.orchestrator_agent import run_assistant

# Test all agents through orchestrator
print("--- Weather Test ---")
print(run_assistant("What is the weather in Mumbai?"))

print("\n--- Search Test ---")
print(run_assistant("Search for latest Python programming news"))

print("\n--- General Chat Test ---")
print(run_assistant("What is artificial intelligence?"))