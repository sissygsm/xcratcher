#########################################################
# Long-lived controller for the Firefox window opened by
# `make setup`. Launched once in the background; later
# `make setup ACCOUNT=...` calls write a URL to CMD_FILE
# instead of starting a second Firefox process.
#########################################################

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

import os
import sys
import time

import config

CACHE_DIR = ".cache"
CMD_FILE = os.path.join(CACHE_DIR, "firefox_daemon.cmd")
QUIT_SENTINEL = "__QUIT__"


def main():
    initial_url = sys.argv[1] if len(sys.argv) > 1 else None

    fp = webdriver.FirefoxProfile(config.FIREFOX_PROFILE)
    options = webdriver.FirefoxOptions()
    options.profile = fp
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    if initial_url:
        driver.get(initial_url)
        print(f"Opened {driver.current_url}", flush=True)

    try:
        while True:
            time.sleep(0.5)
            if not os.path.exists(CMD_FILE):
                continue
            with open(CMD_FILE) as f:
                cmd = f.read().strip()
            os.remove(CMD_FILE)
            if cmd == QUIT_SENTINEL:
                break
            elif cmd:
                driver.get(cmd)
                print(f"Navigated to {driver.current_url}", flush=True)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
