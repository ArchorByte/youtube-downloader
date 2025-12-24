import config
import os
import platform
import shutil
import subprocess
import urllib.request
import zipfile

DPKG = 0
RPM = 1
PACMAN = 2
SNAP = 3

def check_installation () -> bool:
    """
    Check if ffmpeg is installed on this device.
    We automatically try to install it if missing (with the user agreement).

    Tasks:
        1) Verify the existence of FFmpeg depending on the operating system.
        2) Try to install FFmpeg if missing.

    Parameters:
        No parameters.

    Returns:
        True if FFmpeg is installed.
        False if not.
    """

    system = platform.system()

    if system == "Windows":
        if not os.path.isfile("./ffmpeg.exe"):
            print("ffmpeg isn't installed!")
            return False
        return True

    elif system == "Linux":
        if os.path.exists("/system/build.prop"): # Android.
            if not os.path.isfile("./ffmpeg"):
                print("ffmpeg isn't installed!")
                return False
            return True

        else:
            commands = [
                ["dpkg", "-s", "ffmpeg"],
                ["rpm", "-q", "ffmpeg"],
                ["pacman", "-Qi", "ffmpeg"],
                ["snap", "list", "ffmpeg"]
            ]

            package_manager = detect_linux_package_manager()
            request = subprocess.run(commands[package_manager], stdout = subprocess.PIPE, stderr = subprocess.PIPE)

            if request.returncode != 0:
                print("ffmpeg isn't installed!")
                return False
            return True

    elif system == "Darwin": # MacOS.
        try:
            subprocess.check_call(["ffmpeg", "--version"])
            return True
        except:
            print("ffmpeg isn't installed!")
            return False

    else:
        raise ValueError("Unsupported operating system!")


def install () -> None:
    """
    Select the correct function to install FFmpeg depending on the operating system we are running on.

    Tasks:
        1) Verify the operating system.
        2) Run the function for the right OS.

    Parameters:
        No parameters.

    Returns:
        No object returned.
    """

    system = platform.system()

    if system == "Windows":
        windows_installation()
    elif system == "Linux":
        if os.path.exists("/system/build.prop"): # Android.
            android_installation()
        else:
            linux_installation()
    elif system == "Darwin": # MacOS.
        macos_installation()
    else:
        raise ValueError("Unsupported operating system!")


def detect_linux_package_manager () -> int:
    """
    Detect the package manager of a Linux distribution.

    Tasks:
        1) Select a command and try it.
        2) If it fails, it's not existing on the computer.

    Parameters:
        No parameters.

    Returns:
        An integer representing a package manager.
    """

    if shutil.which("apt"):
        return DPKG
    elif shutil.which("dnf") or shutil.which("yum"):
        return RPM
    elif shutil.which("pacman"):
        return PACMAN
    elif shutil.which("snap"):
        return SNAP

    raise ValueError("Unsupported package manager!")


def windows_installation() -> None:
    """
    Install FFmpeg on a Windows device.

    Tasks:
        1) Ask permission.
        2) Download the official FFmpeg .zip archive from GitHub.
        3) Retrieve the FFmpeg executable.
        4) Delete all other files.

    Parameters:
        No parameters.

    Returns:
        No object returned.
    """

    authorization = input("Do you allow the installation of FFmpeg on your device? (y/n) ")

    if authorization.lower() != "y":
        raise ValueError("FFmpeg installation aborted by the user!")

    print("Downloading the latest version of FFmpeg..")

    download_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    urllib.request.urlretrieve(download_url, "ffmpeg.zip", reporthook = download_progress)

    print("\nInstalling FFmpeg..")

    with zipfile.ZipFile("ffmpeg.zip", "r") as zip:
        zip.extractall("./")

    shutil.move("./ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe", "./")
    shutil.rmtree("./ffmpeg-master-latest-win64-gpl")
    os.remove("./ffmpeg.zip")

    print("FFmpeg installation completed! Enjoy!", end = "\n\n")


