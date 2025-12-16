"""
Docker Sandbox Tool for CrewAI

Runs Python code in an isolated Docker container with:
- Safety gate for dangerous commands (requires user approval)
- Volume mounting for file persistence to host ./workspace directory
"""

import os
import docker
import tarfile
import io
import time
import base64

# Windows compatibility - must be imported before crewai
import win_patch

from crewai.tools import BaseTool


# Keywords that trigger human approval before execution
DANGEROUS_KEYWORDS = [
    "rm ", "rm(",           # File deletion
    "rmdir", "shutil.rmtree",
    "os.remove", "os.unlink",
    "docker system prune",  # Docker cleanup
    "curl ", "wget ",       # Network requests
    "requests.get", "requests.post",
    "urllib.request",
    "subprocess.call", "subprocess.run", "os.system",  # Shell commands
]


class DockerSandboxTool(BaseTool):
    """
    Runs Python code in a secure, isolated Docker container.
    
    Features:
    - Human approval gate for dangerous operations
    - Volume mounting: Files written to /workspace in container 
      appear in ./workspace on host machine
    """
    
    name: str = "Docker Sandbox Executor"
    description: str = (
        "Runs Python code in a secure, isolated Docker container. "
        "Input should be a raw string of valid Python code. "
        "Files saved to the current directory will persist in ./workspace on host. "
        "Returns the standard output (stdout) or error (stderr)."
    )
    
    def _check_dangerous(self, code: str) -> bool:
        """
        Check if the code contains dangerous operations.
        
        Args:
            code: The Python code to check
            
        Returns:
            True if dangerous keywords found, False otherwise
        """
        code_lower = code.lower()
        for keyword in DANGEROUS_KEYWORDS:
            if keyword.lower() in code_lower:
                return True
        return False
    
    def _request_approval(self, code: str) -> bool:
        """
        Request human approval for dangerous code execution.
        
        Args:
            code: The dangerous code to review
            
        Returns:
            True if user approves, False otherwise
        """
        print("\n" + "="*60)
        print("⚠️  HUMAN APPROVAL REQUIRED")
        print("="*60)
        print("The agent wants to execute code with potentially dangerous operations:")
        print("-"*60)
        print(code[:500] + ("..." if len(code) > 500 else ""))
        print("-"*60)
        
        try:
            response = input("Allow execution? [y/N]: ").strip().lower()
            return response == 'y'
        except EOFError:
            # Non-interactive mode, deny by default
            print("Non-interactive mode detected. Denying by default.")
            return False
    
    def _run(self, code: str) -> str:
        """
        Execute Python code in a Docker container.
        
        Args:
            code: Python code to execute
            
        Returns:
            Execution output or error message
        """
        # Safety check
        if self._check_dangerous(code):
            if not self._request_approval(code):
                return "EXECUTION DENIED: User rejected potentially dangerous code."
        
        client = docker.from_env()
        
        # Ensure workspace directory exists on host
        workspace_path = os.path.join(os.getcwd(), "workspace")
        os.makedirs(workspace_path, exist_ok=True)
        
        try:
            # Spin up container with volume mount
            # The workspace folder is mounted so files persist
            container = client.containers.run(
                "mcr.microsoft.com/devcontainers/python:3.11",
                command="sleep 120",  # Keep alive for execution
                detach=True,
                remove=True,
                working_dir="/workspace",
                volumes={
                    workspace_path: {
                        'bind': '/workspace',
                        'mode': 'rw'
                    }
                }
            )
            
            # Write code to file using base64 to avoid escaping issues
            code_b64 = base64.b64encode(code.encode('utf-8')).decode('utf-8')
            write_cmd = f"echo '{code_b64}' | base64 -d > /workspace/script.py"
            container.exec_run(f"/bin/bash -c \"{write_cmd}\"")
            
            # Execute the code
            exec_result = container.exec_run(
                "python /workspace/script.py",
                workdir="/workspace"
            )
            
            output = exec_result.output.decode('utf-8')
            exit_code = exec_result.exit_code
            
            # Cleanup
            container.stop()
            
            if exit_code != 0:
                return f"EXECUTION ERROR:\n{output}"
            return f"SUCCESS OUTPUT:\n{output}"
            
        except Exception as e:
            return f"SYSTEM ERROR: Docker failed to run. Reason: {str(e)}"