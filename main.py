import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "dependencies")) # Load bundled dependencies.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))          # Load src folder.

import config
import ffmpeg
import platform
import playlist_handler
import pytubefix
import video_handler

def main () -> None:
    """
    Program main.

    Tasks:
        1) Load the config.json file.
        2) Verify the configuration values.
        3) Install FFmpeg if necessary.
        4) In loop:
            -> Clean the terminal.
            -> Ask for a YouTube URL if necessary.
            -> Detect whether it's a video or a playlist.
            -> Display all relevant data.
            -> Ask for a download action.
            -> Run the action.
            -> Ask if we keep running and whether we use the same video/playlist or not.

    Parameters:
        No parameters.

    Returns:
        No object returned.
    """

    config.load_config_file()
    app_config = config.get_config_data()
    range_size_bytes = app_config.get("pytube_range_size_bytes", 1024 * 1024)
    default_download_option = app_config.get("default_download_option_number", 1)
    default_download_option = default_download_option if default_download_option > 0 and default_download_option <= 4 else 1

    ffmpeg_installed = ffmpeg.check_installation()
    pytubefix.request.default_range_size = range_size_bytes if range_size_bytes > 0 else 1024 * 1024
    source_type = "video"
    system = platform.system()
    url = None
    youtube_source = None

    if not ffmpeg_installed:
        ffmpeg.install()

    while True:
        os.system("cls" if system == "Windows" else "clear")

        if url == None:
            url = input("YouTube video or playlist link: ")
            print("Retrieving information.. This may take a while.", end = "\n\n")

            try:
                youtube_source = pytubefix.YouTube(url)
                source_type = "video"
            except:
                youtube_source = pytubefix.Playlist(url)
                source_type = "playlist"

        if source_type == "video":
            video_handler.video_information_scrapper(youtube_source)
            print("\nWhat would you like to download?\n1) The full video.\n2) The audio only.\n3) The subtitles.\n4) The thumbnail.")
        else:
            playlist_handler.playlist_information_scrapper(youtube_source)
            print("\nWhat would you like to download?\n1) All videos.\n2) The audio of all videos only.\n3) The subtitles of all videos.\n4) The thumbnail of all videos.")

        while True:
            option = input(f"\nNumber of the option (enter nothing to select {default_download_option}): ")
            option = option if option else str(default_download_option)
            valid_options = { "1", "2", "3", "4" }

            if option in valid_options:
                if source_type == "video":
                    video_handler.download_video_handler(youtube_source, option)
                else:
                    playlist_handler.playlist_download_handler(youtube_source, option)
                break
            else:
                print("Invalid option! Please, try again.")

        restart = input("\nReady for another download? (y/n) ")

        if restart.lower() != "y":
            print("Bye!")
            break

        reset = input(f"Do you want to use this {"video" if source_type == "video" else "playlist"} again? (y/n) ")

        if reset.lower() != "y":
            url = None

try:
    main()
except Exception as error:
    print(f"\nThe program has crashed! Error: {error}")
    input("Press [Enter] to end the program..")
