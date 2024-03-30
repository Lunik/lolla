"""
Root module for lolla
"""

import sys
import cmd
import argparse
import os
import re
from textwrap import dedent
from base64 import b64encode

from rich.table import Table
from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    FileSizeColumn,
    TransferSpeedColumn,
)
from rich.text import Text
from rich import filesize
from rich.live import Live

from .ollama import OllamaConnector
from .tools import parse_model


class LollaShell(cmd.Cmd):
    prompt = "(user) "

    system_messages_content = (
        dedent(
            """
        From now on, you are 'Lolla', a virtual assistant that is helping users.
        You are about to chat with a Human user.
        You MUST follow those very important rules during the conversation:
        - You need to respond in the same language as the user.
        - ALWAYS make short answers. You are not verbose.
    """
        )
        .strip()
        .replace("\n", " ")
    )
    conversation = []
    files_pattern = re.compile(r"@\'?([a-zA-Z0-9-_/\.\~\s]+)\'?")
    stop_trigger = False

    def __init__(self, app_version, storage, logger, args):
        super().__init__()
        self.app_version = app_version
        self.logger = logger
        self.args = args
        self.ollama_connector = OllamaConnector(
            app_version, logger, args.endpoint, args.keep_alive
        )
        self.selected_model = (
            parse_model(args.model).get("full") if args.model else None
        )
        self.storage = storage

        self.conversation = self.storage.load_conversation()

    def _get_files(self, content):
        return self.files_pattern.findall(content)

    def _clean_files(self, content):
        return self.files_pattern.sub("", content)

    def _load_file(self, path):
        # Return as base64
        self.logger.info(f"Loading file '{path}'")
        with open(path, "rb") as file:
            return b64encode(file.read()).decode("utf-8")

    def reset_conversation(self):
        self.conversation = [
            {"role": "system", "content": self.system_messages_content}
        ]
        self.storage.save_conversation(conversation=self.conversation)

    def append_conversation(self, role, content, files=None):
        message = {"role": role, "content": content}

        if files:
            message["images"] = []
            for file_path in files:
                if os.path.isfile(file_path):
                    message["images"].append(self._load_file(file_path))
                else:
                    self.logger.error(f"File '{file_path}' not found")

        self.conversation.append(message)
        self.storage.save_conversation(conversation=self.conversation)

    def init_select_model(self):
        models = self.ollama_connector.list_models()
        if len(models) == 0:
            self.logger.info(
                "No models currently available. Continue with default model"
            )
            return

        first_model = self.ollama_connector.list_models()[0].get("name")

        if self.selected_model:
            exists = False
            for model in self.ollama_connector.list_models():
                if model["name"] == self.selected_model:
                    exists = True
                    break
            if not exists:
                self.logger.error(
                    f"Model '{self.selected_model}' not found. Using '{first_model}' instead"
                )
                self.selected_model = first_model
        else:
            self.selected_model = first_model

        self.logger.info(f"Selected model '{self.selected_model}' by default")

    def preloop(self):
        self.logger.print("Welcome to Lolla\n", style="bold green")
        self.logger.info("Checking Ollama server status")
        try:
            self.ollama_connector.health()
            version = self.ollama_connector.version()
        except Exception as exception:
            self.logger.error(
                f"Unable to connect to Ollama endpoint : {self.ollama_connector.endpoint}"
            )
            self.logger.debug(exception)
            sys.exit(1)

        self.logger.info(f"Connected to Ollama({version})")

        self.init_select_model()

        self.logger.print("\nUse 'help' to see available commands\n")

    def postloop(self):
        self.logger.print("\nThank you for using Lolla\n", style="bold green")

    # ----- basic Lolla commands -----
    def do_list(self, arg):
        "List all the available models."
        models = self.ollama_connector.list_models()

        table = Table(title="Ollama local models")
        table.add_column("Selected", style="bold")
        table.add_column("Name")
        table.add_column("Version")
        table.add_column("Familly")
        table.add_column("Parameters")
        table.add_column("Quantization")
        table.add_column("Size")

        for model in models:
            _model = parse_model(model["name"])
            table.add_row(
                Text(
                    "*" if self.selected_model == model["name"] else "", justify="right"
                ),
                _model["name"],
                _model["version"],
                model["details"]["family"],
                model["details"]["parameter_size"],
                model["details"]["quantization_level"],
                filesize.decimal(model["size"]),
            )

        self.logger.print(table)

    def do_pull(self, arg):
        "Pull a model from the server. Usage: pull <model_name>:[version]"
        if not arg:
            self.logger.error("Please provide a model name")
            self.do_help("pull")
            return

        model = parse_model(arg)

        self.logger.info(f"Pulling model {model['full']}")

        stream = self.ollama_connector.pull_model(
            name=model["name"], version=model["version"]
        )

        statuses = {}
        error = None
        with Progress(
            TextColumn("[progress.description]{task.description}", justify="left"),
            TaskProgressColumn(
                "[progress.percentage]{task.percentage:>3.0f}%",
                justify="right",
                show_speed=True,
            ),
            BarColumn(bar_width=None),
            FileSizeColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(compact=True, elapsed_when_finished=True),
        ) as progress:
            for event in stream:
                if event.get("error"):
                    error = event["error"]
                    break
                match event["status"]:
                    case "success":
                        break
                    case _:
                        if event["status"] not in statuses:
                            statuses[event["status"]] = progress.add_task(
                                event["status"], total=event.get("total", -1)
                            )

                        progress.update(
                            statuses[event["status"]],
                            completed=event.get("completed", -1),
                        )

        if error:
            self.logger.error(error)

        self.logger.info(f"Succesfully pulled model {model['full']}")
        if self.selected_model is None:
            self.selected_model = model["full"]

    def do_delete(self, arg):
        "Delete a model from the server. Usage: delete <model_name>:[version]"
        if not arg:
            self.logger.error("Please provide a model name")
            self.do_help("delete")
            return

        model = parse_model(arg)

        self.logger.info(f"Deleting model {model['full']}")

        self.ollama_connector.delete_model(name=model["name"], version=model["version"])

        self.logger.info(f"Succesfully deleted model {model['full']}")

    def do_quit(self, arg):
        "Quit Lolla. Usage: quit"
        return True

    def do_exit(self, arg):
        "Exit Lolla. Usage: exit"
        return True

    def do_EOF(self, arg):
        "Exit Lolla. Usage: Ctrl+D"
        return True

    def do_select(self, arg):
        "Select a model. Usage: select <model_name>:[version]"
        if not arg:
            self.logger.error("Please provide a model name")
            self.do_help("select")
            return

        model = parse_model(arg)

        models = self.ollama_connector.list_models()
        for _model in models:
            if _model["name"] == f"{model['full']}":
                self.selected_model = model["full"]
                self.logger.info(f"Selected model {model['full']}")
                return

        self.logger.error(
            f"Model {model['full']} not found. Use 'list' to see available models"
        )

    def do_reset(self, arg):
        "Reset the conversation. Usage: reset"
        self.reset_conversation()
        self.logger.info("Conversation reseted")

    def do_clear(self, arg):
        "Clear the screen. Usage: clear"
        os.system("clear")

    def default(self, arg):
        "By default, do chat completion."
        files = self._get_files(arg)
        arg = self._clean_files(arg)
        self.append_conversation("user", arg, files)

        assitant_message = ""

        try:
            stream = self.ollama_connector.chat(
                model=self.selected_model, messages=self.conversation
            )

            model = parse_model(self.selected_model)

            prefix = f"(lolla/{model['name']})"
            with Live(prefix, auto_refresh=False) as live:

                self.stop_trigger = False
                for event in stream:

                    if self.stop_trigger:
                        self.logger.info("Response stopped by user")
                        break

                    partial_assitant_message = event.get("message", {}).get("content")
                    assitant_message += partial_assitant_message
                    live.update(f"{prefix} {assitant_message}")
                    live.refresh()
        except Exception as exception:
            self.logger.error("An error occured during the conversation")
            self.logger.debug(exception)

        if assitant_message:
            self.append_conversation("assistant", assitant_message)

    def emptyline(self):
        "Do nothing when an empty line is entered."
        pass

    def save_conversation(self):
        pass

    # ----- Lolla inner methods -----
    def close(self):
        pass
