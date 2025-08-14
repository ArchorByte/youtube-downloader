import datetime
import config
import video_download
import audio_download
import subtitles_download
import thumbnail_download

# Get and display the info of a YouTube video.
def video_info_scrapper(youtube_video):
    app_config = config.get_config_data()

    title = youtube_video.title
    id = youtube_video.video_id
    publication = youtube_video.publish_date.strftime("%B %d %Y at %I:%M %p") # Format date.
    thumbnail = youtube_video.thumbnail_url
    author = youtube_video.author
    channel_url = youtube_video.channel_url
    restriction = youtube_video.age_restricted
    views = youtube_video.views
    duration = datetime.timedelta(seconds = youtube_video.length) # Convert the duration from seconds to hours:minutes:seconds.

    if restriction and app_config.get("block_age_restricted_content"):
        print("You can't download this YouTube video because it's age restricted!\nTo disable the age restricted content blockage, update your config.json file!")
        input("Press [Enter] to continue.. ")
        pass

    print("Video info:")
    print(f"- Title: \"{title}\".")
    print(f"- Video ID: {id}.")
    print(f"- Publication: {publication}.")
    print(f"- Thumbnail URL: {thumbnail}.")
    print(f"- Author: {author}.")
    print(f"- Channel URL: {channel_url}.")
    print(f"- Age restricted: {"Yes" if restriction else "No"}.")
    print(f"- Views count: {views} views.")
    print(f"- Duration: {duration}.")


# YouTube video download handler.
def download_video_handler(youtube_video, option, system):
    if option == "1":
        video_download.download_video(youtube_video, system, None, None)
    elif option == "2":
        audio_download.download_audio(youtube_video, None)
    elif option == "3":
        subtitles_download.download_subtitles(youtube_video, None)
    else:
        thumbnail_download.download_thumbnail(youtube_video.thumbnail_url, youtube_video.title, None)
