import config    # config.py
import platform
import ffmpeg    # ffmpeg.py
import pytubefix
import downloads # downloads.py
import os

try:
    config.load_config_file()         # Load the config.json file data.
    app_config = config.get_config_data() # Retrieve the configuration.

    system = platform.system()        # Detect the operating we are running on.
    ffmpeg.check_installation(system) # Check if ffmpeg is installed on this device (required).

    while True:
        url = input("YouTube video link: ")
        youtube_video = pytubefix.YouTube(url) # Fetch the YouTube video with pytubefix.
        print("Fetching the data of the video..")

        # Fetch video information all at once.
        title = youtube_video.title
        thumbnail = youtube_video.thumbnail_url
        author = youtube_video.author
        channel = youtube_video.channel_url
        restriction = youtube_video.age_restricted
        views = youtube_video.views

        if restriction == True and app_config.get("block_age_restricted_content") == True:
            print("You can't download this YouTube video because it's age restricted!\nTo disable the age restricted content blockage, update your config.json file!")
            pass

        print(f"\nVideo info:\n- Title: \"{title}\".\n- Thumbnail URL: {thumbnail}.\n- Author: {author} ({url}).\n- Age restricted: {"Yes" if restriction == True else "No"}.\n- Views count: {views} views.")
        print("\nWhat do you want to download?\n1) The full video.\n2) The audio only.\n3) The thumbnail.")

        while True:
            download = input("\nNumber of the option: ")

            if download == "1":
                downloads.download_video(youtube_video, system); # Download the entire YouTube video option.
                break
            elif download == "2":
                downloads.download_audio(youtube_video);         # Download the YouTube video audio only option.
                break
            elif download == "3":
                downloads.download_thumbnail(thumbnail, title);  # Download the YouTube video thumbnail option.
                break
            else:
                print(f"Please, try again!", end = "\n\n")

        restart = input("Ready for an another download? (y/n) ")

        if not restart.lower() == "y":
            print("Bye!")
            break # End the program.

        # Clear the terminal depending on the operating system we are running on.
        os.system("cls" if system == "Windows" else "clear")
except Exception as err:
    # Crash handler.
    print(f"\nThe program has crashed! Error: {err}", end = "\n\n")
    input("Press [Enter] to close the program..")
