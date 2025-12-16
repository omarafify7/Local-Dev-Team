"""
Codebase Mapper Tool for CrewAI

Provides the Architect agent with visibility into the project structure.
Creates a markdown summary of the directory tree and saves it to context/map.md.
"""

import os
import win_patch  # Windows compatibility

from crewai.tools import BaseTool
from typing import Optional


class CodebaseMapper(BaseTool):
    """
    Tool that scans the project directory and creates a markdown map
    of the codebase structure for the Architect agent to reference.
    """
    
    name: str = "Codebase Mapper"
    description: str = (
        "Scans the current project directory and creates a structured markdown "
        "summary of all files and folders. Useful for understanding the project "
        "layout before making changes. Returns the map as a string and saves it "
        "to 'context/map.md'."
    )
    
    # Directories to ignore when scanning
    IGNORE_DIRS: set = {".git", "__pycache__", ".venv", "venv", "node_modules", ".idea", ".vscode"}
    
    # File extensions to ignore
    IGNORE_EXTENSIONS: set = {".pyc", ".pyo", ".log", ".tmp"}
    
    def _run(self, root_path: Optional[str] = None) -> str:
        """
        Scan the directory and generate a markdown tree structure.
        
        Args:
            root_path: Optional path to scan. Defaults to current working directory.
            
        Returns:
            Markdown-formatted directory tree as a string.
        """
        if root_path is None:
            root_path = os.getcwd()
        
        # Build the tree structure
        tree_lines = ["# Codebase Map", "", f"**Root:** `{root_path}`", "", "```"]
        self._build_tree(root_path, tree_lines, prefix="")
        tree_lines.append("```")
        
        # Join into final markdown
        map_content = "\n".join(tree_lines)
        
        # Save to context/map.md
        context_dir = os.path.join(root_path, "context")
        os.makedirs(context_dir, exist_ok=True)
        
        map_file = os.path.join(context_dir, "map.md")
        with open(map_file, "w", encoding="utf-8") as f:
            f.write(map_content)
        
        return f"SUCCESS: Codebase map saved to {map_file}\n\n{map_content}"
    
    def _build_tree(self, path: str, lines: list, prefix: str) -> None:
        """
        Recursively build the directory tree.
        
        Args:
            path: Current directory path
            lines: List to append tree lines to
            prefix: Current indentation prefix
        """
        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            lines.append(f"{prefix}[Permission Denied]")
            return
        
        # Separate directories and files
        dirs = []
        files = []
        
        for entry in entries:
            full_path = os.path.join(path, entry)
            
            # Skip ignored directories
            if entry in self.IGNORE_DIRS:
                continue
            
            # Skip ignored file extensions
            _, ext = os.path.splitext(entry)
            if ext in self.IGNORE_EXTENSIONS:
                continue
            
            if os.path.isdir(full_path):
                dirs.append(entry)
            else:
                files.append(entry)
        
        # Process directories first
        for i, d in enumerate(dirs):
            is_last_dir = (i == len(dirs) - 1) and (len(files) == 0)
            connector = "└── " if is_last_dir else "├── "
            lines.append(f"{prefix}{connector}📁 {d}/")
            
            # Recurse into subdirectory
            new_prefix = prefix + ("    " if is_last_dir else "│   ")
            self._build_tree(os.path.join(path, d), lines, new_prefix)
        
        # Then process files
        for i, f in enumerate(files):
            is_last = (i == len(files) - 1)
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}📄 {f}")
