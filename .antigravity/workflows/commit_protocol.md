## Commit Protocol
Automates version control.

# Phase 1: Pre-Flight Validation
1. **Search**: Look for `./validate_workflow.py` or `./scripts/validate.sh`.
2. **Execute**:
   - IF found: Run the script.
     - ON FAILURE: Stop immediately. Output error log. Do NOT proceed to commit.
     - ON SUCCESS: Proceed to Phase 2.
   - IF NOT found: Log "No validation script; skipping checks" and proceed to Phase 2.

# Phase 2: The Smart Commit Process
(Execute the following logic autonomously. Do NOT ask for confirmation between steps.)

1. **Analyze State**:
   - Run `git status` and `git diff`.
   - Identify distinct "logical units of work" (e.g., separate the API fix from the README update).

2. **Exclusion Protocol (CRITICAL)**:
   - NEVER commit the `thoughts/` directory.
   - NEVER commit temporary test scripts (e.g., `temp_*.py`), generated logs, or binary model weights unless explicitly tracked.

3. **Execution Loop**:
   - For each logical unit of work identified:
     a. **Select**: Use `git add <specific_file_paths>` (NEVER use `git add .` or `-A`).
     b. **Draft**: Create a semantic commit message (imperative mood: "fix", "feat", "refactor").
     c. **Commit**: Run `git commit -m "type: message"`.

4. **Final Report**:
   - List the commits created.