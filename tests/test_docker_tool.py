"""
Unit Tests for DockerSandboxTool

Tests:
1. Dangerous command detection
2. Human approval gate (mocked)
3. File persistence via volume mount
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import win_patch  # Windows compatibility
from tools.docker_tool import DockerSandboxTool, DANGEROUS_KEYWORDS


class TestDangerousCommandDetection(unittest.TestCase):
    """Test the dangerous command detection logic."""
    
    def setUp(self):
        self.tool = DockerSandboxTool()
    
    def test_rm_detected(self):
        """rm command should be flagged as dangerous."""
        code = "import os; os.system('rm -rf /tmp')"
        self.assertTrue(self.tool._check_dangerous(code))
    
    def test_shutil_rmtree_detected(self):
        """shutil.rmtree should be flagged as dangerous."""
        code = "import shutil; shutil.rmtree('/some/path')"
        self.assertTrue(self.tool._check_dangerous(code))
    
    def test_curl_detected(self):
        """curl network requests should be flagged."""
        code = "os.system('curl http://example.com')"
        self.assertTrue(self.tool._check_dangerous(code))
    
    def test_safe_code_not_flagged(self):
        """Simple print statement should not be flagged."""
        code = "print('Hello, World!')"
        self.assertFalse(self.tool._check_dangerous(code))
    
    def test_fibonacci_not_flagged(self):
        """Fibonacci calculation should not be flagged."""
        code = """
a, b = 0, 1
for _ in range(10):
    print(a)
    a, b = b, a + b
"""
        self.assertFalse(self.tool._check_dangerous(code))


class TestHumanApprovalGate(unittest.TestCase):
    """Test the human approval gate logic."""
    
    def setUp(self):
        self.tool = DockerSandboxTool()
    
    @patch('builtins.input', return_value='n')
    def test_denied_when_user_says_no(self, mock_input):
        """Execution should be denied when user enters 'n'."""
        result = self.tool._request_approval("os.system('rm -rf /')")
        self.assertFalse(result)
    
    @patch('builtins.input', return_value='y')
    def test_approved_when_user_says_yes(self, mock_input):
        """Execution should be approved when user enters 'y'."""
        result = self.tool._request_approval("os.system('rm temp.txt')")
        self.assertTrue(result)
    
    @patch('builtins.input', return_value='')
    def test_denied_on_empty_input(self, mock_input):
        """Execution should be denied on empty input (default N)."""
        result = self.tool._request_approval("dangerous code")
        self.assertFalse(result)


class TestDockerExecution(unittest.TestCase):
    """
    Integration tests for Docker execution.
    
    Note: These tests require Docker Desktop to be running.
    They are marked with skip decorators if Docker is not available.
    """
    
    @classmethod
    def setUpClass(cls):
        """Check if Docker is available."""
        try:
            import docker
            client = docker.from_env()
            client.ping()
            cls.docker_available = True
        except Exception:
            cls.docker_available = False
    
    def setUp(self):
        if not self.docker_available:
            self.skipTest("Docker is not available")
        self.tool = DockerSandboxTool()
    
    @patch.object(DockerSandboxTool, '_request_approval', return_value=False)
    def test_dangerous_code_blocked_without_approval(self, mock_approval):
        """Dangerous code should be blocked when user denies."""
        code = "import os; os.system('rm test.txt')"
        result = self.tool._run(code)
        self.assertIn("EXECUTION DENIED", result)
    
    def test_simple_print_executes(self):
        """Simple print statement should execute successfully."""
        code = "print('Hello from Docker!')"
        result = self.tool._run(code)
        self.assertIn("SUCCESS OUTPUT", result)
        self.assertIn("Hello from Docker!", result)
    
    def test_file_written_to_workspace(self):
        """Files written in container should appear in host workspace."""
        # Clean up any existing test file
        workspace_path = os.path.join(os.getcwd(), "workspace")
        test_file = os.path.join(workspace_path, "test_output.txt")
        if os.path.exists(test_file):
            os.remove(test_file)
        
        # Run code that creates a file
        code = """
with open('test_output.txt', 'w') as f:
    f.write('Hello from container!')
print('File written!')
"""
        result = self.tool._run(code)
        
        # Verify success
        self.assertIn("SUCCESS OUTPUT", result)
        
        # Verify file exists on host
        self.assertTrue(os.path.exists(test_file), "File should exist in workspace")
        
        # Verify file content
        with open(test_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, "Hello from container!")
        
        # Clean up
        os.remove(test_file)


if __name__ == '__main__':
    unittest.main(verbosity=2)
