# Script: .\scripts\display_interface.py

# Imports
import os
import json
from scripts.hardware_binaries import (
    list_available_binaries, install_binary, remove_binary, update_binaries
)

# Functions
def print_script_header(header_type="main"):
    """Prints the header based on the menu type."""
    clear_screen()
    print("=" * 120)
    
    if header_type == "main":
        print("    Llama-Legacy-Serve - Main Menu")
    elif header_type == "model_selection":
        print("    Llama-Legacy-Serve - Model Selection")
    elif header_type == "hardware":
        print("    Llama-Legacy-Serve - Hardware Configuration")
    elif header_type == "binary_management":
        print("    Llama-Legacy-Serve - Binary Management")
    elif header_type == "server_start":
        print("    Llama-Legacy-Serve - Start Server")
    elif header_type == "current_config":
        print("    Llama-Legacy-Serve - Current Configuration")
    
    print("=" * 120)
    print("\n")


# Main menu with its own handling logic
def display_main_menu(config, app):
    print_script_header("main")
    print("1. Select Model")
    print("2. Configure Hardware")
    print("3. Manage Binaries")
    print("4. Start Server")
    print("5. View Current Configuration")
    print("x. Exit")
    
    choice = input("Selection; Menu Options = 1-5, Exit and Save = X: ")

    if choice == '1':  # Model selection
        display_model_selection_menu(config)
    
    elif choice == '2':  # Hardware configuration
        display_hardware_menu()
    
    elif choice == '3':  # Binary management
        display_binary_management_menu()
    
    elif choice == '4':  # Start server
        display_server_start_menu(config, app)
    
    elif choice == '5':  # Display current configuration
        display_current_config(config)
    
    elif choice.lower() == 'x':  # Exit and Save
        if confirm_action("exit the program"):
            from llama_legacy_serve import save_json_config  # Import the save function
            save_json_config(config)  # Save config before exit
            return False  # Returning False breaks the main loop

    return True  # Continue the loop


# Model selection menu and handling
def display_model_selection_menu(config):
    print_script_header("model_selection")
    model_dir = config.get("MODEL_DIR", "./models")
    models = list_models(model_dir)

    for idx, model in enumerate(models, start=1):
        print(f"{idx}. {model}")
    
    model_choice = input("Selection; Menu Options = 1-#, Back to Main = B: ")

    if model_choice.lower() != 'b':
        model_idx = int(model_choice) - 1
        if 0 <= model_idx < len(models):
            config['model'] = models[model_idx]
            from llama_legacy_serve import save_json_config
            save_json_config(config)
            print(f"Model selected: {os.path.basename(config['model'])}")
        else:
            print("Invalid model selection.")

# Hardware configuration menu and handling
def display_hardware_menu():
    while True:
        print_script_header("hardware")
        print("1. GPU Settings")
        print("2. CPU Settings")
        print("3. Auto-Detect Hardware")

        hw_choice = input("Selection; Menu Options = 1-3, Back to Main = B: ")

        if hw_choice.lower() == 'b':
            break
        elif hw_choice == '1':
            print("Configuring GPU settings...")
        elif hw_choice == '2':
            print("Configuring CPU settings...")
        elif hw_choice == '3':
            print("Auto-detecting hardware...")

# Binary management menu and handling
def display_binary_management_menu():
    while True:
        print_script_header("binary_management")
        print("1. Install Binary")
        print("2. Remove Binary")
        print("3. Update Binaries")
        
        bin_choice = input("Selection; Menu Options = 1-3, Back to Main = B: ")

        if bin_choice.lower() == 'b':
            break
        elif bin_choice == '1':
            binary_name = input("Enter the name of the binary to install: ")
            install_binary(binary_name)
        elif bin_choice == '2':
            binary_name = input("Enter the name of the binary to remove: ")
            remove_binary(binary_name)
        elif bin_choice == '3':
            update_binaries()

# Server start menu and handling
def display_server_start_menu(config, app):
    print_script_header("server_start")
    print(f"Selected model: {config.get('model', 'None')}")
    print("Press any key to start the server, or 'b' to go back.")

    start_choice = input("Selection; Menu Options = B to go back: ")

    if start_choice.lower() != 'b':
        print("Starting server...")
        app.run(host='0.0.0.0', port=1234)

# Current configuration display
def display_current_config(config):
    print_script_header("current_config")
    print(json.dumps(config, indent=4))

# Confirmation prompt
def confirm_action(action):
    return input(f"Are you sure you want to {action}? (y/n): ").lower() == 'y'

# Helper to list models
def list_models(model_dir):
    models = []
    for root, dirs, files in os.walk(model_dir):
        for file in files:
            if file.lower().endswith((".ggml", ".bin", ".gguf")):
                models.append(os.path.join(root, file))
    return models

# Helper to clear the screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
