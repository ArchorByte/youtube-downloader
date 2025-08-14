import helpers
import requests
import os
import shutil

# Download the thumbnail of a YouTube video.
# The destination can be set to None to let the normal system running.
# Otherwise, it will automate the download process.
def download_thumbnail(thumbnail, title, destination):
    if destination == None:
        download_directory = helpers.folder_input()
        print()
    else:
        download_directory = destination if os.path.isdir(destination) else "./"

    print("Preparing your download.. This may take a while.")
    http_request = requests.get(thumbnail) # Try to retrieve the thumbnail data.

    if http_request.status_code == 200:
        title = helpers.remove_invalid_characters(title) # Removing invalid characters from the video title.
        full_path = os.path.join(download_directory, f"{title}.png")

        helpers.remove_if_exists(f"{title}.png")
        helpers.remove_if_exists(full_path)

        # Create a new file.
        with open(f"{title}.png", "wb") as file:
            file.write(http_request.content) # Write the request data into the file.

            # Move the file in the folder selected by the user if specified.
            if not download_directory == "./":
                shutil.move(f"./{title}.png", download_directory)

            file.close() # Free the file.
            print(f"Download finished: \"{full_path}\"")
    else:
        print(f"\nRequest failed with status code {http_request.status_code}.")
