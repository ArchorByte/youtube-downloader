import config
import os
import platform
import pytubefix
import re
import time

def folder_input() -> str:
    """
    Input made to the user to select a path to a folder.

    Tasks:
        1) Verify the default download path value.
        2) Make the input.
        3) If valid, sanitize it and return it.

    Parameters:
        No parameters.

    Returns:
        A string containing a valid path.
    """

    app_config = config.get_config_data()
    app_directory_path = os.getcwd()
    default_configured_path = app_config.get("default_download_destination", app_directory_path)
    default_download_path = default_configured_path if os.path.exists(default_configured_path) else app_directory_path

    while True:
        folder = input("File location (enter nothing to select the default path): ")
        folder = folder if folder else default_download_path

        if not os.path.isdir(folder):
            print("This folder doesn't exist! Please, try again!", end = "\n\n")
        else:
            folder = os.path.abspath(folder)
            return folder


def remove_if_exists (
    file_path: str
) -> None:
    """
    Safely remove a file if it exists.

    Tasks:
        1) Check that the file exists and it's really a file (not a directory for instance).
        2) Delete the file.

    Parameters:
        - file_path / str / Path to the targeted file.

    Returns:
        No object returned.
    """

    if os.path.isfile(file_path):
        os.remove(file_path)


def remove_invalid_characters (
    input_string: str
) -> str:
    """
    Remove characters that can't be used for a file from an input.

    Tasks:
        1) Remove the characters.
        2) Verify if the output isn't empty.

    Parameters:
        - input / str / Input text to normalize.

    Returns:
        A string containing the normalized input.
    """

    output = re.sub(r"[<>:\"/\\|?*]", "", input_string)
    output = output if output else "A very cool video"

    return output


def download_stream (
    stream:    pytubefix.Stream,
    file_name: str
) -> None:
    """
    Download a YouTube stream with an attempts system.

    Tasks:
        1) Verify the configuration values.
        2) Try to download the stream.
        3) Cooldown and retry on failure.

    Parameters:
        - stream    / Stream / Targeted stream to download.
        - file_name / str    / Name of the output file.

    Returns:
        No object returned.
    """

    app_config = config.get_config_data()
    i = 0
    max_retries = app_config.get("max_download_retries", 10)
    max_retries = max_retries if max_retries >= 1 and max_retries <= 100 else 10
    retry_cooldown = app_config.get("retry_cooldown", 3)
    retry_cooldown = retry_cooldown if retry_cooldown >= 0 and retry_cooldown <= 60 else 3

    for i in range(max_retries):
        try:
            stream.download(filename = file_name)
            return
        except Exception as error:
            print(f"\nDownload attempt {i + 1}/{max_retries} failed with error {error}!", end = "\n\n")
            time.sleep(retry_cooldown)

    raise ValueError(f"Download failed! Too many failures ({max_retries}/{max_retries}).")


def download_progress (
    stream:          pytubefix.Stream,
    chunk:           bytes,
    remaining_bytes: int
) -> None:
    """
    Display the progress of the download of a stream.

    Tasks:
        1) Verify the configuration values.
        2) Calculate the download status.
        3) Make the progress bar.
        4) Display all relevant data.

    Parameters:
        - stream          / Stream / Stream being downloaded.
        - chunk           / bytes  / Bytes of the last downloaded data chunk (not used but necessary in this order).
        - remaining_bytes / int    / Amount of bytes remaining to complete the download.

    Returns:
        No object returned.
    """

    app_config = config.get_config_data()
    bar_length = app_config.get("download_bars_length", 20)
    bar_length = bar_length if bar_length > 0 and bar_length <= 100 else 20

    file_size = stream.filesize
    downloaded_bytes = file_size - remaining_bytes
    percentage = downloaded_bytes / file_size * 100

    filled = int(bar_length * downloaded_bytes / file_size)
    empty = bar_length - filled
    progress_bar = "[" + "█" * filled + " " * empty + "]"
    percentage_display = f"{int(percentage):02d}" # UI format (1 -> 01 ; 2 -> 02 ; 10 -> 10)

    print(f"\rDownload progress: {percentage_display}% {progress_bar} ({downloaded_bytes / 1000000:.2f}MB/{file_size / 1000000:.2f}MB).", end = "", flush = True)


def ffmpeg_command_keyword () -> str:
    """
    Determine the FFmpeg keyword command that we have to use.

    Tasks:
        1) Return the keyword command depending on the OS.

    Parameters:
        - system / str / Operating system name we are running on.

    Returns:
        A string containing the FFmpeg keyword command to use.
    """

    system = platform.system()

    if system == "Windows":
        return "ffmpeg.exe"
    elif os.path.exists("/system/build.prop"): # Android systems.
        return "./ffmpeg"
    else:
        return "ffmpeg"
