import config
import helpers
import os
import pytubefix
import subprocess
import shutil
import typing

def display_resolutions (
    youtube_video: pytubefix.YouTube
) -> list:
    """
    Get and display all resolutions available for a YouTube video.

    Tasks:
        1) List all existing streams.
        2) Append the list if it's a valid resolution.
        3) Sort the list.
        4) Make a string list to display.

    Parameters:
        - youtube_video / YouTube / Targeted YouTube video.

    Returns:
        A list containing all available resolutions.
    """

    available_resolutions = []

    for stream in youtube_video.streams:
        resolution = stream.resolution

        if resolution != None and resolution not in available_resolutions:
            available_resolutions.append(resolution)

    available_resolutions = sorted(available_resolutions, key = lambda x: int(x[:-1]))
    resolutions_list = ", ".join(available_resolutions)

    print(f"\nAvailable resolutions: {resolutions_list}")
    return available_resolutions


def download_video (
    youtube_video:    pytubefix.YouTube,
    destination_path: typing.Optional[str],
    resolution:       str
) -> None:
    """
    Download an entire YouTube video (audio + video).

    Tasks:
        1) Verify the destination path value.
        2) Display available resolutions.
        3) Verify the resolution value.
        4) Download the audio and video streams.
        5) Assemble both streams to make a single output file.
        6) Move the file to the destination folder if necessary.

    Parameters:
        - youtube_video    / YouTube    / Targeted YouTube video.
        - destination_path / str | None / Targeted directory for the download. If None, we give an input to the user.
        - resolution       / str        / Targeted resolution for the video stream. If None, we give an input to the user.

    Returns:
        No object returned.
    """

    app_config = config.get_config_data()
    app_directory_path = os.getcwd()
    default_resolution = app_config.get("default_download_resolution", "1080p")
    ffmpeg = helpers.ffmpeg_command_keyword()
    sanitized_title = helpers.remove_invalid_characters(youtube_video.title)

    if destination_path == None:
        destination_path = helpers.folder_input()
    elif not os.path.isdir(destination_path):
        destination_path = app_directory_path
        print(f"Warning: Modified destination path to {destination_path} as the provided one wasn't valid!\n")

    print("Looking for available resolutions for your video..")
    destination_path = os.path.abspath(destination_path) # Sanitize the destination path.
    available_resolutions = display_resolutions(youtube_video)

    if resolution == None:
        if default_resolution not in available_resolutions:
            default_resolution = available_resolutions[-1] # Select the highest resolution if the default one is not available.

        while True:
            resolution = input("Choose a resolution (enter nothing to select " + default_resolution + "): ")
            resolution = resolution if resolution else default_resolution

            if not resolution.endswith("p"):
                resolution += "p" # Add a "p" to the input if it's missing.

            if resolution in available_resolutions:
                break

            print(f"Unavailable resolution! Please, try again.", end = "\n\n")
    elif resolution not in available_resolutions:
        highest = available_resolutions[-1]
        print(f"Warning: Targeted resolution ({resolution}) is not available! Defaulted to highest resolution available ({highest})!")
        resolution = highest

    video_stream = youtube_video.streams.filter(resolution = resolution, only_video = True).first()
    audio_stream = youtube_video.streams.filter(only_audio = True).order_by("abr").desc().first() # Select the audio source with the highest bitrate.

    if not video_stream:
        print("Download failed! No video stream was found for this video!")
        return

    if not audio_stream:
        print("Download failed! No audio stream was found for this video!")
        return

    # Get the download progress data.
    youtube_video.register_on_progress_callback(helpers.download_progress)

    print("\nDownloading video source:")
    helpers.download_stream(video_stream, "video_source.mp4")

    print("\n\nDownloading audio source:")
    helpers.download_stream(audio_stream, "audio_source.mp3")

    print("\n\nAssembling audio and video..")
    helpers.remove_if_exists("output.mp4")
    subprocess.run([ffmpeg, "-y", "-i", "video_source.mp4", "-i", "audio_source.mp3", "-c:v", "copy", "-c:a", "aac", f"{sanitized_title}.mp4"], check = True)

    helpers.remove_if_exists("video_source.mp4")
    helpers.remove_if_exists("audio_source.mp3")

    if destination_path != app_directory_path:
        shutil.move(f"{sanitized_title}.mp4", destination_path)

    print(f"\nDownload finished: \"{destination_path}/{sanitized_title}.mp4\"")
