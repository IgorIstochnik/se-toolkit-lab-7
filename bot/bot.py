#!/usr/bin/env python3
"""Telegram bot entry point.

Supports two modes:
- Test mode: `python bot.py --test "/command"` — prints response to stdout
- Telegram mode: `python bot.py` — runs the Telegram bot client
"""

import argparse
import asyncio
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart

from config import settings
from handlers import (
    handle_health,
    handle_help,
    handle_labs,
    handle_scores,
    handle_start,
)


async def run_test_mode(command: str) -> None:
    """Run a command in test mode — call handler directly and print result."""
    # Parse the command and route to the appropriate handler
    if command == "/start" or command == "start":
        response = await handle_start()
    elif command == "/help" or command == "help":
        response = await handle_help()
    elif command == "/health" or command == "health":
        response = await handle_health()
    elif command == "/labs" or command == "labs":
        response = await handle_labs()
    elif command.startswith("/scores") or command.startswith("scores"):
        # Extract lab_id if provided: /scores lab-04
        parts = command.split()
        lab_id = parts[1] if len(parts) > 1 else None
        response = await handle_scores(lab_id)
    else:
        response = f"Unknown command: {command}. Use /help for available commands."

    print(response)


async def run_telegram_mode() -> None:
    """Run the Telegram bot client."""
    if not settings.bot_token:
        print("Error: BOT_TOKEN not set in .env.bot.secret", file=sys.stderr)
        sys.exit(1)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Register command handlers
    @dp.message(CommandStart())
    async def cmd_start(message: types.Message) -> None:
        response = await handle_start()
        await message.answer(response)

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message) -> None:
        response = await handle_help()
        await message.answer(response)

    @dp.message(Command("health"))
    async def cmd_health(message: types.Message) -> None:
        response = await handle_health()
        await message.answer(response)

    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message) -> None:
        response = await handle_labs()
        await message.answer(response)

    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message) -> None:
        # Extract lab_id from command args: /scores lab-04
        lab_id = message.text.split()[1] if len(message.text.split()) > 1 else None
        response = await handle_scores(lab_id)
        await message.answer(response)

    # Start polling
    print("Bot is running... Press Ctrl+C to stop.")
    await dp.start_polling(bot)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Run in test mode with the given command (e.g., --test '/start')",
    )
    args = parser.parse_args()

    if args.test:
        # Test mode: call handler directly and print result
        asyncio.run(run_test_mode(args.test))
    else:
        # Telegram mode: run the bot client
        asyncio.run(run_telegram_mode())


if __name__ == "__main__":
    main()
