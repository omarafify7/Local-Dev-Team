"""
Verify Ollama Integration with CrewAI

This script tests if CrewAI can successfully communicate with the 
local Ollama instance running qwen2.5-coder:14b.
"""
import win_patch  # Windows compatibility
from crewai import LLM, Agent, Task, Crew

print("="*50)
print("Testing CrewAI <-> Ollama Integration")
print("Model: qwen2.5-coder:14b")
print("="*50)

try:
    # 1. Setup LLM
    print("1. Initializing LLM Connection...")
    my_llm = LLM(
        model="ollama/qwen2.5-coder:14b",
        base_url="http://localhost:11434"
    )
    
    # 2. Create a simple agent
    print("2. Creating Test Agent...")
    test_agent = Agent(
        role="Test Agent",
        goal="Say hello",
        backstory="You are a test agent.",
        llm=my_llm,
        verbose=True
    )
    
    # 3. Define a trivial task
    print("3. Defining Task...")
    task = Task(
        description="Reply with exactly one word: 'Success'",
        expected_output="The word 'Success'",
        agent=test_agent
    )
    
    # 4. Run it
    print("4. Running Crew...")
    crew = Crew(agents=[test_agent], tasks=[task], verbose=True)
    result = crew.kickoff()
    
    print("\n" + "="*50)
    print(f"RESULT: {result}")
    print("="*50)
    
    if "Success" in str(result):
        print("\n✅ VERIFICATION PASSED: CrewAI can talk to Ollama!")
    else:
        print("\n⚠️ VERIFICATION COMPLETED: Check output above.")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Is Ollama running? (ollama serve)")
    print("2. Is the model pulled? (ollama pull qwen2.5-coder:14b)")
