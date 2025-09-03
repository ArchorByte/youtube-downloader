import helpers
import os
import shutil

# Download the audio of a YouTube video.
# The destination can be set to None to let the normal system running.
# Otherwise, it will fully automate the download process.
def download_audio(youtube_video, destination_path):
    download_directory = ""

    if destination_path == None:
        download_directory = helpers.folder_input()
        print()
    else:
        # We default to the current folder if the destination folder provided is not valid.
        download_directory = destination_path if os.path.isdir(destination_path) else "./"

    # Select the audio of the video that has the best bitrate.
    audio_stream = youtube_video.streams.filter(only_audio = True).order_by("abr").desc().first()
    print("Preparing your download.. This may take a while.")

    youtube_video.register_on_progress_callback(helpers.download_progress)   # Get the download progress data.
    sanitized_title = helpers.remove_invalid_characters(youtube_video.title) # Remove invalid characters from the video title.
    full_path = os.path.join(download_directory, f"{sanitized_title}.mp3")

    helpers.remove_if_exists(full_path)
    helpers.download_stream(audio_stream, f"{sanitized_title}.mp3") # Download the audio file.

    # Move the file in the folder selected by the user if specified.
    if not download_directory == "./":
        shutil.move(f"{sanitized_title}.mp3", download_directory)

    print(f"\nDownload finished: \"{full_path}\"")
