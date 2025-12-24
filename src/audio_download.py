import config
import helpers
import os
import pytubefix
import shutil
import subprocess
import typing

def download_audio (
    youtube_video:    pytubefix.YouTube,
    destination_path: typing.Optional[str]
) -> None:
    """
    Download the audio of a YouTube video.

    Tasks:
        1) Verify the destination path value.
        2) Get the audio stream with the highest bitrate.
        3) Download the stream.
        4) Convert to mp3 if necessary.
        5) Move the file to the destination folder if necessary.

    Parameters:
        - youtube_video    / YouTube    / Targeted YouTube video.
        - destination_path / str | None / Targeted directory for the download. If None, we give an input to the user.

    Returns:
        No object returned.
    """

    app_config = config.get_config_data()
    app_directory_path = os.getcwd()
    auto_mp3_conversion = app_config.get("auto_mp3_conversion", True)
    ffmpeg = helpers.ffmpeg_command_keyword()
    sanitized_title = helpers.remove_invalid_characters(youtube_video.title)

    if destination_path == None:
        destination_path = helpers.folder_input()
        print() # UI format.
    elif not os.path.isdir(destination_path):
        destination_path = app_directory_path
        print(f"Warning: Modified destination path to {destination_path} as the provided one wasn't valid!\n")

    print("Preparing your download.. This may take a while.")
    destination_path = os.path.abspath(destination_path) # Sanitize the destination path.
    audio_stream = youtube_video.streams.filter(only_audio = True).order_by("abr").desc().first() # Select the audio stream that has the best bitrate.

    if audio_stream == None:
        print("Download failed! No audio stream was found for this video!")
        return

    youtube_video.register_on_progress_callback(helpers.download_progress) # Get the download progress data.
    file_extension = audio_stream.mime_type.split("/")[-1]
    helpers.download_stream(audio_stream, f"{sanitized_title}.{file_extension}")

    if file_extension != "mp3" and auto_mp3_conversion:
        print(end = "\n\n") # UI format.
        subprocess.run([ffmpeg, "-y", "-i", f"{sanitized_title}.{file_extension}", "-ar", "44100", "-ac", "2", "-b:a", "192k",  f"{sanitized_title}.mp3"], check = True)
        helpers.remove_if_exists(f"{sanitized_title}.{file_extension}") # Delete the original file.
        file_extension = "mp3"

    if destination_path != app_directory_path:
        shutil.move(f"{sanitized_title}.{file_extension}", destination_path)

    print(f"\nDownload finished: \"{destination_path}/{sanitized_title}.{file_extension}\"")
