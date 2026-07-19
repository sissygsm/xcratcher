import configparser
import os
import platform
import sqlite3

from dotenv import load_dotenv

load_dotenv()

X_USERNAME = os.environ["X_USERNAME"]


def _firefox_base_dirs():
    system = platform.system()
    if system == "Windows":
        return [os.path.join(os.environ["APPDATA"], "Mozilla", "Firefox")]
    if system == "Linux":
        return [
            os.path.expanduser("~/.mozilla/firefox"),
            os.path.expanduser("~/snap/firefox/common/.mozilla/firefox"),
        ]
    raise OSError(f"Unsupported OS: {system}")


def _read_profiles_ini(base_dir):
    ini_path = os.path.join(base_dir, "profiles.ini")
    if not os.path.exists(ini_path):
        return None, []

    parser = configparser.ConfigParser()
    parser.read(ini_path)

    default_path = None
    for section in parser.sections():
        if section.startswith("Install") and parser.has_option(section, "Default"):
            default_path = parser.get(section, "Default")
            break
    if default_path is None:
        for section in parser.sections():
            if parser.has_option(section, "Path") and parser.get(section, "Default", fallback="0") == "1":
                default_path = parser.get(section, "Path")
                break

    profile_paths = [
        parser.get(section, "Path")
        for section in parser.sections()
        if section.startswith("Profile") and parser.has_option(section, "Path")
    ]

    return default_path, profile_paths


def _has_x_login(profile_path):
    db_path = os.path.join(profile_path, "cookies.sqlite")
    if not os.path.exists(db_path):
        return False
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            row = con.execute(
                "SELECT 1 FROM moz_cookies WHERE name='auth_token' "
                "AND (host LIKE '%x.com' OR host LIKE '%twitter.com') LIMIT 1"
            ).fetchone()
            return row is not None
        finally:
            con.close()
    except sqlite3.Error:
        return False


def _find_named_profile(base_dir, name):
    for candidate in (name, f"{name}.default-release"):
        path = os.path.join(base_dir, candidate)
        if os.path.isdir(path):
            return path
    for entry in os.listdir(base_dir):
        if entry.startswith(name) and os.path.isdir(os.path.join(base_dir, entry)):
            return os.path.join(base_dir, entry)
    return None


def _autodetect_profile(base_dir):
    default_path, profile_paths = _read_profiles_ini(base_dir)

    candidates = ([default_path] if default_path else []) + [
        p for p in profile_paths if p != default_path
    ]
    logged_in = [
        p for p in candidates
        if os.path.isdir(os.path.join(base_dir, p)) and _has_x_login(os.path.join(base_dir, p))
    ]
    if not logged_in:
        return None
    # Prefer Firefox's own default profile if it's one of the logged-in ones.
    return os.path.join(base_dir, default_path if default_path in logged_in else logged_in[0])


def get_firefox_profile_path():
    override = os.environ.get("FIREFOX_PROFILE_CODE")

    for base_dir in _firefox_base_dirs():
        if not os.path.isdir(base_dir):
            continue

        if override:
            profile_path = _find_named_profile(base_dir, override)
        else:
            profile_path = _autodetect_profile(base_dir)

        if profile_path:
            return profile_path

    if override:
        raise FileNotFoundError(f"Firefox profile matching '{override}' was not found.")
    raise FileNotFoundError(
        "Could not auto-detect a Firefox profile logged into X/Twitter. "
        "Log into X in Firefox, or set FIREFOX_PROFILE_CODE in .env to point at a specific profile."
    )


FIREFOX_PROFILE = get_firefox_profile_path()

# geckodriver copies FIREFOX_PROFILE into a fresh temp dir and launches Firefox
# against that copy. When Firefox is snap-packaged, its sandbox can't see the
# system /tmp (private per-snap mount) or ~/.cache (excluded from the "home"
# interface) - either one causes a "profile cannot be loaded" failure. A plain,
# non-hidden directory anywhere under $HOME (this project dir qualifies) is
# visible to the sandbox, so point geckodriver's temp dir there instead.
_SELENIUM_TMP_DIR = os.path.abspath("firefox_tmp_profile")
os.makedirs(_SELENIUM_TMP_DIR, exist_ok=True)
os.environ["TMPDIR"] = _SELENIUM_TMP_DIR
