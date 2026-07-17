# Project Goals

This project has **two main objectives**:

1. **Scrape video/media links** from the Media section of your own **X/Twitter account**.
2. **Download the scraped links** using an automated script.

> **Important**: This tool is not recommended for scraping videos from other users' profiles. Please do not use it without their explicit permission.

---

## Ingredients

Before you start:

- Install the required packages:

```bash
pip install -r requirements.txt
```

- Download **FFmpeg** and add its location to the `PATH` environment variable.

- Install **Firefox** and either create or sign in with your X/Twitter account. In Linux, reinstalling .deb version is better than snap version because of problems with finding Firefox profiles.

- Log into your X/Twitter account in Firefox to avoid media loading restrictions when accessing the platform without being logged in.

- Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

  - `FIREFOX_PROFILE_CODE`: your Firefox profile code, i.e. the random string before `.default-release`. The profile is created by default and is usually located in:

    ```bash
    C:\Users\your_user\AppData\Roaming\Mozilla\Firefox\Profiles
    ```

  - `X_USERNAME`: your X/Twitter handle, without the `@` symbol.

`.env` is gitignored, so your values are never committed.


## Procedure

### Scraping Video Links
This is done using the script xcrapping_video_links.py. Follow these steps:

a. Open the project in a code editor that can run scripts (e.g., VSCode), then Add Folder to Workspace. Select the root folder containing the src directory.

b. Run the script (from the project root, so it can find `.env` and the `downloads` folder):

```bash
python src/xcrapping_video_links.py
```

The WebDriver will open Firefox and navigate to your X/Twitter media page. It will scroll down to load more content, scraping video and image links as it goes. Once it reaches the top of your timeline, it will close the browser, create a folder with your X username, and save the links into a pending_links.txt file.

Note: Due to network speed issues, some videos and images might not load in time and may not be captured. It’s a good idea to compare the number of scraped links with what is shown on your X/Twitter media tab.


### Downloading the Scraped Links
This is done with the dling_videos_from_links.py script:

a. With the same editor and workspace open, go to the file dling_videos_from_links.py.

b. Run the script:

```bash
python src/dling_videos_from_links.py
```

It will read the pending_links.txt file from the folder named after your username, download each video using yt_dlp, and save them in the same folder.

If a rate-limit exceeded error occurs, the script will stop. In that case, wait for the rate to reset and run the script again.

## Conclusions
This project demonstrates how X/Twitter can be used as a learning platform for working with libraries like yt_dlp and selenium for web automation.

## Recommendations
Ensure you have a good internet connection to avoid incomplete scraping and slow downloads.
