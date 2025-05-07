import subprocess
import os
import requests
import re
import shutil

script_path = os.path.abspath(__file__) # Detect the path to this script.
directory_path = os.path.dirname(script_path) # Determine the path to the program's folder using the script path.

def folder_input(): # Input to select a folder.
    while True:
        folder = input("File location (enter nothing to select the current folder): ")
        # Take the input if specified or take the program's path if not.
        folder = folder if folder else directory_path

        if not os.path.isdir(folder): # Invalid path.
            print("This folder doesn't exist! Please, try again!", end = "\n\n")
        else:
            return folder


def display_resolutions(youtube_video): # Get and display the resolutions available for a video.
    available_resolutions = []

    for video in youtube_video.streams: # Check each resolution available.
        if video.resolution is not None and video.resolution not in available_resolutions:
            # Add the resolution in the list if it's valid and not already in it.
            available_resolutions.append(video.resolution)

    # Sort the resolutions in order (example: 144p, 720p, 1440p).
    available_resolutions = sorted(available_resolutions, key = lambda x: int(x[:-1]))
    show_resolutions = ", ".join(available_resolutions) # Format the output into a string list.

    print(f"\nAvailable resolutions: {show_resolutions}")
    return available_resolutions


def download_video(youtube_video, system): # Download the entire video (video + audio).
    download_directory = folder_input()

    print("Looking for available resolutions for your video..")
    available_resolutions = display_resolutions(youtube_video) # List containing every resolutions available for that video.

    while True:
        resolution = input("Choose a resolution: ")

        if resolution not in available_resolutions: # Invalid resolution.
            print(f"Unavailable resolution! Please, try again.", end = "\n\n")
        else:
            print("\nPreparing your download.. Download speed depends on your internet connection.");
            break

    if resolution == "360p": # Resolutions with built-in audio.
        # Select the video with the right resolution.
        video = youtube_video.streams.filter(resolution = resolution).first()

        youtube_video.register_on_progress_callback(download_progress) # Get the download progresss.
        title = re.sub(r"[<>:\"/\\|?*]", "", youtube_video.title) # Remove invalid characters from the video title.

        video.download(filename = f"{title}.mp4", output_path = directory_path) # Download the video.
        print(f"\n\nDownload finished: \"{os.path.join(download_directory, f"{title}")}.mp4\"")
    else: # Resolutions with missing audio (YouTube's shitty limitations).
        # Select the video with the right resolution and the audio with a bitrate of 128 kbps (good quality).
        video = youtube_video.streams.filter(resolution = resolution, only_video = True).first()
        audio = youtube_video.streams.filter(only_audio = True, abr = "128kbps").first()

        youtube_video.register_on_progress_callback(download_progress) # Get the download progress.
        video.download(filename = "video_source.mp4") # Download the video source.
        audio.download(filename = "audio_source.mp3") # Download the audio source.

        print("\nAssembling audio and video..", end = "\n\n")
        ffmpeg = "ffmpeg" # Default command.

        if system == "Windows": # Command for Windows systems.
            ffmpeg = "ffmpeg.exe"
        elif os.path.exists("/system/build.prop"): # Command for Android systems.
            ffmpeg = "./ffmpeg"

        # Use ffmpeg to assemble the video source file and the audio source file.
        subprocess.run(f"{ffmpeg} -i video_source.mp4 -i audio_source.mp3 -c:v copy -c:a aac output.mp4", shell = True)
        title = re.sub(r"[<>:\"/\\|?*]", "", youtube_video.title) # Remove invalid characters from the video title.

        os.rename("output.mp4", f"{title}.mp4") # Rename the "output.mp4" file into the video title.
        # Delete source files because we no longer need them.
        os.remove("video_source.mp4")
        os.remove("audio_source.mp3")

        if not directory_path == download_directory:
            shutil.move(f"./{title}.mp4", download_directory) # Move the file in the folder selected by the user.

        print(f"\nDownload finished: \"{os.path.join(download_directory, f"{title}")}.mp4\"")


def download_audio(youtube_video): # Download the audio.
    download_directory = folder_input()

    # Select the video's audio only with a bitrate of 128 kbps (good quality).
    audio = youtube_video.streams.filter(only_audio = True, abr = "128kbps").first()
    print("Preparing your download.. Download speed depends on your internet connection.")

    youtube_video.register_on_progress_callback(download_progress) # Get the download progress.
    title = re.sub(r"[<>:\"/\\|?*]", "", youtube_video.title) # Remove invalid characters from the video title.

    audio.download(filename = f"{title}.mp3", output_path = download_directory) # Download the audio file.
    print(f"\n\nDownload finished: \"{os.path.join(download_directory, f"{title}")}.mp3\"")


def download_progress(stream, chunk, remaining): # Download progress report.
    size = stream.filesize
    downloaded = size - remaining # Calculate the amount of downloaded bytes.
    percentage = downloaded / size * 100 # Calculate the progress made so far in percentage.

    filled = int(20 * downloaded / size) # Calculate the amount of "filled" characters to display.
    empty = 20 - filled
    bar = "[" + "█" * filled + " " * empty + "]" # Render the bar.

    print(f"\rDownload progress: {percentage:.0f}% {bar} ({downloaded / 1000000:.2f}MB/{size / 1000000:.2f}MB).", end = "", flush = True)


def download_thumbnail(thumbnail, title): # Download the thumbnail.
    download_directory = folder_input()

    print("Preparing your download.. Download speed depends on your internet connection.")
    request = requests.get(thumbnail) # Try to get the thumbnail.

    if request.status_code == 200:
        title = re.sub(r"[<>:\"/\\|?*]", "", title) # Removing unvalid characters.

        # Create a new file.
        with open(f"{title}.png", "wb") as file:
            file.write(request.content) # Write the image data into a file.

            if not directory_path == download_directory:
                shutil.move(f"./{title}.png", download_directory) # Move the file in the folder selected by the user.

            file.close()
            print(f"\nDownload finished: \"{os.path.join(download_directory, f"{title}")}.png\"")
    else:
        print(f"\nRequest failed with code {request.status_code}.")