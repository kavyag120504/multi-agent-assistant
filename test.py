from agents.orchestrator_agent import run_assistant

response, intent = run_assistant("What are my upcoming events?")
print(response)