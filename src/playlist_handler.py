import video_download
import audio_download
import subtitles_download
import thumbnail_download
import helpers
import config

# Get and display the info of a YouTube playlist.
def playlist_info_scrapper(youtube_playlist):
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


# YouTube playlist download handler.
def playlist_download_handler(youtube_playlist, option, system):
    app_config = config.get_config_data()
    valid_resolutions = { "144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p" }
    resolution = ""

    if option == "1":
        print("Valid resolutions (might not be available): 144p, 240p, 360p, 480p, 720p, 1080p, 1440p, 2160p.", end = "\n\n")

        # We select the default download resolution in the config file if it's available.
        # Otherwise, we select the highest resolution available.
        default_resolution = app_config.get("default_download_resolution", "1080p")
        default_resolution = default_resolution if default_resolution in valid_resolutions else valid_resolutions[-1]

        while True:
            print("If the resolution selected is not available, the highest one will be selected instead!")

            resolution = input("Choose a resolution (enter nothing to select " + default_resolution + "): ")
            resolution = resolution if resolution else default_resolution

            # Add a "p" at the end of the input if missing to allow the user to enter "1080" for "1080p" for example.
            if not resolution.endswith("p"):
                resolution += "p"

            if resolution not in valid_resolutions:
                print(f"Invalid resolution! Please, try again.", end = "\n\n")
            else:
                break

    destination_path = helpers.folder_input()
    i = 0
    print("Preparing downloads.. This may take a while.")

    for youtube_video in youtube_playlist.videos:
        i += 1
        print(f"\n[Download {i}/{len(youtube_playlist.video_urls)} - {youtube_video.title}]")

        if option == "1":
            video_download.download_video(youtube_video, system, resolution, destination_path)
        elif option == "2":
            audio_download.download_audio(youtube_video, destination_path, system)
        elif option == "3":
            subtitles_download.download_subtitles(youtube_video, destination_path)
        else:
            thumbnail_download.download_thumbnail(youtube_video.thumbnail_url, youtube_video.title, destination_path)
