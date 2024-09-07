# Script: .\llama_legacy_serve.py

# Imports
import os
import json
from flask import Flask
from scripts.display_interface import display_main_menu
from scripts.server_models import chat_completions

# Globals
app = Flask(__name__)
PERSISTENCE_FILE = "./data/persistence.json"

# Load config
def load_json_config():
    if os.path.exists(PERSISTENCE_FILE):
        with open(PERSISTENCE_FILE, "r") as f:
            return json.load(f)
    return {}

# Save config
def save_json_config(config):
    with open(PERSISTENCE_FILE, "w") as f:
        json.dump(config, f, indent=4)

# Main Function
def main():
    config = load_json_config()
    chat_completions(app, config)  # Register the chat_completions route

    # Keep displaying the main menu until the user decides to exit
    while display_main_menu(config, app):
        pass

# Entry Point
if __name__ == "__main__":
    main()
