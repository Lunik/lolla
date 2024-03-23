import sys
import cmd
import argparse


class LollaParser(argparse.ArgumentParser):
    """
    Custom python parser for lolla.
    """

    def error(self, message):
        """
        Print an error message and exit.
        """
        self.print_help()
        sys.exit(2)


class LollaConfig:
    """
    Config class for lolla.
    """

    def __init__(self, app_version):
        self.app_version = app_version

    @property
    def parser(self):
        """
        Construct the parser for lolla.
        Returns an instance of LollaParser.
        """
        parser = LollaParser(
            description="Local Ollama CLI.",
            epilog=f"version : {sys.argv[0]}@{self.app_version}",
        )

        parser.add_argument(
            "--endpoint",
            type=str,
            help="The Ollama endpoint to connect to.",
            default="http://localhost:11434",
        )

        parser.add_argument(
            "--keep-alive",
            type=str,
            help="Time to keep the AI model loaded in memory. ex: 5m, 1h, 1d",
            default="5m",
        )

        parser.add_argument(
            "--log-level",
            type=str,
            help="The log level to use.",
            default="error",
            choices=["error", "warning", "info", "debug"],
        )

        parser.add_argument(
            "--model",
            "-m",
            type=str,
            help="The AI model to use by default.",
        )

        parser.add_argument(
            "--home",
            type=str,
            help="The home directory for lolla. This is where data is stored.",
            default="~/.lolla",
        )

        return parser
