import helpers
import os
import requests
import typing

def download_thumbnail (
    thumbnail_url:    str,
    video_title:      str,
    destination_path: typing.Optional[str]
) -> None:
    """
    Download the thumbnail of a YouTube video.

    Tasks:
        1) Verify the destination path value.
        2) Make the HTTP request to the thumbnail URL.
        3) If successful, write the response binaries into a new file.
        4) Move the file to the destination folder if necessary.

    Parameters:
        - thumbnail_url    / str        / URL of the thumbnail.
        - video_title      / str        / Title of the YouTube video.
        - destination_path / str | None / Targeted directory for the download. If None, we give an input to the user.

    Returns:
        No object returned.
    """

    app_directory_path = os.getcwd()

    if destination_path == None:
        destination_path = helpers.folder_input()
        print() # UI format.
    elif not os.path.isdir(destination_path):
        destination_path = app_directory_path
        print(f"Warning: Modified destination path to {destination_path} as the provided one wasn't valid!\n")

    destination_path = os.path.abspath(destination_path) # Sanitize the destination path.
    sanitized_title = helpers.remove_invalid_characters(video_title)
    output_path = os.path.join(destination_path, f"{sanitized_title}.png")

    print("Preparing your download.. This may take a while.")
    http_request = requests.get(thumbnail_url)

    if http_request.status_code == 200:
        with open(output_path, "wb") as file:
            file.write(http_request.content)

        print(f"Download finished: \"{destination_path}/{sanitized_title}.png\"")
    else:
        print(f"\nRequest failed with status code {http_request.status_code}.")
