import os
import config
import subprocess
import shutil
import helpers

# Get and display all available resolutions of a YouTube video.
def display_resolutions(youtube_video):
    available_resolutions = []

    # Check each resolution available.
    for video in youtube_video.streams:
        if video.resolution is not None and video.resolution not in available_resolutions:
            available_resolutions.append(video.resolution) # Add the resolution in the list if it's valid and not already in it.

    available_resolutions = sorted(available_resolutions, key = lambda x: int(x[:-1])) # Sort the resolutions in order.
    resolutions_list = ", ".join(available_resolutions)                                # Format the output into a string list.

    print(f"\nAvailable resolutions: {resolutions_list}")
    return available_resolutions


# Download an entire YouTube video (video + audio).
# The resolution and destination can be set to None to let the normal system running.
# Otherwise, it will automate the download process.
def download_video(youtube_video, system, resolution, destination_path):
    app_config = config.get_config_data() # Retrieve the configured data.

    if destination_path == None:
        download_directory = helpers.folder_input()
    else:
        # We default to the current folder if the destination folder provided is not valid.
        download_directory = destination_path if os.path.isdir(destination_path) else "./"

    print("Looking for available resolutions for your video..")
    available_resolutions = display_resolutions(youtube_video) # Display available resolutions.

    if resolution == None:
        # We select the default download resolution in the config file if it's available.
        # Otherwise, we select the highest resolution available.
        default_resolution = app_config.get("default_download_resolution", "1080p")
        default_resolution = default_resolution if default_resolution in available_resolutions else available_resolutions[-1]

        while True:
            resolution = input("Choose a resolution (enter nothing to select " + default_resolution + "): ")
            resolution = resolution if resolution else default_resolution

            # Add a "p" at the end of the input if missing to allow, for example, the user to enter "1080" for "1080p".
            if not resolution.endswith("p"):
                resolution += "p"

            if resolution not in available_resolutions:
                print(f"Unavailable resolution! Please, try again.", end = "\n\n")
            else:
                break
    else:
        if resolution not in available_resolutions:
            # We select the highest resolution available if the provided resolution is not available.
            resolution = available_resolutions[-1]

    # To bypass the YouTube limitations, we are going to download the video and its audio separately.
    # We do this even on resolutions with built-in audio to always select the highest audio bitrate available.
    # Once it's done, we assemble the video file and audio file using ffmpeg to finally have the entire video ready.

    video_stream = youtube_video.streams.filter(resolution = resolution, only_video = True).first() # Select the video source with our criteria.
    audio_stream = youtube_video.streams.filter(only_audio = True).order_by("abr").desc().first()   # Select the audio source that has the best bitrate.

    # Get the download progress data.
    youtube_video.register_on_progress_callback(helpers.download_progress)

    # Clean up the folder if necessary.
    helpers.remove_if_exists("video_source.mp4")
    helpers.remove_if_exists("audio_source.mp3")
    helpers.remove_if_exists("output.mp4")

    print("\nDownloading video source:")
    helpers.download_stream(video_stream, "video_source.mp4") # Download the video source.

    print("\n\nDownloading audio source:")
    helpers.download_stream(audio_stream, "audio_source.mp3") # Download the audio source.

    print("\n\nAssembling audio and video..")
    ffmpeg = "ffmpeg" # Default command (Linux and MacOS systems).

    # Change the command depending on the operating system.
    if system == "Windows":
        ffmpeg = "ffmpeg.exe"
    elif os.path.exists("/system/build.prop"): # Android systems.
        ffmpeg = "./ffmpeg"

    # Use ffmpeg to assemble the video source file and the audio source file.
    subprocess.run([ffmpeg, "-y", "-i", "video_source.mp4", "-i", "audio_source.mp3", "-c:v", "copy", "-c:a", "aac", "output.mp4"], check = True)
    sanitized_title = helpers.remove_invalid_characters(youtube_video.title) # Remove invalid characters from the video title.

    # Delete source files as we no longer need them.
    helpers.remove_if_exists("video_source.mp4")
    helpers.remove_if_exists("audio_source.mp3")

    full_path = os.path.join(download_directory, f"{sanitized_title}.mp4")
    helpers.remove_if_exists(full_path)
    os.rename("output.mp4", f"{sanitized_title}.mp4") # Rename the "output.mp4" file with the video title.

    # Move the file in the folder selected by the user if specified.
    if not download_directory == "./":
        shutil.move(f"./{sanitized_title}.mp4", download_directory)

    print(f"\nDownload finished: \"{full_path}\"")
