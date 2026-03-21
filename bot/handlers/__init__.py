"""Command handlers — pure functions that take input and return text.

These handlers have NO dependency on Telegram. They can be called from:
- --test mode (direct function call)
- Unit tests
- Telegram bot (via the message handler)

This is called **separation of concerns** — the handler logic is isolated
from the transport layer (Telegram).
"""


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
/scores — View your scores"""


async def handle_health() -> str:
    """Handle /health command — checks backend API status."""
    # Task 2: implement actual backend health check
    return "Backend status: OK (placeholder)"


async def handle_labs() -> str:
    """Handle /labs command — list available labs."""
    # Task 2: fetch labs from backend API
    return "Available labs: Lab 01, Lab 02, ... (placeholder)"


async def handle_scores(lab_id: str | None = None) -> str:
    """Handle /scores command — view scores for a lab.

    Args:
        lab_id: Optional lab identifier (e.g., "lab-04")
    """
    # Task 2: fetch scores from backend API
    if lab_id:
        return f"Scores for {lab_id}: (placeholder)"
    return "Your scores: (placeholder)"
