"""
Unit Tests for CodebaseMapper Tool

Tests:
1. Directory tree generation
2. Ignored directories/files filtering
3. Context file creation
"""

import unittest
import os
import sys
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import win_patch  # Windows compatibility
from tools.file_tools import CodebaseMapper


class TestCodebaseMapper(unittest.TestCase):
    """Test the CodebaseMapper tool."""
    
    def setUp(self):
        """Create a temporary directory structure for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.mapper = CodebaseMapper()
        
        # Create a mock project structure
        os.makedirs(os.path.join(self.test_dir, "src"))
        os.makedirs(os.path.join(self.test_dir, "tests"))
        os.makedirs(os.path.join(self.test_dir, "__pycache__"))  # Should be ignored
        os.makedirs(os.path.join(self.test_dir, ".git"))  # Should be ignored
        
        # Create some files
        with open(os.path.join(self.test_dir, "main.py"), 'w') as f:
            f.write("print('hello')")
        with open(os.path.join(self.test_dir, "src", "utils.py"), 'w') as f:
            f.write("# utils")
        with open(os.path.join(self.test_dir, "tests", "test_main.py"), 'w') as f:
            f.write("# test")
        with open(os.path.join(self.test_dir, "cache.pyc"), 'w') as f:  # Should be ignored
            f.write("")
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)
    
    def test_generates_tree_structure(self):
        """Mapper should generate a tree structure."""
        result = self.mapper._run(self.test_dir)
        
        self.assertIn("SUCCESS", result)
        self.assertIn("Codebase Map", result)
        self.assertIn("main.py", result)
    
    def test_includes_subdirectories(self):
        """Mapper should include subdirectories in tree."""
        result = self.mapper._run(self.test_dir)
        
        self.assertIn("src", result)
        self.assertIn("tests", result)
        self.assertIn("utils.py", result)
    
    def test_ignores_pycache(self):
        """Mapper should ignore __pycache__ directory."""
        result = self.mapper._run(self.test_dir)
        
        self.assertNotIn("__pycache__", result)
    
    def test_ignores_git(self):
        """Mapper should ignore .git directory."""
        result = self.mapper._run(self.test_dir)
        
        self.assertNotIn(".git", result)
    
    def test_ignores_pyc_files(self):
        """Mapper should ignore .pyc files."""
        result = self.mapper._run(self.test_dir)
        
        self.assertNotIn("cache.pyc", result)
    
    def test_creates_context_directory(self):
        """Mapper should create context directory if missing."""
        result = self.mapper._run(self.test_dir)
        
        context_dir = os.path.join(self.test_dir, "context")
        self.assertTrue(os.path.exists(context_dir))
    
    def test_saves_map_file(self):
        """Mapper should save map.md to context directory."""
        result = self.mapper._run(self.test_dir)
        
        map_file = os.path.join(self.test_dir, "context", "map.md")
        self.assertTrue(os.path.exists(map_file))
        
        # Verify content was written
        with open(map_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("Codebase Map", content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
