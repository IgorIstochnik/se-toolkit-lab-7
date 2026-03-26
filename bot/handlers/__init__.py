"""Command handlers — pure functions that take input and return text.

These handlers have NO dependency on Telegram. They can be called from:
- --test mode (direct function call)
- Unit tests
- Telegram bot (via the message handler)

This is called **separation of concerns** — the handler logic is isolated
from the transport layer (Telegram).
"""

from services.lms_api import LMSAPIError, lms_api
from services.llm_client import llm_client
from handlers.intent_router import TOOLS, SYSTEM_PROMPT


async def handle_start() -> str:
    """Handle /start command."""
    return "Welcome! I'm your LMS assistant bot. Use /help to see available commands."


async def handle_help() -> str:
    """Handle /help command."""
    return """Available commands:
/start — Welcome message
/help — Show this help
/health — Check backend connection
/labs — List available labs
/scores <lab> — View pass rates for a lab (e.g., /scores lab-04)

You can also ask questions in plain English, like:
- "Which labs are available?"
- "Show me scores for lab 4"
- "Which lab has the lowest pass rate?"
- "Who are the top 5 students in lab 3?" """


async def handle_health() -> str:
    """Handle /health command — checks backend API status."""
    try:
        result = await lms_api.health_check()
        return f"Backend is healthy. {result['item_count']} items available."
    except LMSAPIError as e:
        return f"Backend error: {e.message}"


async def handle_labs() -> str:
    """Handle /labs command — list available labs."""
    try:
        items = await lms_api.get_items()
        labs = [item for item in items if item.get("type") == "lab"]
        if not labs:
            return "No labs available."
        return "Available labs:\n" + "\n".join(f"- {lab['title']}" for lab in labs)
    except LMSAPIError as e:
        return f"Failed to fetch labs: {e.message}"


async def handle_scores(lab_id: str | None = None) -> str:
    """Handle /scores command — view scores for a lab.

    Args:
        lab_id: Optional lab identifier (e.g., "lab-04")
    """
    if not lab_id:
        return "Please specify a lab, e.g., /scores lab-04"

    try:
        pass_rates = await lms_api.get_pass_rates(lab_id)
        if not pass_rates:
            return f"No data available for {lab_id}. Check the lab ID."

        # Format: "Pass rates for Lab 04:\n- Task Name: XX.X% (N attempts)"
        lines = [f"Pass rates for {lab_id.replace('-', ' ').title()}:"]
        for record in pass_rates:
            task_title = record.get("task_title", record.get("task", "Unknown"))
            pass_rate = record.get("pass_rate", 0)
            attempts = record.get("attempts", 0)
            lines.append(f"- {task_title}: {pass_rate:.1f}% ({attempts} attempts)")
        return "\n".join(lines)
    except LMSAPIError as e:
        return f"Failed to fetch scores for {lab_id}: {e.message}"


async def handle_intent(message: str) -> str:
    """Handle natural language queries using LLM intent routing.

    Args:
        message: User's natural language query

    Returns:
        LLM-generated response based on tool results
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]

    try:
        response = await llm_client.chat_with_tools(messages, TOOLS)
        return response
    except Exception as e:
        return f"Sorry, I couldn't process that request: {str(e)}"
