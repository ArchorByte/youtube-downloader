import config
import os
import re
import time

# Input to select a folder with a retry system.
def folder_input():
    app_config = config.get_config_data()                                          # Retrieve the configured data.
    default_configured_path = app_config.get("default_download_destination", "./") # Default configured download path.

    script_path = os.path.abspath(__file__)       # Detect the path to the main.py script.
    directory_path = os.path.dirname(script_path) # Determine the path to the program's folder using the script path.

    # Select the main directory if the default configured path is not valid.
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
def remove_invalid_characters(input):
    output = re.sub(r"[<>:\"/\\|?*]", "", input)
    output = output if output else "A very cool video" # Check the output is not empty.

    return output


# Download streams with an attempts system.
def download_stream(stream, file_name):
    app_config = config.get_config_data()                    # Retrieve the configured data.
    max_retries = app_config.get("max_download_retries", 10) # Default configured amount of retries before aborting.
    max_retries = max_retries if max_retries >= 1 and max_retries <= 100 else 10 # We set it to 10 if the configured amount is not valid.
    i = 0

    while (i < max_retries):
        try:
            stream.download(filename = file_name, max_retries = max_retries)
            return True
        except Exception as error:
            print(f"\nDownload attempt {i + 1}/{max_retries} failed with error {error}!")
            remove_if_exists(file_name) # Remove the created file before resuming.
            time.sleep(3)               # Wait 3 seconds before trying again.
        i += 1

    return False


# Download progress callback handler.
def download_progress(stream, chunk, remaining_bytes):
    file_size = stream.filesize
    downloaded_bytes = file_size - remaining_bytes
    percentage = downloaded_bytes / file_size * 100

    filled = int(20 * downloaded_bytes / file_size)       # Calculate the amount of "filled characters" to display in the bar.
    empty = 20 - filled                                   # The rest of the bar is set as whitespaces. The bar is 20 characters long.
    progress_bar = "[" + "█" * filled + " " * empty + "]" # Render the bar.

    print(f"\rDownload progress: {percentage:.0f}% {progress_bar} ({downloaded_bytes / 1000000:.2f}MB/{file_size / 1000000:.2f}MB).", end = "", flush = True)
