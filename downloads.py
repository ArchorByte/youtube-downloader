import config # config.py
import subprocess
import os
import requests
import re
import shutil
from pytubefix import request

# Retrieve config data.
app_config = config.get_config_data()

script_path = os.path.abspath(__file__)       # Detect the path to this script.
directory_path = os.path.dirname(script_path) # Determine the path to the program's folder using the script path.

# We select the configured default download path if it's valid.
# Otherwise, we select the directory where the program is located.
default_config_path = app_config.get("default_download_destination", "./")
default_download_path = default_config_path if os.path.exists(default_config_path) else directory_path

request.default_range_size = app_config.get("pytube_range_size_bytes", 1024 * 1024) # Amount in bytes of data to download before triggering the progress callback.
max_retries = app_config.get("max_download_retries", 10)                            # Amount of retries allowed on download failure before aborting.

# Input to select a folder.
def folder_input():
    while True:
        folder = input("File location (enter nothing to select the default path): ")
        folder = folder if folder else default_download_path # Take the input (if specified) or take the program path.

        if not os.path.isdir(folder):
            print("This folder doesn't exist! Please, try again!", end = "\n\n")
        else:
            return folder



# Get and display all available resolutions of a YouTube video.
def display_resolutions(youtube_video):
    available_resolutions = []

    # Check each resolution available.
    for video in youtube_video.streams:
        if video.resolution is not None and video.resolution not in available_resolutions:
            available_resolutions.append(video.resolution) # Add the resolution in the list if it's valid and not already in it.

    available_resolutions = sorted(available_resolutions, key = lambda x: int(x[:-1])) # Sort the resolutions in order.
    show_resolutions = ", ".join(available_resolutions)                                # Format the output into a string list.

    print(f"\nAvailable resolutions: {show_resolutions}")
    return available_resolutions



# Download an entire YouTube video (video + audio).
def download_video(youtube_video, system):
    download_directory = folder_input()

    print("Looking for available resolutions for your video..")
    available_resolutions = display_resolutions(youtube_video) # List containing every resolutions available for that video.

    # We select the default download resolution in the config file if it's valid.
    # Otherwise, we select the highest resolution available.
    default_resolution = app_config.get("default_download_resolution")
    default_resolution = default_resolution if default_resolution in available_resolutions else available_resolutions[-1]

    while True:
        resolution = input("Choose a resolution (enter nothing to select " + default_resolution + "): ")
        resolution = resolution if resolution else default_resolution

        # Add a "p" at the end of the input if missing to allow the user to enter "1080" for "1080p" for example.
        if not resolution.endswith("p"):
            resolution += "p"

        if resolution not in available_resolutions: # Invalid resolution entered.
            print(f"Unavailable resolution! Please, try again.", end = "\n\n")
        else:
            print("\nPreparing your download.. Download speed depends on your internet connection.");
            break

    # To bypass the limitation, we are going to download the video and its audio separately.
    # We do this even on resolutions with built-in audio to select the best audio as possible.
    # Once it's done, we assemble the video file and audio file using ffmpeg to finally have the entire video ready.

    video = youtube_video.streams.filter(resolution = resolution, only_video = True).first() # Select the video source.
    audio = youtube_video.streams.filter(only_audio = True).order_by("abr").desc().first()   # Select the audio source that has the best bitrate.

    youtube_video.register_on_progress_callback(download_progress) # Get the download progress data.
    extension = audio.mime_type.split("/")[-1]                     # Retrieve the audio file extension.

    # Remove the video source file if it already exists.
    if os.path.exists("video_source.mp4"):
        os.remove("video_source.mp4")

    # Remove the audio source file if it already exists
    if os.path.exists(f"audio_source.{extension}"):
        os.remove(f"audio_source.{extension}")

    video.download(filename = "video_source.mp4", max_retries = max_retries) # Download the video source.
    audio.download(filename = f"audio_source.{extension}", max_retries = max_retries) # Download the audio source.

    print("\nAssembling audio and video..", end = "\n\n")
    ffmpeg = "ffmpeg" # Default command.

    # Change the command depending on the operating system.
    if system == "Windows":
        ffmpeg = "ffmpeg.exe"
    elif os.path.exists("/system/build.prop"): # Android systems.
        ffmpeg = "./ffmpeg"

    # Use ffmpeg to assemble the video source file and the audio source file.
    subprocess.run([ffmpeg, "-y", "-i", "video_source.mp4", "-i", f"audio_source.{extension}", "-c:v", "copy", "-c:a", "aac", "output.mp4"], check = True)
    title = re.sub(r"[<>:\"/\\|?*]", "", youtube_video.title) # Remove invalid characters from the video title.

    # If the invalid characters removal emptied the video title, we replace it.
    if not title:
        title = "cool video"

    # Delete source files because we no longer need them.
    os.remove("video_source.mp4")
    os.remove(f"audio_source.{extension}")

    # Rename the "output.mp4" file with the video title.
    os.rename("output.mp4", f"{title}.mp4")

    # Move the file in the folder selected by the user if specified.
    if not download_directory == default_download_path:
        shutil.move(f"./{title}.mp4", download_directory)

    print(f"\nDownload finished: \"{os.path.join(download_directory, f"{title}")}.mp4\"")



# Download the audio of a YouTube video.
def download_audio(youtube_video):
    download_directory = folder_input()

    audio = youtube_video.streams.filter(only_audio = True).order_by("abr").desc().first() # Select the audio of the video that has the best bitrate.
    print("Preparing your download.. Download speed depends on your internet connection.")

    youtube_video.register_on_progress_callback(download_progress) # Get the download progress data.
    extension = audio.mime_type.split("/")[-1]                     # Retrieve the audio file extension.

    title = re.sub(r"[<>:\"/\\|?*]", "", youtube_video.title)                                                      # Remove invalid characters from the video title.
    audio.download(filename = f"{title}.{extension}", output_path = download_directory, max_retries = max_retries) # Download the audio file.

    print(f"\n\nDownload finished: \"{os.path.join(download_directory, f"{title}")}.{extension}\"")



# Download progress callback.
def download_progress(stream, chunk, remaining):
    file_size = stream.filesize
    downloaded_bytes = file_size - remaining
    percentage = downloaded_bytes / file_size * 100

    filled = int(20 * downloaded_bytes / file_size) # Calculate the amount of "filled characters" to display in the bar.
    empty = 20 - filled                             # The rest of the bar is set as whitespaces. The bar is 20 characters whatsoever.
    bar = "[" + "█" * filled + " " * empty + "]"    # Render the bar.

    print(f"\rDownload progress: {percentage:.0f}% {bar} ({downloaded_bytes / 1000000:.2f}MB/{file_size / 1000000:.2f}MB).", end = "", flush = True)



# Download the thumbnail of a YouTube video.
def download_thumbnail(thumbnail, title):
    download_directory = folder_input()

    print("Preparing your download.. Download speed depends on your internet connection.")
    http_request = requests.get(thumbnail) # Try to retrieve the thumbnail data.

    if http_request.status_code == 200:
        title = re.sub(r"[<>:\"/\\|?*]", "", title) # Removing invalid characters from the video title.

        # Create a new file.
        with open(f"{title}.png", "wb") as file:
            file.write(http_request.content) # Write the request data into a file.

            # Move the file in the folder selected by the user if specified.
            if not download_directory == default_download_path:
                shutil.move(f"./{title}.png", download_directory)

            file.close() # Free the file.
            print(f"\nDownload finished: \"{os.path.join(download_directory, f"{title}")}.png\"")
    else:
        print(f"\nRequest failed with code {http_request.status_code}.")
