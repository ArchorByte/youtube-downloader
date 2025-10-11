import datetime
import config
import video_download
import audio_download
import subtitles_download
import thumbnail_download

# Get and display the info of a YouTube video.
def video_info_scrapper(youtube_video):
    app_config = config.get_config_data()

    video_title = youtube_video.title
    video_id = youtube_video.video_id
    publication_date = youtube_video.publish_date.strftime("%B %d %Y at %I:%M %p") # Format date.
    thumbnail_url = youtube_video.thumbnail_url
    video_author = youtube_video.author
    channel_url = youtube_video.channel_url
    age_restricted = youtube_video.age_restricted
    video_views_count = youtube_video.views
    duration = datetime.timedelta(seconds = youtube_video.length) # Convert the duration from seconds to hours:minutes:seconds.

    # Block the video download if it's age restricted and disallowed by the config data.
    if age_restricted and app_config.get("block_age_restricted_content"):
        print("You can't download this YouTube video because it's age restricted!\nTo disable the age restricted content blockage, update your config.json file!")
        input("Press [Enter] to continue.. ")
        pass

    print("Video info:")
    print(f"- Title: \"{video_title}\".")
    print(f"- Video ID: {video_id}.")
    print(f"- Publication: {publication_date}.")
    print(f"- Thumbnail URL: {thumbnail_url}.")
    print(f"- Author: {video_author}.")
    print(f"- Channel URL: {channel_url}.")
    print(f"- Age restricted: {"Yes" if age_restricted else "No"}.")
    print(f"- Views count: {video_views_count} views.")
    print(f"- Duration: {duration}.")


# YouTube video download handler.
def download_video_handler(youtube_video, option, system):
    if option == "1":
        video_download.download_video(youtube_video, system, None, None)
    elif option == "2":
        audio_download.download_audio(youtube_video, None, system)
    elif option == "3":
        subtitles_download.download_subtitles(youtube_video, None)
    else:
        thumbnail_download.download_thumbnail(youtube_video.thumbnail_url, youtube_video.title, None)
