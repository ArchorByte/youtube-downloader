import audio_download
import config
import datetime
import pytubefix
import subtitles_download
import thumbnail_download
import video_download

def video_information_scrapper (
    youtube_video: pytubefix.YouTube
) -> None:
    """
    Get and display the information of a YouTube video.

    Tasks:
        1) Retrieve all relevant information of a YouTube video.
        2) Check the age restriction.
        3) Display the information.

    Parameters:
        - youtube_video / YouTube / Targeted YouTube video.

    Returns:
        No object returned.
    """

    app_config = config.get_config_data()
    age_restriction = app_config.get("block_age_restricted_content", True)

    video_title = youtube_video.title
    video_id = youtube_video.video_id
    publication_date = youtube_video.publish_date.strftime("%B %d %Y at %I:%M %p") # Format date.
    thumbnail_url = youtube_video.thumbnail_url
    video_author = youtube_video.author
    channel_url = youtube_video.channel_url
    age_restricted = youtube_video.age_restricted
    video_views_count = youtube_video.views
    duration = datetime.timedelta(seconds = youtube_video.length) # Convert the duration from seconds to hours:minutes:seconds.

    if age_restricted and age_restriction:
        print("You can't download this YouTube video because it's age restricted!\nTo disable the age restricted content blockage, update the config.json file!")
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


def download_video_handler (
    youtube_video: pytubefix.YouTube,
    option:        int
) -> None:
    """
    Handler of the YouTube video downloads.

    Tasks:
        1) Select an action to do depending on the option selected.

    Parameters:
        - youtube_video / YouTube / Targeted YouTube video.
        - option        / int     / Targeted action to do.

    Returns:
        No object returned.
    """

    if option == "1":
        video_download.download_video(youtube_video, None, None)
    elif option == "2":
        audio_download.download_audio(youtube_video, None)
    elif option == "3":
        subtitles_download.download_subtitles(youtube_video, None, None)
    else:
        thumbnail_download.download_thumbnail(youtube_video.thumbnail_url, youtube_video.title, None)
