import time
import os
import zipfile
import shutil
import requests

INSTALLED_FILE = "installed.txt"
INSTALLED_DIR = "installed"
PROGRAMS_ZIP_DIR = "programs"

PROGRAMS_ZIP_URL = "https://raw.githubusercontent.com/Kiwi8474/pkgManager/main/programs/approved/"

installedPrograms = []


COMMANDS = {
    "pkg install <program>": "Install a program",
    "pkg uninstall <program>": "Uninstall a program",
    "pkg update": "Update all installed programs",
    "pkg list": "List all installed programs",
    "start <program>": "Start an installed program",
    "help": "Show this help message",
    "q": "Quit the package manager"
}


def load_installed():
    try:
        with open(INSTALLED_FILE, "r") as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []


def save_installed(installed_list):
    with open(INSTALLED_FILE, "w") as f:
        for program in installed_list:
            f.write(program + "\n")


def load_animation(msg, program, seconds=3):
    spin_chars = ['|', '/', '-', '\\']
    end_time = time.time() + seconds
    idx = 0
    while time.time() < end_time:
        print(f"{msg} [ {spin_chars[idx % len(spin_chars)]} ]", end='\r', flush=True)
        idx += 1
        time.sleep(0.2)
    print("\nDone")


def search_animation(program, seconds=5):
    spin_chars = ['|', '/', '-', '\\']
    end_time = time.time() + seconds
    idx = 0
    while time.time() < end_time:
        print(f"Searching for {program} [ {spin_chars[idx % len(spin_chars)]} ]", end='\r', flush=True)
        idx += 1
        time.sleep(0.2)
    print(f"\nFound {program}")


def download_zip(program):
    url = f"{PROGRAMS_ZIP_URL}{program}.zip"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            os.makedirs(PROGRAMS_ZIP_DIR, exist_ok=True)
            zip_path = os.path.join(PROGRAMS_ZIP_DIR, f"{program}.zip")
            with open(zip_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            print(f"{program}: Program not found online.")
            return False
    except Exception as e:
        print(f"Error downloading {program}: {e}")
        return False


def install_zip(program):
    zip_path = os.path.join(PROGRAMS_ZIP_DIR, f"{program}.zip")
    install_path = os.path.join(INSTALLED_DIR, program)
    if os.path.exists(zip_path):
        if os.path.exists(install_path):
            shutil.rmtree(install_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(install_path)
        return True
    return False


def install_program(program):
    global installedPrograms
    if program in installedPrograms:
        print(f"{program} is already installed")
        return
    if not download_zip(program):
        print(f"Zip file for {program} not found online.")
        return
    search_animation(program)
    load_animation(f"{program}.zip: Downloading from online repository", program)
    load_animation(f"{program}: Installing", program)
    if install_zip(program):
        installedPrograms.append(program)
        save_installed(installedPrograms)
    else:
        print(f"{program}: [Error] Could not install")


def remove_program(program):
    global installedPrograms
    install_path = os.path.join(INSTALLED_DIR, program)
    if program in installedPrograms:
        load_animation(f"{program}: Uninstalling", program)
        if os.path.exists(install_path):
            shutil.rmtree(install_path)
        installedPrograms.remove(program)
        save_installed(installedPrograms)
    else:
        print(f"{program}: Is not installed")


def update_programs():
    global installedPrograms
    if not installedPrograms:
        print("No programs installed")
        return
    updated_any = False
    for program in installedPrograms:
        if download_zip(program):
            search_animation(program, 0.5)
            load_animation(f"{program}: Updating from online repository", program)
            if install_zip(program):
                updated_any = True
            else:
                print(f"{program}: [Error] Could not update")
        else:
            print(f"{program}: No updates found")
    if not updated_any:
        print("All installed programs have been updated")
    else:
        print("Update completed")


def start_program(parts):
    program = parts[1]
    if program in installedPrograms:
        program_path = os.path.join(INSTALLED_DIR, program, f"{program}.py")
        if os.path.isfile(program_path):
            with open(program_path) as f:
                code = f.read()
            exec(code, globals())
        else:
            print(f"Program file {program}.py not found in installed folder")
    else:
        print(f"Program: {program} not installed")
        print(f"Try to install with 'pkg install {program}'")


def list_installed():
    global installedPrograms
    if installedPrograms:
        print("Installed programs:")
        for prog in installedPrograms:
            print(f"- {prog}")
    else:
        print("No programs installed.")


def help():
    print("Available commands:")
    for cmd, desc in COMMANDS.items():
        print(f"{cmd:<25} - {desc}")


def main():
    global installedPrograms
    installedPrograms = load_installed()
    while True:
        userInput = input("~$ ")

        if userInput.startswith("pkg install "):
            parts = userInput.split()
            if len(parts) > 2:
                program = parts[2]
                install_program(program)

        elif userInput.startswith("pkg uninstall "):
            parts = userInput.split()
            if len(parts) > 2:
                program = parts[2]
                remove_program(program)

        elif userInput == "pkg update":
            update_programs()

        elif userInput == "pkg list":
            list_installed()

        elif userInput.startswith("start "):
            parts = userInput.split()
            if len(parts) > 1:
                start_program(parts)
        
        elif userInput == "help":
            help()
        elif userInput == "q":
            break

if __name__ == "__main__":
    main()
