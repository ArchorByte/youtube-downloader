import config
import helpers
import os
import shutil

# Get and display all available subtitle languages of a YouTube video.
def display_subtitles_list(youtube_video):
    available_subtitles = []
    show_subtitles = ""
    i = 0

    for subtitle in youtube_video.captions:
        show_subtitles = f"{show_subtitles}\n- '{subtitle.code}' for {subtitle.name}."
        available_subtitles.append(subtitle.code)
        i += 1

    if i == 0:
        show_subtitles = "No subtitles available."

    print(f"\nAvailable subtitle languages: {show_subtitles}", end = "\n\n")
    return available_subtitles


# Download the subtitles of a YouTube video.
# The destination can be set to None to let the normal system running.
# Otherwise, it will automate the download process.
def download_subtitles(youtube_video, destination):
    app_config = config.get_config_data()
    default_subtitle_lang = app_config.get("default_subtitle_lang", "a.en")

    if destination == None:
        download_directory = helpers.folder_input()
    else:
        download_directory = destination if os.path.isdir(destination) else "./"

    available_subtitles = display_subtitles_list(youtube_video)                       # List and display all subtitle languages available.
    default_allowed = True if default_subtitle_lang in available_subtitles else False # Determine if the default subtitle language can be used for this video.

    if len(available_subtitles) < 1:
        print("No subtitles available for this video!")
        return

    while True:
        # Propose to use the "enter nothing" option to select the default language only if it's allowed.
        lang = input(f"Choose a subtitle language (enter nothing to select {default_subtitle_lang}): ") if default_allowed else input("Choose a subtitle language: ")
        lang = default_subtitle_lang if default_allowed and not lang else lang

        if lang not in available_subtitles:
            print(f"Unavailable language! Please, try again.", end = "\n\n")
        else:
            print("\nPreparing your download.. Download speed depends on your internet connection.");
            break

    subtitles = youtube_video.captions[lang]         # Retrieve the subtitle using the language code.
    subtitle_srt = subtitles.generate_srt_captions() # Get the subtitles in the SRT format.

    title = helpers.remove_invalid_characters(youtube_video.title)
    full_path = os.path.join(download_directory, f"{title}.srt")

    helpers.remove_if_exists(f"{title}.srt")
    helpers.remove_if_exists(full_path)

    # Create the SRT file that will contain the subtitles.
    with open(f"{title}.srt", "w") as file:
        file.write(subtitle_srt)
        file.close() # Free the file.

    # Move the file in the folder selected by the user if specified.
    if not download_directory == "./":
        shutil.move(f"./{title}.srt", download_directory)

    print(f"Download finished: \"{full_path}\"")
