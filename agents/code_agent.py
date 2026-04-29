"""
Code Executor Agent — restricted Python sandbox.

Security model:
- LLM extracts the code from natural language
- Code runs in a subprocess with a hard timeout (10s)
- Dangerous modules are blocked before execution
- No file system writes, no network calls, no shell access
- stdout + stderr captured and returned to user
"""
import subprocess
import sys
import re
import textwrap
import logging

logger = logging.getLogger(__name__)

# ── Blocked modules ───────────────────────────────────────────────────────────
# Any import of these will be rejected before execution
_BLOCKED = {
    "os", "sys", "subprocess", "shutil", "pathlib", "glob",
    "socket", "requests", "urllib", "http", "ftplib", "smtplib",
    "importlib", "builtins", "ctypes", "multiprocessing", "threading",
    "signal", "pty", "tty", "termios", "fcntl", "resource",
    "pickle", "shelve", "dbm", "sqlite3",
    "open",   # built-in file open
}

# Regex to detect import statements
_IMPORT_RE = re.compile(
    r"^\s*(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
    re.MULTILINE
)

# Detect open() calls
_OPEN_RE = re.compile(r"\bopen\s*\(")

# Detect exec/eval
_EXEC_RE = re.compile(r"\b(?:exec|eval|compile|__import__)\s*\(")


def _check_safety(code: str) -> str | None:
    """
    Return an error message if the code is unsafe, else None.
    """
    # Check imports
    for match in _IMPORT_RE.finditer(code):
        module = match.group(1)
        if module in _BLOCKED:
            return (
                f"🚫 **Blocked:** `import {module}` is not allowed in the sandbox.\n"
                f"Restricted modules: {', '.join(sorted(_BLOCKED))}"
            )

    # Check open()
    if _OPEN_RE.search(code):
        return "🚫 **Blocked:** `open()` (file access) is not allowed in the sandbox."

    # Check exec/eval
    if _EXEC_RE.search(code):
        return "🚫 **Blocked:** `exec`, `eval`, `compile`, and `__import__` are not allowed."

    return None


def _run_code(code: str, timeout: int = 10) -> tuple[str, str]:
    """
    Execute code in a subprocess. Returns (stdout, stderr).
    """
    # Wrap in a try/except so runtime errors are captured cleanly
    wrapped = textwrap.dedent(f"""
import traceback
try:
{textwrap.indent(code, '    ')}
except Exception:
    traceback.print_exc()
""")

    try:
        result = subprocess.run(
            [sys.executable, "-c", wrapped],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "", f"⏱️ Execution timed out after {timeout} seconds."
    except Exception as e:
        return "", f"❌ Execution error: {str(e)}"


def handle_code(user_message: str, context: str = "") -> str:
    from tools.llm_client import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage

    try:
        llm          = get_llm()
        context_hint = f"\nConversation so far:\n{context}\n" if context else ""

        # ── Step 1: Extract or generate code ─────────────────────────────────
        extract_messages = [
            SystemMessage(content=f"""
            The user wants to run Python code.
            Extract or write the Python code they want to execute.

            Rules:
            - Return ONLY the raw Python code, no markdown, no explanation
            - Do NOT include ```python or ``` markers
            - If the user describes what they want (e.g. "write a fibonacci function"),
              write clean working Python code for it
            - If the user pastes code directly, return it as-is
            - Keep code concise and correct
            {context_hint}
            """),
            HumanMessage(content=user_message)
        ]
        code = llm.invoke(extract_messages).content.strip()

        # Strip markdown code fences if LLM added them anyway
        code = re.sub(r"^```(?:python)?\n?", "", code, flags=re.MULTILINE)
        code = re.sub(r"\n?```$", "", code, flags=re.MULTILINE)
        code = code.strip()

        if not code:
            return "❓ I couldn't extract any code from your message. Try: *\"Run: print('hello world')\"*"

        # ── Step 2: Safety check ──────────────────────────────────────────────
        safety_error = _check_safety(code)
        if safety_error:
            return safety_error

        # ── Step 3: Execute ───────────────────────────────────────────────────
        logger.info(f"Executing code snippet ({len(code)} chars)")
        stdout, stderr = _run_code(code, timeout=10)

        # ── Step 4: Format output ─────────────────────────────────────────────
        output = f"💻 **Code Executed:**\n```python\n{code}\n```\n\n"

        if stdout:
            output += f"**Output:**\n```\n{stdout}\n```"
        if stderr:
            output += f"\n**Errors/Warnings:**\n```\n{stderr}\n```"
        if not stdout and not stderr:
            output += "✅ Code ran successfully with no output."

        return output

    except Exception as e:
        logger.error(f"Code agent error: {e}", exc_info=True)
        return f"⚠️ Code executor error: {str(e)}"
