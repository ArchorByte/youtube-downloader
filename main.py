import platform
import ffmpeg # ffmpeg.py
import pytubefix
import downloads # downloads.py
import os

try:
    system = platform.system() # Detect the OS.
    ffmpeg.check_installation(system) # Check if ffmpeg is installed (required).

    while True:
        url = input("YouTube video link: ")
        youtube_video = pytubefix.YouTube(url) # Fetch the video with pytubefix.
        print("Fetching the data of the video..")

        # Fetch informations.
        title = youtube_video.title
        thumbnail = youtube_video.thumbnail_url
        author = youtube_video.author
        channel = youtube_video.channel_url
        restriction = youtube_video.age_restricted
        views = youtube_video.views

        print(f"\nVideo info:\n- Title: \"{title}\"\n- Thumbnail: {thumbnail}\n- Author: {author} ({url})\n- 18+: {"Yes" if restriction == True else "No"}\n- Views count: {views} views")
        print("\nWhat do you want to download?\n1) The full video.\n2) The audio only.\n3) The thumbnail.")

        while True:
            download = input("\nNumber of the option: ")

            if download == "1":
                downloads.download_video(youtube_video, system);
                break # We leave the loop once it's done.
            elif download == "2":
                downloads.download_audio(youtube_video);
                break
            elif download == "3":
                downloads.download_thumbnail(thumbnail, title);
                break
            else:
                print(f"Please, try again!", end = "\n\n") # Bad option.

        restart = input("Ready for an another download? (y/n) ")

        if not restart.lower() == "y":
            print("Bye!")
            break # End the program

        os.system("cls" if system == "Windows" else "clear") # Clear the terminal.
except Exception as err:
    print(f"\nThe program crashed!\nError: {err}", end = "\n\n")
    input("Press [Enter] to close the program..")