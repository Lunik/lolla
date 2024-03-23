"""
This module contains the logger used by lolla.
"""

from rich.console import Console


class LollaLogger:
    """
    Custom logger for lolla.
    """

    def __init__(self, level="error"):
        self.console = Console()
        self.level = level

    def info(self, message, **kwargs):
        """
        Print an info message.
        """
        if self.level in ["info", "error", "warning", "debug"]:
            self.print(f"info: {message}", style="bold blue", **kwargs)

    def error(self, message, **kwargs):
        """
        Print an error message.
        """
        if self.level in ["error", "warning", "debug"]:
            self.print(f"error: {message}", style="bold red", **kwargs)

    def warning(self, message, **kwargs):
        """
        Print a warning message.
        """
        if self.level in ["warning", "debug"]:
            self.print(f"warning: {message}", style="bold yellow", **kwargs)

    def debug(self, message, **kwargs):
        """
        Print a debug message.
        """
        if self.level == "debug":
            self.print(f"debug: {message}", style="bold grey0", **kwargs)

    def print(self, *args, **kwargs):
        """
        Print a raw message.
        """
        self.console.print(*args, **kwargs)
