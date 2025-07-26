import config # config.py
import subprocess
import os
import requests
import re
import shutil
from pytubefix import request
import time

app_config = config.get_config_data()                                      # Retrieve config data.
default_config_path = app_config.get("default_download_destination", "./") # Default configured download path.
range_size_bytes = app_config.get("pytube_range_size_bytes", 1024 * 1024)  # Default configured range size in bytes for the callback trigger.
max_retries = app_config.get("max_download_retries", 10)                   # Default configured amount of retries before aborting.
default_subtitle_lang = app_config.get("default_subtitle_lang", "a.en")    # Default configured language for the subtitle downloads.

script_path = os.path.abspath(__file__)       # Detect the path to this script.
directory_path = os.path.dirname(script_path) # Determine the path to the program's folder using the script path.

# Select "./" if the default configured path is not valid.
default_download_path = default_config_path if os.path.exists(default_config_path) else directory_path

# Set up the range size. We set it to 1 MB if the configured range is not valid.
request.default_range_size = range_size_bytes if range_size_bytes >= 1 else 1024 * 1024

# Set up the max amount of retries. We set it to 10 if the configured amount is not valid.
max_retries = max_retries if max_retries >= 1 and max_retries <= 100 else 10



# Input to select a folder.
def folder_input():
    while True:
        folder = input("File location (enter nothing to select the default path): ")
        folder = folder if folder else default_download_path # Take the input (if specified) or select the default path.

        if not os.path.isdir(folder):
            print("This folder doesn't exist! Please, try again!", end = "\n\n")
        else:
            return folder



# Remove a file if it's already existing.
def remove_if_exists(path):
    if os.path.exists(path) and os.path.isfile(path):
        os.remove(path)



# Remove invalid characters for a file name from an input.
def remove_invalid_characters(input):
    output = re.sub(r"[<>:\"/\\|?*]", "", input)
    output = output if output else "A very cool video" # Check that there the output is not empty.

    return output



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



# Get and display all available subtitle languages of a YouTube video.
def display_subtitles_list(youtube_video):
    available_subtitles = []
    show_subtitles = ""

    # Register each subtitle available.
    for subtitle in youtube_video.captions:
        show_subtitles = f"{show_subtitles}\n- '{subtitle.code}' for {subtitle.name}" # We update our output message to add thee language in it.
        available_subtitles.append(subtitle.code)                                     # We only take the language code in the list.

    print(f"\nAvailable subtitle languages: {show_subtitles}", end = "\n\n")
    return available_subtitles



# Download streams with an attempts system.
def download_stream(stream, filename):
    i = 0

    while (i < max_retries):
        try:
            stream.download(filename = filename, max_retries = max_retries)
            return True
        except Exception as error:
            print(f"\nDownload attempt {i + 1}/{max_retries} failed with error {error}!")
            remove_if_exists(filename) # Remove the created file before resuming.
            time.sleep(3)              # Wait 3 seconds before trying again.

        i += 1

    return False



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

        if resolution not in available_resolutions:
            print(f"Unavailable resolution! Please, try again.", end = "\n\n")
        else:
            print("\nPreparing your download.. Download speed depends on your internet connection.")
            break

    # To bypass the limitation, we are going to download the video and its audio separately.
    # We do this even on resolutions with built-in audio to always select the highest audio bitrate available.
    # Once it's done, we assemble the video file and audio file using ffmpeg to finally have the entire video ready.

    video = youtube_video.streams.filter(resolution = resolution, only_video = True).first() # Select the video source.
    audio = youtube_video.streams.filter(only_audio = True).order_by("abr").desc().first()   # Select the audio source that has the best bitrate.

    # Get the download progress data.
    youtube_video.register_on_progress_callback(download_progress)

    remove_if_exists("video_source.mp4")
    remove_if_exists("audio_source.mp3")
    remove_if_exists("output.mp4")

    download_stream(video, "video_source.mp4") # Download the video source.
    print()                                    # Separate the two progression bars.
    download_stream(audio, "audio_source.mp3") # Download the audio source.

    print("\n\nAssembling audio and video..")
    ffmpeg = "ffmpeg" # Default command (Linux + MacOS systems).

    # Change the command depending on the operating system.
    if system == "Windows":
        ffmpeg = "ffmpeg.exe"
    elif os.path.exists("/system/build.prop"): # Android systems.
        ffmpeg = "./ffmpeg"

    # Use ffmpeg to assemble the video source file and the audio source file.
    subprocess.run([ffmpeg, "-y", "-i", "video_source.mp4", "-i", "audio_source.mp3", "-c:v", "copy", "-c:a", "aac", "output.mp4"], check = True)
    title = remove_invalid_characters(youtube_video.title)

    # Delete source files because we no longer need them.
    remove_if_exists("video_source.mp4")
    remove_if_exists("audio_source.mp3")

    full_path = os.path.join(download_directory, f"{title}.mp4")
    remove_if_exists(full_path)
    os.rename("output.mp4", f"{title}.mp4") # Rename the "output.mp4" file with the video title.

    # Move the file in the folder selected by the user if specified.
    if not download_directory == "./":
        shutil.move(f"./{title}.mp4", download_directory)

    print(f"\nDownload finished: \"{full_path}\"")



