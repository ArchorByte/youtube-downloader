import json
import os

# Default config file content.
# We use it as a base to avoid to have missing keys in case the config.json file is incomplete or any unexpected keys.
# We use it to check the types in the config.json file as well.
config = {
    "max_download_retries": 10,
    "pytube_range_size_bytes": 1048576, # 1 MB (1024 * 1024).
    "default_download_destination": "./",
    "default_download_resolution": "1080p",
    "default_subtitle_lang": "a.en",    # English (auto generated).
    "block_age_restricted_content": False
}



# Check the type of the input to prevent exploits or invalid type inputs.
def check_input(key, data):
    expected_type = type(config[key])
    return isinstance(data, expected_type) # Return true if the types match.



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

    # We try to load the keys listed in the default config from the config.json file to prevent loading random keys.
    # We check the input type as well to prevent loading random data or exploits.
    for key in config:
        if key in data and check_input(key, data[key]):
            config[key] = data[key]



# Simply return the config data.
def get_config_data():
    return config
