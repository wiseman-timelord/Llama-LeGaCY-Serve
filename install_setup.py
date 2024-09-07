# Script: .\install_setup.py - the standalone setup-installer for `Llama-Legacy-Serve`.

import os, subprocess, json

# Global variables
DATA_FOLDER = ".\\data"
PERSISTENCE_TXT = os.path.join(DATA_FOLDER, "persistence.txt")
PYTHON_EXE_TO_USE = None  # Will be updated dynamically

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_script_header():
    """Prints the main header for the script."""
    clear_screen()
    print("=" * 120)
    print("    Install-Setup")
    print("=" * 120)
    print("\n")

def read_python_exe_from_persistence():
    """Reads the Python executable path from persistence.txt."""
    global PYTHON_EXE_TO_USE
    if os.path.exists(PERSISTENCE_TXT):
        with open(PERSISTENCE_TXT, "r") as file:
            PYTHON_EXE_TO_USE = file.readline().strip()
        if os.path.exists(PYTHON_EXE_TO_USE):
            print(f"Using Python from persistence.txt: {PYTHON_EXE_TO_USE}")
        else:
            print(f"Error: Python path not valid: {PYTHON_EXE_TO_USE}")
            raise FileNotFoundError(f"Python executable not found: {PYTHON_EXE_TO_USE}")
    else:
        print(f"Error: persistence.txt not found.")
        raise FileNotFoundError(f"persistence.txt not found at {PERSISTENCE_TXT}")

def install_python_libraries():
    """Installs the main Python requirements."""
    print_script_header()  # Reprint header before beginning the process
    print("Installing Python Libraries...\n")
    requirements_main = os.path.join(DATA_FOLDER, 'requirements_main.txt')
    if os.path.exists(requirements_main):
        subprocess.run([PYTHON_EXE_TO_USE, "-m", "pip", "install", "-r", requirements_main])
        subprocess.run([PYTHON_EXE_TO_USE, "-m", "pip", "check"])
        print(f"Installed Python libraries from {requirements_main}")
    else:
        print(f"Error: {requirements_main} not found!")

def detect_and_install_binaries():
    """Function to detect and install both CPU and GPU binaries."""
    print_script_header()  # Reprint header before beginning the process
    print("Detecting and Installing CPU and GPU Binaries...\n")
    # Logic for detecting and installing both CPU and GPU binaries goes here

def main_menu():
    """Main menu loop for LMS-Local Setup."""
    while True:
        print_script_header()
        print("    1. Install Python Libraries")
        print("    ./data/requirements_main.txt\n")
        print("    2. Detect and Install, Binaries\n\n")
        print("")
        print("=" * 120)
        choice = input("Selection; Menu Options = 1-2, Exit Setup-Install = X: ").strip().lower()

        if choice == '1':
            install_python_libraries()
        elif choice == '2':
            detect_and_install_binaries()
        elif choice == 'x':
            print("Exiting setup...")
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    """Main function to initialize the setup."""
    try:
        read_python_exe_from_persistence()  # Load the Python executable from persistence.txt
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Run the main menu
    main_menu()

if __name__ == "__main__":
    main()
