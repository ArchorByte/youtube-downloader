import config
import os
import re
import time

# Input to select a folder with a retry system.
def folder_input():
    app_config = config.get_config_data()
    default_configured_path = app_config.get("default_download_destination", "./")

    script_path = os.path.abspath(__file__)       # Detect the path to the main.py script.
    directory_path = os.path.dirname(script_path) # Determine the path to the program's folder using the main.py path.
    default_download_path = default_configured_path if os.path.exists(default_configured_path) else directory_path

    while True:
        folder = input("File location (enter nothing to select the default path): ")
        folder = folder if folder else default_download_path # Take the input (if specified) or select the default path.

        if not os.path.isdir(folder):
            print("This folder doesn't exist! Please, try again!", end = "\n\n")
        else:
            return folder


# Remove a file if it already exists.
def remove_if_exists(file_path):
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)


# Remove invalid characters from an input.
def remove_invalid_characters(input_text):
    output = re.sub(r"[<>:\"/\\|?*]", "", input_text)
    output = output if output else "A very cool video" # Verify the output.

    return output


# Download streams with an attempts system.
def download_stream(stream, file_name):
    app_config = config.get_config_data()
    i = 0

    max_retries = app_config.get("max_download_retries", 10)
    max_retries = max_retries if max_retries >= 1 and max_retries <= 100 else 10

    retry_cooldown = app_config.get("retry_cooldown", 3)
    retry_cooldown = retry_cooldown if retry_cooldown >= 0 and retry_cooldown <= 60 else 3

    for i in range(max_retries):
        try:
            stream.download(filename = file_name, max_retries = max_retries)
            return True
        except Exception as error:
            print(f"\nDownload attempt {i + 1}/{max_retries} failed with error {error}!", end = "\n\n")
            remove_if_exists(file_name) # Remove the created file before resuming.
            time.sleep(retry_cooldown)  # Wait before trying again.

    return False


# Download progress callback handler.
def download_progress(stream, chunk, remaining_bytes):
    app_config = config.get_config_data()
    bar_length = app_config.get("download_bars_length", 20)
    bar_length = bar_length if bar_length > 0 and bar_length <= 100 else 20

    file_size = stream.filesize
    downloaded_bytes = file_size - remaining_bytes
    percentage = downloaded_bytes / file_size * 100

    filled = int(bar_length * downloaded_bytes / file_size) # Calculate the amount of "filled characters" to put in the bar.
    empty = bar_length - filled                             # The rest of the bar is set as whitespaces.
    progress_bar = "[" + "█" * filled + " " * empty + "]"   # Render the text bar.

    print(f"\rDownload progress: {percentage:.0f}% {progress_bar} ({downloaded_bytes / 1000000:.2f}MB/{file_size / 1000000:.2f}MB).", end = "", flush = True)


# Give the ffmpeg keyword to use to start an ffmpeg command, depending on the operating system.
def ffmpeg_command_keyword(system):
    if system == "Windows":
        return "ffmpeg.exe"
    elif os.path.exists("/system/build.prop"): # Android systems.
        return "./ffmpeg"
    else:
        return "ffmpeg"