# Download the audio of a YouTube video.
def download_audio(youtube_video):
    download_directory = folder_input()

    audio = youtube_video.streams.filter(only_audio = True).order_by("abr").desc().first() # Select the audio of the video that has the best bitrate.
    print("\nPreparing your download.. Download speed depends on your internet connection.")

    youtube_video.register_on_progress_callback(download_progress) # Get the download progress data.
    title = remove_invalid_characters(youtube_video.title)         # Remove invalid characters from the video title.
    full_path = os.path.join(download_directory, f"{title}.mp3")

    remove_if_exists(full_path)
    download_stream(audio, f"{title}.mp3") # Download the audio file.

    # Move the file in the folder selected by the user if specified.
    if not download_directory == "./":
        shutil.move(f"{title}.mp3", download_directory)

    print(f"\nDownload finished: \"{full_path}\"")



# Download progress callback.
def download_progress(stream, chunk, remaining):
    file_size = stream.filesize
    downloaded_bytes = file_size - remaining
    percentage = downloaded_bytes / file_size * 100

    filled = int(20 * downloaded_bytes / file_size) # Calculate the amount of "filled characters" to display in the bar.
    empty = 20 - filled                             # The rest of the bar is set as whitespaces. The bar is 20 characters whatsoever.
    bar = "[" + "█" * filled + " " * empty + "]"    # Render the bar.

    print(f"\rDownload progress: {percentage:.0f}% {bar} ({downloaded_bytes / 1000000:.2f}MB/{file_size / 1000000:.2f}MB).", end = "", flush = True)



# Download the subtitles of a YouTube video.
def download_subtitles(youtube_video):
    download_directory = folder_input()
    available_subtitles = display_subtitles_list(youtube_video)                       # List and display all subtitle languages available.
    default_allowed = True if default_subtitle_lang in available_subtitles else False # Determine if the default subtitle language can be used for this video.

    # If there is no subtitle available for this video, we abort.
    if len(available_subtitles) < 1:
        print("No subtitles available for this video!")
        return

    while True:
        # Propose to use the "enter nothing" option to select the default language only if it's allowed.
        lang = input(f"Choose a subtitle language (enter nothing to select {default_subtitle_lang}): ") if default_allowed else input("Choose a subtitle language: ")
        lang = default_subtitle_lang if default_allowed and not lang else lang

        if lang not in available_subtitles:
            print(f"Unavailable language! Please, try again.", end = "\n\n")
        else:
            print("\nPreparing your download.. Download speed depends on your internet connection.");
            break

    subtitle = youtube_video.captions[lang]         # Retrieve the subtitle using the language code.
    subtitle_srt = subtitle.generate_srt_captions() # Get the subtitles in SRT format.

    title = remove_invalid_characters(youtube_video.title) # Removing invalid characters from the video title.
    full_path = os.path.join(download_directory, f"{title}.srt")

    remove_if_exists(f"{title}.srt")
    remove_if_exists(full_path)

    # Create the SRT file that will contain the subtitles.
    with open(f"{title}.srt", "w") as file:
        file.write(subtitle_srt)
        file.close() # Free the file.

    # Move the file in the folder selected by the user if specified.
    if not download_directory == "./":
        shutil.move(f"./{title}.srt", download_directory)

    print(f"Download finished: \"{full_path}\"")



# Download the thumbnail of a YouTube video.
def download_thumbnail(thumbnail, title):
    download_directory = folder_input()

    print("\nPreparing your download.. Download speed depends on your internet connection.")
    http_request = requests.get(thumbnail) # Try to retrieve the thumbnail data.

    if http_request.status_code == 200:
        title = remove_invalid_characters(title) # Removing invalid characters from the video title.
        full_path = os.path.join(download_directory, f"{title}.png")

        remove_if_exists(f"{title}.png")
        remove_if_exists(full_path)

        # Create a new file.
        with open(f"{title}.png", "wb") as file:
            file.write(http_request.content) # Write the request data into the file.

            # Move the file in the folder selected by the user if specified.
            if not download_directory == "./":
                shutil.move(f"./{title}.png", download_directory)

            file.close() # Free the file.
            print(f"Download finished: \"{full_path}\"")
    else:
        print(f"\nRequest failed with status code {http_request.status_code}.")
