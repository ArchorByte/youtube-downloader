import os
import subprocess
import urllib.request
import zipfile
import shutil
import sys

def check_installation(system): # Check if ffmpeg is installed.
    if system == "Windows":
        if not os.path.isfile("./ffmpeg.exe"): # Check if any "ffmpeg.exe" file is available.
            print("ffmpeg isn't installed!")
            windows_installation()
    elif system == "Linux":
        if os.path.exists("/system/build.prop"): # Android device.
            if not os.path.isfile("./ffmpeg"): # Check if any "ffmpeg" is available.
                print("ffmpeg isn't installed!")
                android_installation()
        else:
            package_manager = None
            installed = False

            # Supported linux package managers.
            commands = {
                0: ["dpkg", "-s", "ffmpeg"], # apt
                1: ["rpm", "-q", "ffmpeg"], # dnf or yum
                2: ["pacman", "-Qi", "ffmpeg"], # pacman
                3: ["snap", "list", "ffmpeg"] # snap
            }

            for i in range(len(commands)): # Try each package manager.
                try:
                    command = commands[i]
                    fetch = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE) # Try to use the package manager.

                    if fetch.returncode == 0: # The command is successful.
                        package_manager = i
                        installed = True
                except:
                    print("", end = "")

            os.system("clear") # Clear the terminal.

            if package_manager == None:
                # To add your package manager, you can edit the code and send a pull request to https://github.com/archorbyte/youtube-downloader.
                print("This program doesn't support your package manager!")
                input("Press [Enter] to close the program..")
                sys.exit()
            elif not installed:
                print("ffmpeg isn't installed!")
                linux_installation(package_manager)
    elif system == "Darwin": # MacOS.
        try:
            subprocess.check_call(["ffmpeg", "--version"])
            os.system("clear")
        except:
            os.system("clear")
            print("ffmpeg isn't installed!")
            macos_installation()
    else:
        # To add your OS, you can edit the code and send a pull request to https://github.com/archorbyte/youtube-downloader.
        print("This program doesn't support your operating system!")
        sys.exit()


def windows_installation(): # Install ffmpeg for Windows systems.
    allowed = input(f"Do you allow the installation of ffmpeg? (y/n) ")

    if not allowed.lower() == "y": # Installation cancelled by the user or input invalid.
        print("Aborted.")
        sys.exit() # End the program.

    print("Downloading the latest version of ffmpeg..")
    # Download the latest version from GitHub and get the download progress report.
    urllib.request.urlretrieve("https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip", "ffmpeg.zip", reporthook = download_progress)

    print("\nInstalling ffmpeg..")

    # Open the archive in read-only mode.
    with zipfile.ZipFile("ffmpeg.zip", "r") as zip:
        zip.extractall("./") # Extract the files in the current directory.

    shutil.move("./ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe", "./") # Extract the ffmpeg.exe file.
    shutil.rmtree("./ffmpeg-master-latest-win64-gpl") # Delete all other files because we don't need them.
    os.remove("./ffmpeg.zip") # Delete the zip file.
    print("ffmpeg installation completed, enjoy!", end = "\n\n")


def android_installation(): # Install ffmpeg for Android systems.
    allowed = input(f"Do you allow the installation of ffmpeg? (y/n) ")

    if not allowed.lower() == "y": # Installation cancelled by the user or input invalid.
        print("Aborted.")
        sys.exit() # End the program.

    print("Downloading ffmpeg for Android..")
    # Download the latest known version from GitHub and get the download progress report.
    urllib.request.urlretrieve("https://github.com/cropsly/ffmpeg-android/releases/download/v0.3.4/prebuilt-binaries.zip", "ffmpeg.zip", reporthook = download_progress)

    print("\nInstalling ffmpeg..")

    # Open the archive in read-only mode.
    with zipfile.ZipFile("ffmpeg.zip", "r") as zip:
        zip.extractall("./") # Extract the files.

    shutil.move("./prebuilt-binaries/armeabi-v7a-neon/ffmpeg", "./") # Extract the "ffmpeg" executable file.
    shutil.rmtree("./prebuilt-binaries") # Delete all other files because we don't need them.
    os.remove("./ffmpeg.zip") # Delete the zip file.
    print("ffmpeg installation completed, enjoy!", end = "\n\n")


def download_progress(block_number, block_size, total_size): # Download progress report.
    downloaded = block_number * block_size # Calculate the amount of downloaded bytes.
    percentage = downloaded / total_size * 100 # Calculate the progress made so far in percentage.

    filled = int(20 * downloaded / total_size) # Calculate the amount of "filled" characters to display.
    empty = 20 - filled
    bar = "[" + "█" * filled + " " * empty + "]" # Render the bar.

    print(f"\rDownload progress: {percentage:.0f}% {bar} ({downloaded / 1000000:.2f}MB/{total_size / 1000000:.2f}MB).", end = "", flush = True)


def linux_installation(package_manager): # Install ffmpeg on Linux devices.
    allowed = input(f"Do you allow the installation of ffmpeg? (y/n) ")

    if not allowed.lower() == "y": # Installation cancelled by the user or input invalid.
        print("Aborted.")
        sys.exit() # End the program

    if package_manager == 0: # apt
        os.system("sudo apt install ffmpeg -y")
    elif package_manager == 1: # rpm
        # Add the rpmfusion repositories to be able to install ffmpeg.
        os.system("sudo dnf -y install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm")
        os.system("sudo dnf -y install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm")

        try:
            os.system("sudo dnf install ffmpeg -y")
        except: # If the dnf command failed, we try to install it with yum.
            os.system("clear")
            os.system("sudo yum install ffmpeg -y")
    elif package_manager == 2: # pacman
        os.system("sudo pacman -Syu ffmpeg")
    elif package_manager == 3: # snap
        os.system("sudo snap install ffmpeg")

    print("ffmpeg installation completed, enjoy!", end = "\n\n")


def macos_installation():
    allowed = input(f"Do you allow the installation of ffmpeg? (y/n) ")

    if not allowed.lower() == "y": # Installation cancelled by the user or input invalid.
        print("Aborted.")
        sys.exit() # End the program.

    try:
        subprocess.check_call(["brew", "--version"]) # Check if Homebrew is installed.
    except:
        print("The package manager \"Homebrew\" isn't installed!")
        allowed = input("Do you allow the installation of Homebrew? (y/n) ")

        if not allowed.lower() == "y": # Installation cancelled by the user or input invalid.
            print("Aborted.")
            sys.exit() # End the program.

        # Install Homebrew from GitHub.
        os.system("/bin/bash -c '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'") 
        print("Homebrew installation completed!", end = "\n\n")

    print("Installing ffmpeg..")
    os.system("brew install ffmpeg") # Install ffmpeg using Homebew.
    print("ffmpeg installation completed, enjoy!", end = "\n\n")