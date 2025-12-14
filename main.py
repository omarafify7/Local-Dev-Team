"""
Local Agent Team - Main Entry Point

CrewAI-based autonomous development team using Ollama (qwen2.5-coder:14b)
with Docker sandbox execution for secure code testing.

Architecture:
    Architect (Planner) -> Engineer (Coder) -> Executor (Tester)
    
Feedback Loop:
    If Executor returns stderr, Engineer retries (max 3 attempts).
"""

# Windows compatibility - must be imported first
import win_patch

from crewai import Agent, Task, Crew, Process, LLM
from tools.docker_tool import DockerSandboxTool

# =============================================================================
# LLM Configuration - Ollama Backend
# =============================================================================

# Configure Ollama as the LLM backend
# Ensure Ollama is running: `ollama serve`
# Ensure model is pulled: `ollama pull qwen2.5-coder:14b`
ollama_llm = LLM(
    model="ollama/qwen2.5-coder:14b",
    base_url="http://localhost:11434"
)

# =============================================================================
# Tool Initialization
# =============================================================================

# Docker sandbox tool for secure code execution
docker_tool = DockerSandboxTool()

# =============================================================================
# Agent Definitions
# =============================================================================

# Architect Agent - Plans the solution approach
architect = Agent(
    role="Software Architect",
    goal="Create clear, step-by-step implementation plans for coding tasks",
    backstory="""You are an experienced software architect who excels at 
    breaking down complex problems into simple, actionable steps. You provide 
    clear pseudocode and implementation guidance that developers can follow.""",
    llm=ollama_llm,
    verbose=True
)

# Engineer Agent - Writes the actual code
engineer = Agent(
    role="Software Engineer",
    goal="Write clean, working Python code based on the architect's plan",
    backstory="""You are a skilled Python developer who writes concise, 
    functional code. You follow best practices and ensure your code handles 
    edge cases. When given feedback about errors, you fix them efficiently.""",
    llm=ollama_llm,
    verbose=True
)

# Executor Agent - Tests code in Docker sandbox
executor = Agent(
    role="Code Executor",
    goal="Execute Python code in a secure Docker sandbox and report results",
    backstory="""You are a QA engineer who tests code by running it in an 
    isolated Docker environment. You provide clear feedback about whether 
    the code works correctly or if there are errors that need fixing.""",
    llm=ollama_llm,
    tools=[docker_tool],
    verbose=True
)

# =============================================================================
# Task Definitions with Feedback Loop
# =============================================================================

def run_agent_team(user_task: str, max_retries: int = 3) -> str:
    """
    Run the agent team on a given task with automatic retry on failure.
    
    Args:
        user_task: The task description for the agents to complete.
        max_retries: Maximum number of retry attempts if code fails.
        
    Returns:
        The final output from the agent team.
    """
    
    # Task 1: Architect creates the plan
    planning_task = Task(
        description=f"""
        Analyze the following task and create a step-by-step implementation plan:
        
        TASK: {user_task}
        
        Provide:
        1. A brief analysis of the problem
        2. Step-by-step pseudocode
        3. Key considerations and edge cases
        """,
        expected_output="A clear implementation plan with pseudocode",
        agent=architect
    )
    
    # Task 2: Engineer writes the code (depends on planning)
    coding_task = Task(
        description="""
        Based on the architect's plan, write complete Python code that:
        1. Implements the solution correctly
        2. Includes proper error handling
        3. Outputs results clearly with print statements
        
        IMPORTANT: Provide ONLY the raw Python code. No markdown, no explanations.
        The code must be directly executable.
        """,
        expected_output="Complete, executable Python code",
        agent=engineer,
        context=[planning_task]
    )
    
    # Task 3: Executor runs the code (depends on coding)
    execution_task = Task(
        description="""
        Execute the engineer's code in the Docker sandbox and report results.
        
        Use the Docker Sandbox Executor tool with the code provided.
        
        Report:
        - Whether the code executed successfully
        - The actual output from the code
        - Any errors that occurred
        """,
        expected_output="Execution results with output or error details",
        agent=executor,
        context=[coding_task]
    )
    
    # Run the crew with the defined workflow
    crew = Crew(
        agents=[architect, engineer, executor],
        tasks=[planning_task, coding_task, execution_task],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute and handle retries for failures
    for attempt in range(max_retries):
        print(f"\n{'='*60}")
        print(f"ATTEMPT {attempt + 1}/{max_retries}")
        print(f"{'='*60}\n")
        
        result = crew.kickoff()
        
        # Check if execution was successful
        result_str = str(result)
        if "EXECUTION ERROR:" not in result_str and "SYSTEM ERROR:" not in result_str:
            print("\n✅ SUCCESS: Code executed without errors!")
            return result_str
        else:
            print(f"\n⚠️ Attempt {attempt + 1} failed. Retrying...")
            if attempt < max_retries - 1:
                # Modify the coding task to indicate retry
                coding_task.description = f"""
                The previous code attempt FAILED with this error:
                {result_str}
                
                Please fix the code and try again. Remember:
                1. Analyze what went wrong
                2. Fix the specific issue
                3. Provide complete, executable Python code
                """
    
    print("\n❌ FAILED: Max retries exceeded.")
    return result_str


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    # Test task from the workflow specification
    test_task = """
    Write a Python script that calculates the first 10 Fibonacci numbers 
    and prints them. The output should be a comma-separated list.
    """
    
    print("="*60)
    print("LOCAL AGENT TEAM - CrewAI + Ollama + Docker")
    print("="*60)
    print(f"\nTest Task: {test_task.strip()}")
    print("="*60)
    
    # Run the agent team
    final_result = run_agent_team(test_task)
    
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    print(final_result)
