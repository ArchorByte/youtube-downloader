import helpers
import os
import shutil
import config
import subprocess

# Download the audio of a YouTube video.
# The destination can be set to None to let the normal system running.
# Otherwise, it will fully automate the download process.
def download_audio(youtube_video, destination_path, system):
    app_config = config.get_config_data()
    auto_mp3_conversion = app_config.get("auto_mp3_conversion", True)
    download_directory = ""

    if destination_path == None:
        download_directory = helpers.folder_input()
        print()
    else:
        download_directory = destination_path if os.path.isdir(destination_path) else "./"

    # Select the audio of the video that has the best bitrate.
    audio_stream = youtube_video.streams.filter(only_audio = True).order_by("abr").desc().first()
    print("Preparing your download.. This may take a while.")

    youtube_video.register_on_progress_callback(helpers.download_progress)   # Get the download progress data.
    sanitized_title = helpers.remove_invalid_characters(youtube_video.title)
    file_extension = audio_stream.mime_type.split("/")[-1]                   # Retrieve the extension of the audio file.
    full_path = os.path.join(download_directory, f"{sanitized_title}.{file_extension}")

    helpers.remove_if_exists(full_path)
    helpers.download_stream(audio_stream, f"{sanitized_title}.{file_extension}")

    # If necessary and enabled, we automatically make the conversion to mp3.
    if not file_extension == "mp3" and auto_mp3_conversion:
        print(end = "\n\n") # Text format.

        ffmpeg = helpers.ffmpeg_command_keyword(system)
        helpers.remove_if_exists(f"./{sanitized_title}.mp3")

        subprocess.run([ffmpeg, "-y", "-i", f"{sanitized_title}.{file_extension}", "-ar", "44100", "-ac", "2", "-b:a", "192k",  f"{sanitized_title}.mp3"], check = True)
        helpers.remove_if_exists(f"{sanitized_title}.{file_extension}")

        file_extension = "mp3"
        full_path = os.path.join(download_directory, f"{sanitized_title}.mp3")

    # Move the file in the folder selected by the user if specified.
    if not download_directory == "./":
        shutil.move(f"{sanitized_title}.{file_extension}", download_directory)

    print(f"\nDownload finished: \"{full_path}\"")
