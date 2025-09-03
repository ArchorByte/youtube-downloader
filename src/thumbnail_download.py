import helpers
import requests
import os
import shutil

# Download the thumbnail of a YouTube video.
# The destination can be set to None to let the normal system running.
# Otherwise, it will automate the download process.
def download_thumbnail(thumbnail_url, video_title, destination_path):
    if destination_path == None:
        download_directory = helpers.folder_input()
        print()
    else:
        # We default to the current folder if the destination folder provided is not valid.
        download_directory = destination_path if os.path.isdir(destination_path) else "./"

    print("Preparing your download.. This may take a while.")
    http_request = requests.get(thumbnail_url) # Try to retrieve the thumbnail data.

    if http_request.status_code == 200:
        sanitized_title = helpers.remove_invalid_characters(video_title) # Removing invalid characters from the video title.
        full_path = os.path.join(download_directory, f"{sanitized_title}.png")

        helpers.remove_if_exists(f"{sanitized_title}.png")
        helpers.remove_if_exists(full_path)

        # Create a new file and open it in binary mode.
        with open(f"{sanitized_title}.png", "wb") as file:
            file.write(http_request.content) # Write the received data into the file.

            # Move the file in the folder selected by the user if specified.
            if not download_directory == "./":
                shutil.move(f"./{sanitized_title}.png", download_directory)

            file.close() # Free the file.
            print(f"Download finished: \"{full_path}\"")
    else:
        print(f"\nRequest failed with status code {http_request.status_code}.")
