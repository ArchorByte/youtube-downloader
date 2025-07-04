import os
import subprocess
import urllib.request
import zipfile
import shutil
import sys

# Check if ffmpeg is installed on this device, depending on the host operating system.
def check_installation(system):
    if system == "Windows":
        # Check if any "ffmpeg.exe" file is present in this folder.
        if not os.path.isfile("./ffmpeg.exe"):
            print("ffmpeg isn't installed!")
            windows_installation()
    elif system == "Linux":
        # Android devices.
        if os.path.exists("/system/build.prop"):
            # Check if any "ffmpeg" is present in this folder.
            if not os.path.isfile("./ffmpeg"):
                print("ffmpeg isn't installed!")
                android_installation()

        # Linux devices.
        else:
            package_manager = None
            installed = False

            # Supported linux package managers.
            commands = {
                0: ["dpkg", "-s", "ffmpeg"],    # APT package manager.
                1: ["rpm", "-q", "ffmpeg"],     # RPM package managers (DNF or YUM).
                2: ["pacman", "-Qi", "ffmpeg"], # PACMAN package manager.
                3: ["snap", "list", "ffmpeg"]   # SNAP package manager.
            }

            # Try each package manager until we find an available package manager.
            for i in range(len(commands)):
                try:
                    command = commands[i]                                                               # Select a package manager in the commands list.
                    fetch = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE) # Try to use the package manager.
                    package_manager = i

                    # If the command is successful, we select the package manager.
                    if fetch.returncode == 0:
                        installed = True
                        break
                except:
                    print("", end = "")

            # Clear the terminal.
            os.system("clear")

            if package_manager == None:
                # To add your package manager, you can edit the code and make a pull request to https://github.com/archorbyte/youtube-downloader.
                print("This program doesn't support your package manager!")
                input("Press [Enter] to close the program..")
                sys.exit()
            elif not installed:
                print("ffmpeg isn't installed!")
                linux_installation(package_manager)

    # MacOS devices.
    elif system == "Darwin":
        try:
            subprocess.check_call(["ffmpeg", "--version"]) # Try to use the ffmpeg command.
            os.system("clear")
        except:
            os.system("clear")
            print("ffmpeg isn't installed!")
            macos_installation()
    else:
        # To add your OS, you can edit the code and make a pull request to https://github.com/archorbyte/youtube-downloader.
        print("This program doesn't support your operating system!")
        sys.exit()



# Install ffmpeg on Windows devices.
def windows_installation():
    allowed = input(f"Do you allow the installation of ffmpeg? (y/n) ")

    # Installation cancelled by the user or invalid input.
    if not allowed.lower() == "y":
        print("Aborted by the user!")
        sys.exit() # End the program.

    print("Downloading the latest version of ffmpeg..")

    # Download the latest ffmpeg version from GitHub and get the download progress data.
    download_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    urllib.request.urlretrieve(download_url, "ffmpeg.zip", reporthook = download_progress)

    print("\nInstalling ffmpeg..")

    # Open the archive in read-only mode.
    with zipfile.ZipFile("ffmpeg.zip", "r") as zip:
        zip.extractall("./") # Extract the files.

    shutil.move("./ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe", "./") # Extract the ffmpeg.exe file from the others.
    shutil.rmtree("./ffmpeg-master-latest-win64-gpl")                    # Delete all other files because we don't need them.
    os.remove("./ffmpeg.zip")                                            # Delete the original zip file.

    print("ffmpeg installation completed, enjoy!", end = "\n\n")



