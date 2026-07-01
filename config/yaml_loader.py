import os

import yaml


class YAMLLoader:
    """Base class for loading YAML configuration files with auto-reload capabilities."""

    def __init__(self, path: str):
        self.path = path
        self.last_modified = 0
        self.raw = {}
        self.load()

    def load(self):
        """Loads or reloads the YAML file."""
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Configuration file not found: {self.path}")

        with open(self.path) as file:
            self.raw = yaml.safe_load(file) or {}

        self.last_modified = os.path.getmtime(self.path)

    def reload_if_needed(self) -> bool:
        """
        Reloads the configuration if the file has been modified.
        Returns True if reloaded, False otherwise.
        """
        current_time = os.path.getmtime(self.path)
        if current_time != self.last_modified:
            self.load()
            return True
        return False
