import os
import subprocess
import urllib.request
import zipfile
import shutil
import sys
import config

# Check if ffmpeg is installed on this device, depending on the host operating system.
def check_installation(system):
    if system == "Windows":
        if not os.path.isfile("./ffmpeg.exe"):
            print("ffmpeg isn't installed!")
            windows_installation()

    elif system == "Linux":
        # Android devices.
        if os.path.exists("/system/build.prop"):
            if not os.path.isfile("./ffmpeg"):
                print("ffmpeg isn't installed!")
                android_installation()
        else:
            package_manager = None
            ffmpeg_installed = False

            # Supported linux package managers.
            commands = {
                0: ["dpkg", "-s", "ffmpeg"],
                1: ["rpm", "-q", "ffmpeg"],
                2: ["pacman", "-Qi", "ffmpeg"],
                3: ["snap", "list", "ffmpeg"]
            }

            # Try each package manager until we find a valid one.
            for i in range(len(commands)):
                try:
                    command = commands[i] # Select a package manager.
                    request = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE) # Try to use it.
                    package_manager = i # Select this package manager if the command didn't fail.

                    # If the command was successful, ffmpeg is installed.
                    if request.returncode == 0:
                        ffmpeg_installed = True
                        break
                except:
                    print("", end = "")

            os.system("clear")

            if package_manager == None:
                print("This program doesn't support your package manager!")
                input("Press [Enter] to close the program..")
                sys.exit()
            elif not ffmpeg_installed:
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
        print("This program doesn't support your operating system!")
        sys.exit()


# Install ffmpeg on Windows devices.
def windows_installation():
    allowed = input(f"Do you allow the installation of ffmpeg? (y/n) ")

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
        zip.close()          # Free the archive.

    shutil.move("./ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe", "./") # Extract the ffmpeg.exe file from the other files.
    shutil.rmtree("./ffmpeg-master-latest-win64-gpl")                    # Delete all other files as we don't need them.
    os.remove("./ffmpeg.zip")                                            # Delete the original zip file.

    print("ffmpeg installation completed, enjoy!", end = "\n\n")


# Install ffmpeg for Android devices.
def android_installation():
    allowed = input(f"Do you allow the installation of ffmpeg? (y/n) ")

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
        zip.close()          # Free the archive.

    shutil.move("./prebuilt-binaries/armeabi-v7a-neon/ffmpeg", "./") # Extract the "ffmpeg" executable file from the others.
    shutil.rmtree("./prebuilt-binaries")                             # Delete all other files as we don't need them.
    os.remove("./ffmpeg.zip")                                        # Delete the original zip file.

    print("ffmpeg installation completed, enjoy!", end = "\n\n")


# Download progress callback.
def download_progress(block_number, block_size, total_size):
    app_config = config.get_config_data()
    bar_length = app_config.get("download_bars_length", 20)
    bar_length = bar_length if bar_length > 0 and bar_length <= 100 else 20

    downloaded_bytes = block_number * block_size
    percentage = downloaded_bytes / total_size * 100

    filled = int(20 * downloaded_bytes / total_size)      # Calculate the amount of "filled characters" to put in the bar.
    empty = 20 - filled                                   # The rest of the bar is set as whitespaces.
    progress_bar = "[" + "█" * filled + " " * empty + "]" # Render the text bar.

    print(f"\rDownload progress: {percentage:.0f}% {progress_bar} ({downloaded_bytes / 1000000:.2f}MB/{total_size / 1000000:.2f}MB).", end = "", flush = True)


# Install ffmpeg on Linux devices.
def linux_installation(package_manager):
    allowed = input(f"Do you allow the installation of ffmpeg? (y/n) ")

    if not allowed.lower() == "y":
        print("Aborted.")
        sys.exit() # End the program

    # APT (DPKG) package manager.
    if package_manager == 0:
        os.system("sudo apt install ffmpeg -y")

    # RPM package managers (DNF or YUM).
    elif package_manager == 1:
        try:
            # Add the RPM fusion repositories using DNF to be able to install ffmpeg.
            os.system("sudo dnf -y install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm")
            os.system("sudo dnf -y install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm")
            os.system("sudo dnf install ffmpeg -y")

        # If the DNF command failed, we try again using YUM.
        except:
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

    if not allowed.lower() == "y":
        print("Aborted.")
        sys.exit() # End the program.

    try:
        subprocess.check_call(["brew", "--version"]) # Check if Homebrew is installed.
    except:
        print("The Homebrew package manager isn't installed!")
        allowed = input("Do you allow the installation of Homebrew? (y/n) ")

        if not allowed.lower() == "y":
            print("Aborted.")
            sys.exit() # End the program.

        # Install Homebrew from GitHub.
        os.system("/bin/bash -c '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'")
        print("Homebrew installation completed!", end = "\n\n")

    print("Installing ffmpeg..")
    os.system("brew install ffmpeg") # Install ffmpeg using Homebrew.
    print("ffmpeg installation completed, enjoy!", end = "\n\n")
