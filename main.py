import argparse
import configparser
import os
from shutil import copy2
import sqlite3
from traceback import print_exception
from urllib import request

import urllib
import urllib.error


from bookmarks.bookmark import determine_root_guid, fetch_bookmark, insert_tree, remove_tree_if_exists
from bookmarks.parser import parse_html_bookmark
from utils.hash import hash_function
from utils.guid import generate_guid
from utils.places import get_host_and_port, get_prefix
from utils.triggers import CREATE_BOOKMARKS_FOREIGNCOUNT_AFTERINSERT_TRIGGER, CREATE_PLACES_AFTERINSERT_TRIGGER


def main(args: argparse.Namespace):
    config = configparser.ConfigParser()
    config.read(args.config)

    profile_path = config.get("path", "firefox_profile")
    bookmarks_url = config.get("path", "bookmarks_url")
    remove_if_duplicate = config.getboolean("options", "remove_if_duplicate")
    root_guid = determine_root_guid(config.get("options", "root_folder"))

    if not os.path.exists(profile_path):
        print(f"Profile path does not exist: {profile_path}. Please check your configuration.")
        exit(1)

    db_path = os.path.join(profile_path, "places.sqlite")
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}. Please check your configuration.")
        exit(1)

    if os.path.exists(os.path.join(profile_path, "parent.lock")) and not args.yes:
        print("[WARNING] A parent.lock file exists in the profile directory. Proceeding will cause potential data loss.")
        pick = input("Do you want to continue? (yes/no) [no]: ").strip().lower()
        if pick not in ["yes", "y"]:
            print("Exiting without making changes.")
            return

    # Backup the existing database file
    backup_path = db_path + ".auto.bak"
    copy2(db_path, backup_path)
    print(f"Backup of the database created at {backup_path}")

    conn = None
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=rw", uri=True)
        print("Binding Functions...")
        conn.create_function("HASH", -1, hash_function)
        conn.create_function("GENERATE_GUID", 0, generate_guid)
        conn.create_function("get_prefix", 1, get_prefix)
        conn.create_function("get_host_and_port", 1, get_host_and_port)

        print("Creating temp trigger...")
        conn.execute(CREATE_BOOKMARKS_FOREIGNCOUNT_AFTERINSERT_TRIGGER)
        conn.execute(CREATE_PLACES_AFTERINSERT_TRIGGER)

        cursor = conn.cursor()
        root = fetch_bookmark(cursor, root_guid)
        if not root:
            print(f"Root bookmark with GUID {root_guid} not found. Possibily the profile is not set up correctly.")
            return

        try:
            print("Fetching bookmarks...")
            html_content = request.urlopen(bookmarks_url).read().decode("utf-8")
        except urllib.error.HTTPError as e:
            print(f"HTTP Error fetching bookmarks: {e.code} - {e.reason}")
            return
        except urllib.error.URLError as e:
            print(f"URL Error fetching bookmarks: {e.reason}")
            return

        print("Parsing bookmarks...")
        bookmarks = parse_html_bookmark(html_content)
        if not bookmarks:
            print("No bookmarks found in the provided HTML content.")
            return

        if remove_if_duplicate:
            print("Removing existing bookmarks in the root folder...")
            remove_tree_if_exists(cursor, bookmarks, root.id)

        print("Inserting bookmarks...")
        insert_tree(cursor, bookmarks, root.id, root.guid)

        conn.commit()

        print(f"Bookmarks successfully inserted into the Firefox profile at {profile_path}.")

    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print("Database is locked. Please close Firefox and try again.")
            return
        else:
            print_exception(e)
            print(f"Database connection error: {e}")
            return
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Import bookmarks from an HTML file into a Firefox profile.")
    arg_parser.add_argument(
        "-y", "--yes", action="store_true", help="Automatically confirm the presence of parent.lock file without prompting."
    ) 
    arg_parser.add_argument(
        "-c", "--config", type=str, default="config", help="Path to the configuration file (default: 'config')."
    )
    args = arg_parser.parse_args()
    main(args)
