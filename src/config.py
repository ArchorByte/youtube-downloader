import json
import os

# Default config file content.
# We use it as a base to avoid to have missing keys in case the config.json file is incomplete or contain any unexpected keys.
# We use it to check the types as well for security.
config = {
    "max_download_retries": 10,
    "retry_cooldown": 3,
    "pytube_range_size_bytes": 1048576,  # 1 MB (1024 KB * 1024 KB).
    "download_bars_length": 20,
    "default_download_option_number": 1, # Download full video option.
    "default_download_destination": "./",
    "default_download_resolution": "1080p",
    "default_subtitle_lang": "a.en",     # English (auto generated).
    "block_age_restricted_content": True,
    "auto_mp3_conversion": True
}


# Compare the type of the input with the expected type.
def check_input(key, data):
    expected_type = type(config[key])
    return isinstance(data, expected_type) # Returns true if the types match.


# Load the config file data.
def load_config_file():
    if not os.path.exists("./config.json"):
        return

    config_file_data = None

    # Read the config.json file in read only mode.
    with open("config.json", "r") as file:
        config_file_data = json.load(file) # Read file content as JSON.
        file.close()                       # Free the file.

    # We try to load from the config.json, only the keys that are listed in the default config.
    for key in config:
        if key in config_file_data and check_input(key, config_file_data[key]):
            config[key] = config_file_data[key] # Overwrite the default value configured.


# Simply returns the config data.
def get_config_data():
    return config
