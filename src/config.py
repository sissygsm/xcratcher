import os

from dotenv import load_dotenv

load_dotenv()

FIREFOX_PROFILE = os.environ["FIREFOX_PROFILE_CODE"] + ".default-release"
X_USERNAME = os.environ["X_USERNAME"]
