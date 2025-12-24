import json
import os

# Default config file content.
# We use it as a base to avoid to have any missing keys in case the config.json file is incomplete.
# We also use it to check the types and avoid to load extra keys for security.
config = {
    "max_download_retries": 10,
    "retry_cooldown": 3,
    "pytube_range_size_bytes": 1048576,  # 1 MB (1024 KB * 1024 KB).
    "download_bars_length": 20,
    "default_download_option_number": 1, # Full video download option.
    "default_download_destination": "./",
    "default_download_resolution": "1080p",
    "default_subtitle_lang": "a.en",     # English (auto generated).
    "block_age_restricted_content": True,
    "auto_mp3_conversion": True
}


def check_input (
    key:  str,
    input: any
) -> bool:
    """
    Compare the type of an input key with the type of the actual key.

    Tasks:
        1) Retrieve the input key type.
        2) Check for a match with the type of the actual key.

    Parameters:
        - key  / str / Key to validate.
        - data / any / Input key.

    Returns:
        True if there is a match.
        False if not.
    """

    expected_type = type(config[key])
    return isinstance(input, expected_type)


def load_config_file() -> None:
    """
    Load keys from the config.json file.

    Tasks:
        1) Check the existence of the config.json file.
        2) Read the file and load the data as JSON.
        3) Verify the retrieved keys and overwrite the default config if valid.

    Parameters:
        No parameters.

    Returns:
        No object returned.
    """

    if not os.path.exists("./config.json"):
        print("Config file missing! The default configuration will be used.")
        return

    config_file_data = None

    with open("config.json", "r") as file:
        config_file_data = json.load(file)

    for key in config:
        if key in config_file_data and check_input(key, config_file_data[key]):
            config[key] = config_file_data[key]


def get_config_data():
    """
    Return the configuration of the program.

    Tasks:
        1) Get and return the config.

    Parameters:
        No parameters.

    Returns:
        A dictionary containing the app configuration.
    """

    return config
