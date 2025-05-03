import subprocess
import os
import requests
import re
import shutil

scriptPath = os.path.abspath(__file__) # Detect the path to this script.
directoryPath = os.path.dirname(scriptPath) # Determine the path to the program's folder using the script path.

def folderInput(): # Input to select a folder.
    while True:
        folder = input("File location (enter nothing to select the current folder): ")
        # Take the input if specified or take the program's path if not.
        folder = folder if folder else directoryPath

        if not os.path.isdir(folder): # Invalid path.
            print("This folder doesn't exist! Please, try again!", end = "\n\n")
        else:
            return folder


def displayResolutions(youtubeVideo): # Get and display the resolutions available for a video.
    availableResolutions = []

    for video in youtubeVideo.streams: # Check each resolution available.
        if video.resolution is not None and video.resolution not in availableResolutions:
            # Add the resolution in the list if it's valid and not already in it.
            availableResolutions.append(video.resolution)

    # Sort the resolutions in order (example: 144p, 720p, 1440p).
    availableResolutions = sorted(availableResolutions, key = lambda x: int(x[:-1]))
    showResolutions = ", ".join(availableResolutions) # Format the output into a string list.

    print(f"\nAvailable resolutions: {showResolutions}")
    return availableResolutions


def downloadVideo(youtubeVideo, system): # Download the entire video (video + audio).
    downloadDirectory = folderInput()

    print("Looking for available resolutions for your video..")
    availableResolutions = displayResolutions(youtubeVideo) # List containing every resolutions available for that video.

    while True:
        resolution = input("Choose a resolution: ")

        if resolution not in availableResolutions: # Invalid resolution.
            print(f"Unavailable resolution! Please, try again.", end = "\n\n")
        else:
            print("\nPreparing your download.. Download speed depends on your internet connection.");
            break

    if resolution == "360p": # Resolutions with built-in audio.
        # Select the video with the right resolution.
        video = youtubeVideo.streams.filter(resolution = resolution).first()

        youtubeVideo.register_on_progress_callback(downloadProgress) # Get the download progresss.
        title = re.sub(r"[<>:\"/\\|?*]", "", youtubeVideo.title) # Remove invalid characters from the video title.

        video.download(filename = f"{title}.mp4", output_path = directoryPath) # Download the video.
        print(f"\n\nDownload finished: \"{os.path.join(downloadDirectory, f"{title}")}.mp4\"")
    else: # Resolutions with missing audio (YouTube's shitty limitations).
        # Select the video with the right resolution and the audio with a bitrate of 128 kbps (good quality).
        video = youtubeVideo.streams.filter(resolution = resolution, only_video = True).first()
        audio = youtubeVideo.streams.filter(only_audio = True, abr = "128kbps").first()

        youtubeVideo.register_on_progress_callback(downloadProgress) # Get the download progress.
        video.download(filename = "videoSource.mp4") # Download the video source.
        audio.download(filename = "audioSource.mp3") # Download the audio source.

        print("\nAssembling audio and video..", end = "\n\n")
        ffmpeg = "ffmpeg" # Default command.

        if system == "Windows": # Command for Windows systems.
            ffmpeg = "ffmpeg.exe"
        elif os.path.exists("/system/build.prop"): # Command for Android systems.
            ffmpeg = "./ffmpeg"

        # Use ffmpeg to assemble the video source file and the audio source file.
        subprocess.run(f"{ffmpeg} -i videoSource.mp4 -i audioSource.mp3 -c:v copy -c:a aac output.mp4", shell = True)
        title = re.sub(r"[<>:\"/\\|?*]", "", youtubeVideo.title) # Remove invalid characters from the video title.

        os.rename("output.mp4", f"{title}.mp4") # Rename the "output.mp4" file into the video title.
        # Delete source files because we no longer need them.
        os.remove("videoSource.mp4")
        os.remove("audioSource.mp3")

        if not directoryPath == downloadDirectory:
            shutil.move(f"./{title}.mp4", downloadDirectory) # Move the file in the folder selected by the user.

        print(f"\nDownload finished: \"{os.path.join(downloadDirectory, f"{title}")}.mp4\"")


def downloadAudio(youtubeVideo): # Download the audio.
    downloadDirectory = folderInput()

    # Select the video's audio only with a bitrate of 128 kbps (good quality).
    audio = youtubeVideo.streams.filter(only_audio = True, abr = "128kbps").first()
    print("Preparing your download.. Download speed depends on your internet connection.")

    youtubeVideo.register_on_progress_callback(downloadProgress) # Get the download progress.
    title = re.sub(r"[<>:\"/\\|?*]", "", youtubeVideo.title) # Remove invalid characters from the video title.

    audio.download(filename = f"{title}.mp3", output_path = downloadDirectory) # Download the audio file.
    print(f"\n\nDownload finished: \"{os.path.join(downloadDirectory, f"{title}")}.mp3\"")


def downloadProgress(stream, chunk, sizeRemaining): # Download progress report.
    videoSize = stream.filesize
    downloaded = videoSize - sizeRemaining # Calculate the amount of downloaded bytes.
    percentage = downloaded / videoSize * 100 # Calculate the progress made so far in percentage.

    filled = int(20 * downloaded / videoSize) # Calculate the amount of "filled" characters to display.
    empty = 20 - filled
    bar = "[" + "█" * filled + " " * empty + "]" # Render the bar.

    print(f"\rDownload progress: {percentage:.0f}% {bar} ({downloaded / 1000000:.2f}MB/{videoSize / 1000000:.2f}MB).", end = "", flush = True)


def downloadThumbnail(videoThumbnail, videoTitle): # Download the thumbnail.
    downloadDirectory = folderInput()

    print("Preparing your download.. Download speed depends on your internet connection.")
    request = requests.get(videoThumbnail) # Try to get the thumbnail.

    if request.status_code == 200:
        title = re.sub(r"[<>:\"/\\|?*]", "", videoTitle) # Removing unvalid characters.

        # Create a new file.
        with open(f"{title}.png", "wb") as file:
            file.write(request.content) # Write the image data into a file.

            if not directoryPath == downloadDirectory:
                shutil.move(f"./{videoTitle}.png", downloadDirectory) # Move the file in the folder selected by the user.

            file.close()
            print(f"\nDownload finished: \"{os.path.join(downloadDirectory, f"{videoTitle}")}.png\"")
    else:
        print(f"\nRequest failed with code {request.status_code}.")