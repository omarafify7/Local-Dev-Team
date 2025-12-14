## Build Local Team
A workflow that outlines the steps needed to build a Local LLM Agent Team running using the RTX 5070 Ti

**Role:** You are the Lead Systems Architect. Your goal is to build a local, autonomous software development team using Python, CrewAI, and Docker.
**Constraint:** All code execution by the generated agents must happen inside a Docker container.
**Hardware Context:** The user is running an RTX 5070 Ti (16GB VRAM). We are using Ollama with `qwen2.5-coder:14b` as the backend.

---

## Phase 1: Foundation & Dependencies
1.  **Check Environment:** Usthe the workflopw for setting up-work-env found in /setting-up-work-env you might need to deviate by because we dont necessiarlity want to install pytorch. Verify `python`, `pip`, and `docker` are installed and running withing the enviornment you create.
2.  **Initialize Project:**
    * Create a virtual environment.
    * Create a `requirements.txt` with: `crewai`, `langgraph`, `docker`, `duckduckgo-search`.
    * Install dependencies.
3.  **Verify Ollama:**
    * Check if Ollama is running at `localhost:11434`.
    * If not, instruct the user to run `ollama serve`.
    * Instruct user to pull the model: `ollama pull qwen2.5-coder:14b`.

## Phase 2: The Docker Execution Tool (Critical)
* **Action:** Create a file named `tools/docker_tool.py`.
* **Content:** Implement a CrewAI-compatible tool class named `DockerExecutor`.
    * It must use the python `docker` SDK.
    * It must spin up a container from `mcr.microsoft.com/devcontainers/python:3.11`.
    * It must accept a `code` string, write it to a file inside the container, run it, and return `stdout` + `stderr`.
    * *Self-Correction:* Ensure the container is cleaned up (removed) after execution to save resources.

## Phase 3: The Agent Definitions
* **Action:** Create `main.py` that defines the Agent Team.
* **Agents to Create:**
    1.  **Architect:** (Role: Planner) - Uses `qwen2.5-coder:14b`.
    2.  **Engineer:** (Role: Coder) - Uses `qwen2.5-coder:14b`.
    3.  **Executor:** (Role: Tester) - Uses the `DockerExecutor` tool we created in Phase 2.
* **Workflow Logic:**
    * Architect creates a plan -> Engineer writes code -> Executor runs it in Docker.
    * *Feedback Loop:* If Executor returns `stderr`, the Engineer must retry.

## Phase 4: Verification
1.  **Test Run:** Create a simplified test in `main.py` that asks the team to: "Write a Python script that calculates the first 10 Fibonacci numbers and prints them."
2.  **Execution:** Run the `main.py` file.
3.  **Validation:** Check if the output shows the correct numbers generated from inside the Docker container.

## Phase 5: Advanced Context Workflows 
* **Action:** Implement a `CodebaseMapper` tool for the Architect agent.
    * *Function:* Walks the directory tree, creates a markdown summary of the project structure, and stores it in `context/map.md`.
    * *Constraint:* The Architect MUST read this map before proposing any file changes.
* **Action:** Implement a `HumanApproval` gate.
    * *Logic:* Before the Executor runs any shell command that contains `rm`, `docker system prune`, or network requests, it must pause and ask the user: "Allow execution? [y/n]" via the terminal.