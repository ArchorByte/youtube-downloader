import os
import sys
import config
import platform
import ffmpeg
import pytubefix
import video_handler
import playlist_handler

# Load the dependencies folder to retrieve the bundled libraries.
# Bundling those dependencies make it "plug-and-play".
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "dependencies"))

# Load the src folder to retrieve the other scripts.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    config.load_config_file()             # Load the config.json file data.
    app_config = config.get_config_data() # Retrieve the configuration.

    # Set up the range size in bytes for the pytube download callback trigger.
    range_size_bytes = app_config.get("pytube_range_size_bytes", 1024 * 1024)
    pytubefix.request.default_range_size = range_size_bytes if range_size_bytes >= 1 else 1024 * 1024

    # Default download option.
    # We select 1 (full video download option) if the data registered is not valid.
    default_download_option_number = app_config.get("default_download_option_number", 1)
    default_download_option_number = default_download_option_number if default_download_option_number >= 1 and default_download_option_number <= 4 else 1

    system = platform.system()        # Detect the operating system we are running on.
    ffmpeg.check_installation(system) # Check if ffmpeg is installed on this device (required).

    url = None            # When this variable is set to "None", we give to the user a URL input.
    youtube_source = None # This variable saves the latest video data fetched in case the user wants to use this video again.
    source_type = "v"     # This variable has normally two states: "v" for video and "p" for playlist.

    while True:
        if url == None:
            url = input("YouTube video or playlist link: ")
            print("Retrieving information.. This may take a while.", end = "\n\n")

            try:
                youtube_source = pytubefix.YouTube(url)  # Make a query for a YouTube video with the URL.
                source_type = "v"
            except:
                youtube_source = pytubefix.Playlist(url) # If the query failed, we try to make a query for a playlist instead.
                source_type = "p"

        if source_type == "v":
            video_handler.video_info_scrapper(youtube_source)
            print("\nWhat would you like to download?\n1) The full video.\n2) The audio only.\n3) The subtitles.\n4) The thumbnail.")
        else:
            playlist_handler.playlist_info_scrapper(youtube_source)
            print("\nWhat would you like to download?\nThe selected option will be applied to all videos in the playlist.\n\n1) The full videos.\n2) The audios only.\n3) The subtitles.\n4) The thumbnails.")

        while True:
            download = input(f"\nNumber of the option (enter nothing to select {default_download_option_number}): ")
            download = download if download else str(default_download_option_number) # Select the default option if none was specified.
            available_options = { "1", "2", "3", "4" }

            if download in available_options:
                if source_type == "v":
                    video_handler.download_video_handler(youtube_source, download, system)
                else:
                    playlist_handler.playlist_download_handler(youtube_source, download, system)
                break
            else:
                print("Invalid option! Please, try again.")

        restart = input("\nReady for another download? (y/n) ")

        if not restart.lower() == "y":
            print("Bye!")
            break # End the program.

        reset = input("Do you want to use this video/playlist again? (y/n) ")

        # Clear the previous video data.
        if not reset.lower() == "y":
            url = None
            youtube_video = None

        os.system("cls" if system == "Windows" else "clear")

except Exception as err:
    print(f"\nThe program has crashed! Error: {err}", end = "\n\n")
    input("Press [Enter] to end the program..")