def android_installation () -> None:
    """
    Install FFmpeg on an Android device.

    Tasks:
        1) Ask permission.
        2) Download an Android version of FFmpeg from GitHub.
        3) Retrieve the FFmpeg executable.
        4) Delete all other files.

    Parameters:
        No parameters.

    Returns:
        No object returned.
    """

    authorization = input("Do you allow the installation of FFmpeg on your device? (y/n) ")

    if authorization.lower() != "y":
        raise ValueError("FFmpeg installation aborted by the user!")

    print("Downloading FFmpeg for Android..")

    download_url = "https://github.com/cropsly/ffmpeg-android/releases/download/v0.3.4/prebuilt-binaries.zip"
    urllib.request.urlretrieve(download_url, "ffmpeg.zip", reporthook = download_progress)

    print("\nInstalling FFmpeg..")

    with zipfile.ZipFile("ffmpeg.zip", "r") as zip:
        zip.extractall("./")

    shutil.move("./prebuilt-binaries/armeabi-v7a-neon/ffmpeg", "./")
    shutil.rmtree("./prebuilt-binaries")
    os.remove("./ffmpeg.zip")

    print("FFmpeg installation completed! Enjoy!", end = "\n\n")


def linux_installation () -> None:
    """
    Install FFmpeg on a Linux device.

    Tasks:
        1) Ask permission.
        2) Install FFmpeg using the correct command.

    Parameters:
        No parameters.

    Returns:
        No object returned.
    """

    authorization = input("Do you allow the installation of FFmpeg device? (y/n) ")

    if authorization.lower() != "y":
        raise ValueError("FFmpeg installation aborted by the user!")

    package_manager = detect_linux_package_manager()

    if package_manager == DPKG:
        os.system("sudo apt install ffmpeg -y")
    elif package_manager == RPM:
        try:
            os.system("sudo dnf -y install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm")
            os.system("sudo dnf -y install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm")
            os.system("sudo dnf install ffmpeg -y")
        except: # If the DNF command failed, we try again using YUM.
            os.system("sudo yum localinstall --nogpgcheck https://download1.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm")
            os.system("sudo yum localinstall --nogpgcheck https://download1.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-$(rpm -E %rhel).noarch.rpm")
            os.system("sudo yum install ffmpeg -y")
    elif package_manager == PACMAN:
        os.system("sudo pacman -S ffmpeg")
    elif package_manager == SNAP:
        os.system("sudo snap install ffmpeg")
    else:
        raise ValueError("Unsupported package manager provided!")

    print("FFmpeg installation completed! Enjoy!", end = "\n\n")


def macos_installation () -> None:
    """
    Install FFmpeg on a MacOS device.

    Tasks:
        1) Ask permission.
        2) Check Homebrew installation. If not installed, ask permission and install it from GitHub.
        3) Install FFmpeg using Homebrew.

    Parameters:
        No parameters.

    Returns:
        No object returned.
    """

    authorization = input("Do you allow the installation of FFmpeg on your device? (y/n) ")

    if authorization.lower() != "y":
        raise ValueError("FFmpeg installation aborted by the user!")

    try:
        subprocess.check_call(["brew", "--version"])
    except:
        print("The Homebrew package manager isn't installed!")
        authorization = input("Do you allow the installation of Homebrew on your device? (y/n) ")

        if authorization.lower() != "y":
            raise ValueError("Homebrew installation aborted by the user!")

        os.system("/bin/bash -c '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'")
        print("Homebrew installation completed!", end = "\n\n")

    print("Installing FFmpeg..")
    os.system("brew install ffmpeg")
    print("FFmpeg installation completed! Enjoy!", end = "\n\n")


def download_progress (
    block_number: int,
    block_size:   int,
    total_size:   int
) -> None:
    """
    Download progress bar.

    Tasks:
        1) Verify the bar length value.
        2) Calculate the progress status.
        3) Make the progress bar.
        4) Display all relevant data.

    Parameters:
        - block_number / int / Amount of downloaded blocks.
        - block_size   / int / Size of a block.
        - total_size   / int / Size of the item we are downloading.s

    Returns:
        No object returned.
    """

    app_config = config.get_config_data()
    bar_length = app_config.get("download_bars_length", 20)
    bar_length = bar_length if bar_length > 0 and bar_length <= 100 else 20

    downloaded_bytes = block_number * block_size
    percentage = downloaded_bytes / total_size * 100

    filled_char = int(bar_length * downloaded_bytes / total_size)
    empty_char = bar_length - filled_char
    progress_bar = "[" + "█" * filled_char + " " * empty_char + "]"

    print(f"\rDownload progress: {percentage:.0f}% {progress_bar} ({downloaded_bytes / 1000000:.2f}MB/{total_size / 1000000:.2f}MB).", end = "", flush = True)
