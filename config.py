import json
import os

# Default config file content.
config = {
    "max_download_retries": 10,
    "pytube_range_size_bytes": 1048576, # 1 MB.
    "default_download_destination": "./",
    "default_download_resolution": "1080p",
    "block_age_restricted_content": False
}

# Load the config file data.
def load_config_file():

    # If the config file doesn't exist, we will use the default data.
    if not os.path.exists("./config.json"):
        return

    data = None

    # Read the file in read only mode.
    with open("config.json", "r") as file:
        data = json.load(file) # Retrieve the data as json.
        file.close()           # Free the file.

    # If the key is available in both the config defaults and config file, we update the config to take the user config.s
    for key in config:
        if key in data:
            config[key] = data[key]


# Simply return the config data.
def get_config_data():
    return config
