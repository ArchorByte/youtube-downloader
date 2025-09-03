# Youtube Downloader
Download YouTube videos and playlists for free! <br/>
This Python program can run on Windows, Linux, MacOS and even Android!
> **Warning:** VPNs can provoke some unexpected results such as download failures or major slow downs.

# 📦 Requirements
- Python interpreter (**3.7+ recommended**).
- Internet connection ;-).
- FFmpeg (**the program handles it automatically**).

# 📥 Installation
1) Download the program. <br/>
2) Check for libraries updates (**update.bat** / **update.sh**). <br/>
3) Run the program using `python main.py` <br/>
4) Enjoy!

# ⚙️ Configuration
You can configure the program using the `config.json` file. <br/>
The default configuration is available at the bottom of this section. <br/>
Here are the different options you have:
- `"max_download_retries"` -> Maximum amount of retries the program does when a download fail, before aborting.
- `"pytube_range_size_bytes"` -> Amount in bytes to download to trigger the download callback.
- `"default_download_option_number"` -> Download option we use by default.
- `"default_download_destination"` -> Destination path where the program puts the downloaded file by default.
- `"default_download_resolution"` -> Resolution of the video files by default (if available, otherwise we propose the highest).
- `"default_subtitle_lang"` -> Language of the subtitles by default (only proposed if available).
- `"block_age_restricted_content"` -> Disallow the download of YouTube videos that have age restriction.
``` json
{
    "max_download_retries": 10,
    "pytube_range_size_bytes": 1048576,
    "default_download_option_number": 1,
    "default_download_destination": "./",
    "default_download_resolution": "1080p",
    "default_subtitle_lang": "a.en",
    "block_age_restricted_content": false
}
```

# 🤝 User Agreement
By downloading and/or using this program, you confirm that you are solely responsible for how you use this software, especially if you download copyrighted content or if you break the YouTube terms of service. You agree as well that this agreement extends to any prior version of the program, and any new version of the user agreement in any future update, overwrites this one.

# 💻 Contribution
If you want to contribute to the project, please respect the global syntax and the file naming. If the syntax is not respected and/or the file naming is not conform, we may reject your pull request! <br/>
**Do not forget to verify that your fork is up-to-date before making a pull request!** <br/>
Here is the project tree:
- `dependencies/` -> Bundled dependencies of the program.
- `src/` -> Source code of the program.
