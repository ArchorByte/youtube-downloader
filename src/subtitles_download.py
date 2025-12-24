import config
import helpers
import os
import pytubefix
import shutil
import typing

def display_subtitles_list (
    youtube_video: pytubefix.YouTube
) -> list:
    """
    Get and display all available subtitle languages of a YouTube video.

    Tasks:
        1) Verify the amount of captions available.
        2) Display and save all available subtitles.

    Parameters:
        - youtube_video / YouTube / Targeted YouTube video.

    Returns:
        A list containing all available subtitle languages.
    """

    available_subtitles = []

    if len(youtube_video.captions) < 1:
        return available_subtitles
    else:
        print("\nAvailable subtitle languages:")

    for subtitle in youtube_video.captions:
        available_subtitles.append(subtitle.code)
        print(f"- '{subtitle.code}' for {subtitle.name}.")

    return available_subtitles


def download_subtitles (
    youtube_video:    pytubefix.YouTube,
    destination_path: typing.Optional[str],
    language:         typing.Optional[str]
) -> None:
    """
    Download the subtitles of a YouTube video.

    Tasks:
        1) Verify the destination path value.
        2) Display available subtitles.
        3) Verify the language value.
        4) Write the subtitles into a .srt file.
        5) Move the file to the destination folder if necessary.

    Parameters:
        - youtube_video    / YouTube    / Targeted YouTube video.
        - destination_path / str | None / Targeted directory for the download. If None, we give an input to the user.
        - language         / str | None / Targeted language for the subtitles. If None, we give an input to the user.

    Returns:
        No object returned.
    """

    app_config = config.get_config_data()
    app_directory_path = os.getcwd()
    default_lang = app_config.get("default_subtitle_lang", "a.en")
    sanitized_title = helpers.remove_invalid_characters(youtube_video.title)

    if destination_path == None:
        destination_path = helpers.folder_input()
    elif not os.path.isdir(destination_path):
        destination_path = app_directory_path
        print(f"Warning: Modified destination path to {destination_path} as the provided one wasn't valid!\n")

    available_subtitles = display_subtitles_list(youtube_video)
    destination_path = os.path.abspath(destination_path) # Sanitize the destination path.
    default_available = True if default_lang in available_subtitles else False

    if len(available_subtitles) < 1:
        print("Download failed! No subtitles available for this video!")
        return
    else:
        print() # UI format.

    if language == None:
        while True:
            language = input(f"Choose a subtitle language (enter nothing to select {default_lang}): ") if default_available else input("Choose a subtitle language: ")
            language = default_lang if default_available and not language else language

            if language in available_subtitles:
                break

            print(f"Unavailable language! Please, try again.", end = "\n\n")
    elif language not in available_subtitles:
        if default_available:
            language = default_lang
        elif "en" in available_subtitles:
            language = "en"
        elif "a.en" in available_subtitles:
            language = "a.en"
        else:
            language = available_subtitles[0]

        print(f"Warning: Modified subtitles language to {language} as the provided one wasn't available!")

    print("\nPreparing your download.. Download speed depends on your internet connection.");
    subtitles = youtube_video.captions[language].generate_srt_captions()

    with open(f"{sanitized_title}.srt", "w") as file:
        file.write(subtitles)

    if destination_path != app_directory_path:
        shutil.move(f"{sanitized_title}.srt", destination_path)

    print(f"Download finished: \"{destination_path}/{sanitized_title}.srt\"")
