# Script: .\llama_legacy_serve.py

# Imports
import os
import json
from flask import Flask
from scripts.display_interface import display_main_menu
from scripts.server_models import chat_completions
from scripts.config_manager import load_json_config, save_json_config

# Globals
app = Flask(__name__)
PERSISTENCE_FILE = "./data/persistence.json"

# Load config
def load_json_config(file_path: str) -> Dict[str, Any]:
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {file_path}. Using empty config.")
        except IOError:
            print(f"Error reading file {file_path}. Using empty config.")
    return {}

def save_json_config(file_path: str, config: Dict[str, Any]):
    try:
        with open(file_path, "w") as f:
            json.dump(config, f, indent=4)
        print(f"Configuration saved to {file_path}")
    except IOError:
        print(f"Error writing to file {file_path

# Main Function
def main():
    config = load_json_config()
    chat_completions(app, config)  # Register the chat_completions route

    # Keep displaying the main menu until the user decides to exit
    while display_main_menu(config, app):
        pass

    save_json_config(PERSISTENCE_FILE, config) 

# Entry Point
if __name__ == "__main__":
    main()
