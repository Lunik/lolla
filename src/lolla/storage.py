import os
import json
import shutil

class LollaStorage:
    def __init__(self, home):
        self.home =  os.path.expanduser(home)

        self._prepare_home()

    def _prepare_home(self):
        if not os.path.isdir(self.home):
            os.makedirs(self.home)

    def save_conversation(self, conversation):
        with open(os.path.join(self.home, "conversation.json"), "w", encoding="utf-8") as f:
            json.dump(conversation, f, indent=2, ensure_ascii=False)

    def load_conversation(self):
        if not os.path.isfile(os.path.join(self.home, "conversation.json")):
            return []

        with open(os.path.join(self.home, "conversation.json"), "r", encoding="utf-8") as f:
            return json.load(f)

    def cleanup(self):
        shutil.rmtree(self.home)
