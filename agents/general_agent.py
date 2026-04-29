import math
import ast
import operator
import re
from tools.llm_client import get_llm
from langchain_core.messages import HumanMessage, SystemMessage


# ── Safe math evaluator ──────────────────────────────────────────────────────
_SAFE_OPS = {
    ast.Add:  operator.add,
    ast.Sub:  operator.sub,
    ast.Mult: operator.mul,
    ast.Div:  operator.truediv,
    ast.Pow:  operator.pow,
    ast.Mod:  operator.mod,
    ast.USub: operator.neg,
}

def _safe_eval(node):
    """Recursively evaluate a math AST node — no exec, no eval."""
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        op = _SAFE_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {node.op}")
        return op(_safe_eval(node.left), _safe_eval(node.right))
    elif isinstance(node, ast.UnaryOp):
        op = _SAFE_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {node.op}")
        return op(_safe_eval(node.operand))
    elif isinstance(node, ast.Call):
        # Allow math module functions: sqrt, sin, cos, log, etc.
        if isinstance(node.func, ast.Attribute) and node.func.attr in dir(math):
            fn = getattr(math, node.func.attr)
            args = [_safe_eval(a) for a in node.args]
            return fn(*args)
        raise ValueError(f"Function calls not allowed: {ast.dump(node.func)}")
    else:
        raise ValueError(f"Unsupported expression: {ast.dump(node)}")


def calculate(expression: str):
    """
    Safely evaluate a math expression string.
    Supports: +, -, *, /, **, %, math.sqrt(), math.sin(), etc.
    Returns (result, error_message).
    """
    # Normalise: replace ^ with ** for power
    expression = expression.replace("^", "**")
    # Replace common words
    expression = re.sub(r'\bsqrt\b', 'math.sqrt', expression)
    expression = re.sub(r'\bsin\b',  'math.sin',  expression)
    expression = re.sub(r'\bcos\b',  'math.cos',  expression)
    expression = re.sub(r'\btan\b',  'math.tan',  expression)
    expression = re.sub(r'\blog\b',  'math.log',  expression)
    expression = re.sub(r'\bpi\b',   str(math.pi), expression)
    expression = re.sub(r'\be\b',    str(math.e),  expression)

    try:
        tree = ast.parse(expression, mode='eval')
        result = _safe_eval(tree.body)
        # Format nicely
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return result, None
    except ZeroDivisionError:
        return None, "Division by zero."
    except Exception as ex:
        return None, str(ex)


def handle_general(user_message, memory=None):
    llm = get_llm()

    # ── Detect if this is a math/calculation request ─────────────────────
    math_check = [
        SystemMessage(content="""
        Does the user message contain a math calculation or arithmetic expression?
        Examples that ARE math: "25 * 4", "sqrt(144)", "what is 15% of 200",
        "calculate 2^10", "sin(90)", "1000 / 4 + 50"
        Examples that are NOT math: "what is the capital of France", "tell me a joke"

        Respond with just: yes or no
        """),
        HumanMessage(content=user_message)
    ]
    is_math = llm.invoke(math_check).content.strip().lower() == "yes"

    if is_math:
        # Ask LLM to extract the clean math expression
        extract_messages = [
            SystemMessage(content="""
            Extract only the mathematical expression from the user message.
            Convert word problems to expressions.
            Examples:
            "what is 25 times 4"          -> 25 * 4
            "calculate 15 percent of 200" -> 200 * 0.15
            "square root of 144"          -> sqrt(144)
            "2 to the power of 10"        -> 2 ** 10
            "what is 100 divided by 4"    -> 100 / 4

            Respond with just the expression, nothing else.
            """),
            HumanMessage(content=user_message)
        ]
        expression = llm.invoke(extract_messages).content.strip()
        result, error = calculate(expression)

        if error is None:
            return (
                f"🧮 **Calculation Result**\n\n"
                f"Expression: `{expression}`\n"
                f"Answer: **{result}**"
            )
        else:
            # Fall through to LLM if safe eval fails (complex word problem)
            pass

    # ── General LLM response ─────────────────────────────────────────────
    messages = [
        SystemMessage(content="""
        You are ARIA, a helpful, friendly, and knowledgeable AI personal assistant.
        Answer questions clearly and concisely.
        For factual questions, be precise. For casual conversation, be warm and engaging.
        If you remember previous messages, use that context to give better answers.
        Format your responses with markdown when it improves readability.
        """)
    ]

    # Add memory history if available
    if memory:
        history = memory.get_history()
        messages.extend(history[-4:])  # last 4 messages for context

    messages.append(HumanMessage(content=user_message))

    response = llm.invoke(messages)
    return response.content.strip()