# Install ffmpeg for Android devices.
def android_installation():
    allowed = input(f"Do you allow the installation of ffmpeg? (y/n) ")

    # Installation cancelled by the user or invalid input.
    if not allowed.lower() == "y":
        print("Aborted.")
        sys.exit() # End the program.

    print("Downloading ffmpeg for Android..")

    # Download the latest Android known version of ffmpeg from GitHub and get the download progress data.
    download_url = "https://github.com/cropsly/ffmpeg-android/releases/download/v0.3.4/prebuilt-binaries.zip"
    urllib.request.urlretrieve(download_url, "ffmpeg.zip", reporthook = download_progress)

    print("\nInstalling ffmpeg..")

    # Open the archive in read-only mode.
    with zipfile.ZipFile("ffmpeg.zip", "r") as zip:
        zip.extractall("./") # Extract the files.

    shutil.move("./prebuilt-binaries/armeabi-v7a-neon/ffmpeg", "./") # Extract the "ffmpeg" executable file from the others.
    shutil.rmtree("./prebuilt-binaries")                             # Delete all other files because we don't need them.
    os.remove("./ffmpeg.zip")                                        # Delete the original zip file.

    print("ffmpeg installation completed, enjoy!", end = "\n\n")



# Download progress callback.
def download_progress(block_number, block_size, total_size):
    downloaded_bytes = block_number * block_size
    percentage = downloaded_bytes / total_size * 100

    filled = int(20 * downloaded_bytes / total_size) # Calculate the amount of "filled characters" to display in the bar.
    empty = 20 - filled                              # The rest of the bar is set as whitespaces. The bar is 20 characters whatsoever.
    bar = "[" + "█" * filled + " " * empty + "]"     # Render the bar.

    print(f"\rDownload progress: {percentage:.0f}% {bar} ({downloaded_bytes / 1000000:.2f}MB/{total_size / 1000000:.2f}MB).", end = "", flush = True)



# Install ffmpeg on Linux devices.
def linux_installation(package_manager):
    allowed = input(f"Do you allow the installation of ffmpeg? (y/n) ")

    # Installation cancelled by the user or invalid input.
    if not allowed.lower() == "y":
        print("Aborted.")
        sys.exit() # End the program

    # APT package manager.
    if package_manager == 0:
        os.system("sudo apt install ffmpeg -y")

    # RPM package managers (DNF or YUM).
    elif package_manager == 1:
        try:
            # Add the RPM fusion repositories using DNF to be able to install ffmpeg.
            os.system("sudo dnf -y install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm")
            os.system("sudo dnf -y install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm")

            os.system("sudo dnf install ffmpeg -y")

        # If the DNF command failed, we try again using YUM this time.
        except:
            os.system("clear")

            # Add the RPM fusion repositories using YUM to be able to install ffmpeg.
            os.system("sudo yum localinstall --nogpgcheck https://download1.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm")
            os.system("sudo yum localinstall --nogpgcheck https://download1.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-$(rpm -E %rhel).noarch.rpm")

            os.system("sudo yum install ffmpeg -y")

    # PACMAN package manager.
    elif package_manager == 2:
        os.system("sudo pacman -S ffmpeg")

    # SNAP package manager.
    elif package_manager == 3:
        os.system("sudo snap install ffmpeg")

    print("ffmpeg installation completed, enjoy!", end = "\n\n")



# Install ffmpeg on MacOS devices.
def macos_installation():
    allowed = input(f"Do you allow the installation of ffmpeg? (y/n) ")

    # Installation cancelled by the user or invalid inputs.
    if not allowed.lower() == "y":
        print("Aborted.")
        sys.exit() # End the program.

    try:
        subprocess.check_call(["brew", "--version"]) # Check if Homebrew is installed.
    except:
        print("The Homebrew package manager isn't installed!")
        allowed = input("Do you allow the installation of Homebrew? (y/n) ")

        # Installation cancelled by the user or invalid inputs.
        if not allowed.lower() == "y":
            print("Aborted.")
            sys.exit() # End the program.

        # Install Homebrew from GitHub.
        os.system("/bin/bash -c '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'")
        print("Homebrew installation completed!", end = "\n\n")

    print("Installing ffmpeg..")
    os.system("brew install ffmpeg") # Install ffmpeg using Homebrew.
    print("ffmpeg installation completed, enjoy!", end = "\n\n")
