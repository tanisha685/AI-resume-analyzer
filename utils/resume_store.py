import json
import os

class ResumeStore:

    def __init__(self):
        self.file = "resumes.json"

        if not os.path.exists(self.file):
            with open(self.file, "w") as f:
                json.dump([], f)

    def save_resume(self, name, text):
        data = self._load()

        data.append({
            "name": name,
            "text": text
        })

        self._save(data)

    def get_all_resumes(self):
        return self._load()

    def _load(self):
        with open(self.file, "r") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.file, "w") as f:
            json.dump(data, f, indent=2)