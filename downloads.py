import subprocess
import os
import requests
import re
import shutil
from pytubefix import request

script_path = os.path.abspath(__file__)       # Detect the path to this script.
directory_path = os.path.dirname(script_path) # Determine the path to the program's folder using the script path.

request.default_range_size = 1024 * 1024 # We download one MB per MB.
max_retries = 10                         # Allow up to 10 retries if the download failed.

# Input to select a folder.
def folder_input():
    while True:
        folder = input("File location (enter nothing to select the current folder): ")
        folder = folder if folder else directory_path # Take the input (if specified) or take the program path.

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

    # Verify the resolution output.
    while True:
        resolution = input("Choose a resolution: ")

        if resolution not in available_resolutions: # Invalid resolution.
            print(f"Unavailable resolution! Please, try again.", end = "\n\n")
        else:
            print("\nPreparing your download.. Download speed depends on your internet connection.");
            break

    # Resolutions with built-in audio.
    if resolution == "360p":
        video = youtube_video.streams.filter(resolution = resolution).first() # Select the video with the right resolution.

        youtube_video.register_on_progress_callback(download_progress) # Get the download progress data.
        title = re.sub(r"[<>:\"/\\|?*]", "", youtube_video.title)      # Remove invalid characters from the video title.

        video.download(filename = f"{title}.mp4", output_path = directory_path, max_retries = max_retries) # Download the video file.
        print(f"\n\nDownload finished: \"{os.path.join(download_directory, f"{title}")}.mp4\"")

    # Resolutions with missing audio (YouTube limitations).
    else:
        video = youtube_video.streams.filter(resolution = resolution, only_video = True).first() # Select the video source.
        audio = youtube_video.streams.filter(only_audio = True, abr = "128kbps").first()         # Select the audio source (128 kbps for good quality)

        youtube_video.register_on_progress_callback(download_progress)           # Get the download progress data.
        video.download(filename = "video_source.mp4", max_retries = max_retries) # Download the video source.
        audio.download(filename = "audio_source.mp3", max_retries = max_retries) # Download the audio source.

        print("\nAssembling audio and video..", end = "\n\n")
        ffmpeg = "ffmpeg" # Default command.

        # Change the command depending on the operating system.
        if system == "Windows":
            ffmpeg = "ffmpeg.exe"
        elif os.path.exists("/system/build.prop"): # Android systems.
            ffmpeg = "./ffmpeg"

        # Use ffmpeg to assemble the video source file and the audio source file.
        subprocess.run(f"{ffmpeg} -i video_source.mp4 -i audio_source.mp3 -c:v copy -c:a aac output.mp4", shell = True)
        title = re.sub(r"[<>:\"/\\|?*]", "", youtube_video.title) # Remove invalid characters from the video title.

        # Rename the "output.mp4" file with the video title.
        os.rename("output.mp4", f"{title}.mp4")

        # Delete source files because we no longer need them.
        os.remove("video_source.mp4")
        os.remove("audio_source.mp3")

        # Move the file in the folder selected by the user if specified.
        if not directory_path == download_directory:
            shutil.move(f"./{title}.mp4", download_directory)

        print(f"\nDownload finished: \"{os.path.join(download_directory, f"{title}")}.mp4\"")


# Download the audio of a YouTube video.
def download_audio(youtube_video):
    download_directory = folder_input()

    audio = youtube_video.streams.filter(only_audio = True, abr = "128kbps").first() # Select the audio of the video (128 kbps for good quality).
    print("Preparing your download.. Download speed depends on your internet connection.")

    youtube_video.register_on_progress_callback(download_progress) # Get the download progress data.
    title = re.sub(r"[<>:\"/\\|?*]", "", youtube_video.title)      # Remove invalid characters from the video title.

    audio.download(filename = f"{title}.mp3", output_path = download_directory, max_retries = max_retries) # Download the audio file.
    print(f"\n\nDownload finished: \"{os.path.join(download_directory, f"{title}")}.mp3\"")


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
    request = requests.get(thumbnail) # Try to retrieve the thumbnail data.

    if request.status_code == 200:
        title = re.sub(r"[<>:\"/\\|?*]", "", title) # Removing invalid characters from the video title.

        # Create a new file.
        with open(f"{title}.png", "wb") as file:
            file.write(request.content) # Write the request data into a file.

            # Move the file in the folder selected by the user if specified.
            if not directory_path == download_directory:
                shutil.move(f"./{title}.png", download_directory)

            file.close() # Free the file.
            print(f"\nDownload finished: \"{os.path.join(download_directory, f"{title}")}.png\"")
    else:
        print(f"\nRequest failed with code {request.status_code}.")
