import audio_download
import config
import helpers
import os
import pytubefix
import subtitles_download
import thumbnail_download
import video_download

def playlist_information_scrapper (
    youtube_playlist: pytubefix.Playlist
) -> None:
    """
    Get and display the information of a YouTube playlist.

    Tasks:
        1) Get the relevant information.
        2) Display the information.

    Parameters:
        - youtube_playlist / Playlist / Targeted YouTube playlist.

    Returns:
        No object returned.
    """

    playlist_title = youtube_playlist.title
    playlist_id = youtube_playlist.playlist_id
    last_updated = youtube_playlist.last_updated.strftime("%B %d %Y at %I:%M %p") # Format date.
    playlist_owner = youtube_playlist.owner
    owner_url = youtube_playlist.owner_url
    playlist_videos_count = len(youtube_playlist.video_urls)
    playlist_views = youtube_playlist.views

    print("Playlist info:")
    print(f"- Title: \"{playlist_title}\".")
    print(f"- Playlist ID: {playlist_id}.")
    print(f"- Last update: {last_updated}.")
    print(f"- Owner: {playlist_owner}.")
    print(f"- Owner channel URL: {owner_url}.")
    print(f"- Videos count: {playlist_videos_count} videos.")
    print(f"- Views count: {playlist_views} views.")


def playlist_download_handler (
    youtube_playlist: pytubefix.Playlist,
    option:           str
) -> None:
    """
    Handler of the YouTube playlist downloads.

    Tasks:
        1) Select an action to do depending on the option selected.
        2) Ask preferred values to the user if necessary.

    Parameters:
        - youtube_playlist / Playlist / Targeted YouTube playlist.
        - option           / str      / Targeted action to do.
        - system           / str      / Operating system name we are running on.

    Returns:
        No object returned.
    """

    app_config = config.get_config_data()
    default_lang = app_config.get("default_subtitle_lang", "a.en")
    default_resolution = app_config.get("default_download_resolution", "1080p")
    destination_path = helpers.folder_input()
    destination_path = os.path.abspath(destination_path) # Sanitize the destination path.
    language = ""
    resolution = ""

    if option == "1":
        valid_resolutions = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
        default_resolution = default_resolution if default_resolution in valid_resolutions else valid_resolutions[-1]

        print("\nValid resolutions (might not be available): 144p, 240p, 360p, 480p, 720p, 1080p, 1440p, 2160p.")
        print("Warning: If the resolution selected is not available for a video, the highest one will be selected instead!", end = "\n\n")

        while True:
            resolution = input("Choose a resolution (enter nothing to select " + default_resolution + "): ")
            resolution = resolution if resolution else default_resolution

            if not resolution.endswith("p"):
                resolution += "p" # Add a "p" to the input if it's missing.

            if resolution in valid_resolutions:
                break

            print(f"Invalid resolution! Please, try again.", end = "\n\n")
    elif option == "3":
        language = input(f"\nChoose a subtitle language (enter nothing to select {default_lang}): ")
        language = default_lang if not language else language

    i = 0
    videos_count = len(youtube_playlist.video_urls)

    print("Preparing downloads.. This may take a while.")

    for youtube_video in youtube_playlist.videos:
        i += 1
        print(f"\n[Download {i}/{videos_count} - {youtube_video.title}]")

        if option == "1":
            video_download.download_video(youtube_video, destination_path, resolution)
        elif option == "2":
            audio_download.download_audio(youtube_video, destination_path)
        elif option == "3":
            subtitles_download.download_subtitles(youtube_video, destination_path, language)
        else:
            thumbnail_download.download_thumbnail(youtube_video.thumbnail_url, youtube_video.title, destination_path)
