import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = str(os.path.dirname(APP_DIR))
DEFAULT_DATA_DIR = os.path.join(PROJECT_ROOT, "data")
PLAYWELL_DATA_DIR = os.getenv("PLAYWELL_DATA_DIR", DEFAULT_DATA_DIR)

DB_PATH = os.path.join(PLAYWELL_DATA_DIR, "playwell.db")
CONTENTS_DIR = os.path.join(PLAYWELL_DATA_DIR, "contents")

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.svg")
