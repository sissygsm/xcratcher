#########################################################
# Configure FIREFOX_PROFILE_CODE & X_USERNAME in .env
# (copy .env.example to .env and fill in your values)
#########################################################

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager

import time
import os
import platform

import config

# Create downloads directory if it doesn't exist
DOWNLOADS_DIR = "./downloads"
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)


def get_firefox_profile_path():
    system = platform.system()

    if system == "Windows":
        profile_path = os.path.join(
            os.environ["APPDATA"],"Mozilla", "Firefox", "Profiles", config.FIREFOX_PROFILE
        )

        if not os.path.exists(profile_path):
            raise FileNotFoundError(f"Firefox profile path does not exist: {profile_path}")
    elif system == "Linux":
        # Possible paths
        classic_path = os.path.expanduser(
            f"~/.mozilla/firefox/{config.FIREFOX_PROFILE}")
        snap_path = os.path.expanduser(
            f"~/snap/firefox/common/.mozilla/firefox/{config.FIREFOX_PROFILE}")

        # Detect which exists
        if os.path.exists(classic_path):
            profile_path = classic_path
        elif os.path.exists(snap_path):
            profile_path = snap_path
        else:
            raise FileNotFoundError(f"Firefox profile path does not exist: {profile_path}")
    else:
        raise OSError(f"Unsupported OS: {system}")

    return profile_path


def scrap_links_withFirefox(username):
    # Create user-specific directory
    user_dir = os.path.join(DOWNLOADS_DIR, username)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    # Driver configurations
    profile_path = get_firefox_profile_path()
    fp = webdriver.FirefoxProfile(profile_path)
    options = webdriver.FirefoxOptions()
    options.profile = fp
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    driver.get(f"https://x.com/{username}/media")
    time.sleep(5)

    len_set, len_all_links = -1, 0
    all_links = set()
    while len_set != len_all_links:
        len_set = len_all_links
        elements = driver.find_elements(By.TAG_NAME, "a")
        links = {e.get_attribute("href") for e in elements}
        all_links |= links
        len_all_links = len(all_links)
        driver.execute_script("""window.scrollTo(0, document.body.scrollHeight);
                            window.scrollTo(document.body.scrollHeight, 0);
                            window.scrollTo(0, document.body.scrollHeight);""")
        time.sleep(3)

    driver.quit()
    return all_links


def filter_links(x_links, username):
    media_links = [l for l in x_links if f"/{username}/status/" in l]
    print(f"\nTotal media links found: {len(media_links)}")
    # Filter by type (videos only)
    video_links = [l for l in media_links if "/video/" in l]
    print(f"\nTotal video links found: {len(video_links)}")
    # Cut the link to only show https://x.com/user/video_number
    cleaned_links = [link[:-8] for link in video_links]
    #cleaned_links = ["/".join(link.split("/")[:2]) for link in video_links]
    cleaned_links.sort()
    return cleaned_links


def save_pending_links(links, username, file="pending_links.txt"):
    user_dir = os.path.join(DOWNLOADS_DIR, username)
    file_path = os.path.join(user_dir, file)
    with open(file_path, "a") as f:
        for link in links: 
            f.write(link + "\n")    
    print(f"\n{len(links)} new video links saved to {file_path}")


x_links = scrap_links_withFirefox(config.X_USERNAME)
video_links_only = filter_links(x_links, config.X_USERNAME)
save_pending_links(video_links_only, config.X_USERNAME)
