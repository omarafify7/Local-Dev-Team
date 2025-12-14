import docker
import tarfile
import io
import time

# Windows compatibility - must be imported before crewai
import win_patch

from crewai.tools import BaseTool

class DockerSandboxTool(BaseTool):
    name: str = "Docker Sandbox Executor"
    description: str = (
        "Runs Python code in a secure, isolated Docker container. "
        "Input should be a raw string of valid Python code. "
        "Returns the standard output (stdout) or error (stderr)."
    )

    def _run(self, code: str) -> str:
        client = docker.from_env()
        
        # 1. Spin up the container (keep it alive just long enough to run)
        # using the Microsoft Dev Container image we discussed
        try:
            container = client.containers.run(
                "mcr.microsoft.com/devcontainers/python:3.11",
                command="sleep 60",  # Keep alive for 60s
                detach=True,
                remove=True
            )

            # 2. Setup the code inside the container
            # We wrap the user's code to capture errors easily
            setup_cmd = f"echo '{code}' > /workspace/script.py"
            
            # Using exec_run to write the file (simple bash echo)
            container.exec_run(f"/bin/bash -c \"{setup_cmd}\"")

            # 3. Execute the code
            exec_result = container.exec_run("python /workspace/script.py")
            
            output = exec_result.output.decode('utf-8')
            exit_code = exec_result.exit_code

            # 4. Cleanup manually if needed (though auto-remove is on)
            container.stop()

            if exit_code != 0:
                return f"EXECUTION ERROR:\n{output}"
            return f"SUCCESS OUTPUT:\n{output}"

        except Exception as e:
            return f"SYSTEM ERROR: Docker failed to run. Reason: {str(e)}"