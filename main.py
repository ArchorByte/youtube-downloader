import config    # config.py
import platform
import ffmpeg    # ffmpeg.py
import pytubefix
import downloads # downloads.py
import os
import datetime

try:

    config.load_config_file()             # Load the config.json file data.
    app_config = config.get_config_data() # Retrieve the configuration.

    system = platform.system()        # Detect the operating we are running on.
    ffmpeg.check_installation(system) # Check if ffmpeg is installed on this device (required).

    url = None           # When this variable is set to "None", we give to the user a URL input.
    youtube_video = None # This variable saves the latest video data fetched in case the user wants to use this video again.

    while True:
        if url == None:
            url = input("YouTube video link: ")
            print("Fetching the data of the video..", end = "\n\n")
            youtube_video = pytubefix.YouTube(url) # Fetch the YouTube video with pytubefix.

        # Fetch video information all at once.
        title = youtube_video.title
        id = youtube_video.video_id
        publication = youtube_video.publish_date.strftime("%B %d %Y at %I:%M %p")
        thumbnail = youtube_video.thumbnail_url
        author = youtube_video.author
        channel_url = youtube_video.channel_url
        restriction = youtube_video.age_restricted
        views = youtube_video.views
        duration = datetime.timedelta(seconds = youtube_video.length)

        if restriction and app_config.get("block_age_restricted_content") == True:
            print("You can't download this YouTube video because it's age restricted!\nTo disable the age restricted content blockage, update your config.json file!")
            input("Press [Enter] to continue.. ")
            pass

        print(f"Video info:\n- Title: \"{title}\".\n- Video ID: {id}.\n- Publication: {publication}.\n- Thumbnail URL: {thumbnail}.\n- Author: {author}.\n- Channel URL: {channel_url}.\n- Age restricted: {"Yes" if restriction == True else "No"}.\n- Views count: {views} views.\n- Duration: {duration}.")
        print("\nWhat do you want to download?\n1) The full video.\n2) The audio only.\n3) The subtitles.\n4) The thumbnail.")

        while True:
            download = input("\nNumber of the option: ")

            if download == "1":
                downloads.download_video(youtube_video, system); # Download the entire YouTube video option.
                break
            elif download == "2":
                downloads.download_audio(youtube_video);         # Download the YouTube video audio only option.
                break
            elif download == "3":
                downloads.download_subtitles(youtube_video)      # Download the YouTube video subtitles option.
                break
            elif download == "4":
                downloads.download_thumbnail(thumbnail, title);  # Download the YouTube video thumbnail option.
                break
            else:
                print("Invalid option! Please, try again.")

        restart = input("\nReady for an another download? (y/n) ")

        if not restart.lower() == "y":
            print("Bye!")
            break # End the program.

        reset = input("Do you want to use this video again? (y/n) ")

        # Clear the previous video data.
        if not reset.lower() == "y":
            url = None
            youtube_video = None

        # Clear the terminal depending on the operating system we are running on.
        os.system("cls" if system == "Windows" else "clear")

except Exception as err:
    # Crash handler.
    print(f"\nThe program has crashed! Error: {err}", end = "\n\n")
    input("Press [Enter] to close the program..")
