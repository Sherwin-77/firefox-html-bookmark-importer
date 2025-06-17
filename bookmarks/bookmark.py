"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this file,
you can obtain one at http://mozilla.org/MPL/2.0/.
"""

from sqlite3 import Cursor
import time
from typing import List, Optional

from bookmarks.bookmark_types import Bookmark, BookmarkFolder, BookmarkInfo, BookmarkTree
from utils.places import maybe_insert_place
from utils.guid import generate_guid

TYPE_BOOKMARK = 1
TYPE_FOLDER = 2
TYPE_SEPARATOR = 3


"""
See: https://searchfox.org/mozilla-central/source/toolkit/components/places/nsINavBookmarksService.idl

Sync status flags, stored in Places for each item. These affect conflict
resolution, when an item is changed both locally and remotely; deduping,
when a local item matches a remote item with similar contents and different
GUIDs; and whether we write a tombstone when an item is deleted locally.
Status  | Description               | Conflict   | Can     | Needs
        |                           | resolution | dedupe? | tombstone?
-----------------------------------------------------------------------
UNKNOWN | Automatically restored    | Prefer     | No      | No
        | on startup to recover     | deletion   |         |
        | from database corruption, |            |         |
        | or sync ID change on      |            |         |
        | server.                   |            |         |
-----------------------------------------------------------------------
NEW     | Item not uploaded to      | Prefer     | Yes     | No
        | server yet, or Sync       | newer      |         |
        | disconnected.             |            |         |
-----------------------------------------------------------------------
NORMAL  | Item uploaded to server.  | Prefer     | No      | Yes
        |                           | newer      |         |

"""
SYNC_STATUS_UNKNOWN = 0
SYNC_STATUS_NEW = 1
SYNC_STATUS_NORMAL = 2


ROOT_GUID = "root________"
MENU_GUID = "menu________"
TOOLBAR_GUID = "toolbar_____"
UNFILED_GUID = "unfiled_____"
MOBILE_GUID = "mobile______"

TAGS_GUID = "tags________"

user_content_roots = [
    MENU_GUID,
    TOOLBAR_GUID,
    UNFILED_GUID,
    MOBILE_GUID,
]


class BookmarkRow(object):
    def __init__(
        self, id, type, fk, parent, position, title, keyword_id, folder_type, guid, sync_status, sync_change_counter
    ):
        self.id = id
        self.type = type
        self.fk = fk
        self.parent = parent
        self.position = position
        self.title = title
        self.keyword_id = keyword_id
        self.folder_type = folder_type
        self.guid = guid
        self.sync_status = sync_status
        self.sync_change_counter = sync_change_counter


def determine_root_guid(name: str) -> str:
    name = name.lower()
    if name == "menu":
        return MENU_GUID
    elif name == "toolbar":
        return TOOLBAR_GUID
    elif name == "unfiled":
        return UNFILED_GUID
    elif name == "mobile":
        return MOBILE_GUID
    else:
        raise ValueError(f"Unknown root name: {name}. Expected one of: {user_content_roots}")


def fetch_bookmark(db: Cursor, guid: str) -> Optional[BookmarkRow]:
    row = db.execute(
        """
        SELECT b.id, b.type, b.fk, b.parent, b.position, b.title, b.keyword_id, b.folder_type, b.guid, b.syncStatus AS sync_status, b.syncChangeCounter AS sync_change_counter
        FROM moz_bookmarks b
        WHERE b.guid = :guid
        """,
        {"guid": guid},
    ).fetchone()

    if row is None:
        return None

    return BookmarkRow(*row)


def remove_folder_contents(db: Cursor, guids: List[str]):
    if not guids:
        return

    for guid in guids:
        db.execute(
            """
            WITH RECURSIVE
            descendants(did) AS (
                SELECT b.id FROM moz_bookmarks b
                JOIN moz_bookmarks p ON b.parent = p.id
                WHERE p.guid = :guid
                UNION ALL
                SELECT id FROM moz_bookmarks
                JOIN descendants ON parent = did
            )
            DELETE FROM moz_bookmarks WHERE id IN descendants
            """,
            {"guid": guid},
        )


def insert_bookmarks(db: Cursor, items: List[BookmarkInfo]):
    db.executemany(
        """
        INSERT INTO moz_bookmarks (fk, type, parent, position, title, 
                                dateAdded, lastModified, guid, 
                                syncChangeCounter, syncStatus)
        VALUES (
            (CASE WHEN :url ISNULL THEN NULL ELSE (SELECT id FROM moz_places WHERE url_hash = HASH(:url) AND url = :url) END),
            :type,
            (SELECT id FROM moz_bookmarks WHERE guid = :parent_guid),
            IFNULL(:position, (SELECT COUNT(*) FROM moz_bookmarks WHERE parent = :root_id)),
            NULLIF(:title, ''),
            :date_added,
            :last_modified,
            :guid,
            :syncChangeCounter,
            :syncStatus
        )
        """,
        items,
    )


def remove_tree_if_exists(db: Cursor, tree: BookmarkTree, root_id: int):
    if not tree:
        return

    names = [item.name for item in tree]
    rows = db.execute(
        """
        SELECT guid FROM moz_bookmarks
        WHERE parent = ? AND title IN ({})
        """.format(
            ', '.join(['?'] * len(names))
        ),
        [root_id] + names,
    ).fetchall()
    guids = [row[0] for row in rows]

    if guids:
        remove_folder_contents(db, guids)
        db.execute(
            "DELETE FROM moz_bookmarks WHERE guid IN ({})".format(
                ', '.join(['?'] * len(guids))
            ),
            guids,
        )


def insert_tree(
    db: Cursor,
    tree: BookmarkTree,
    root_id: int,
    parent_guid: str,
    position: Optional[int] = None,
    date_added: Optional[int] = None,
):
    if not tree:
        return

    now = date_added or int(time.time() * 1_000_000)

    items: List[BookmarkInfo] = []

    for item in tree:
        if isinstance(item, Bookmark):
            maybe_insert_place(db, item.url)
            items.append(
                {
                    "url": item.url,
                    "type": TYPE_BOOKMARK,
                    "root_id": root_id,
                    "parent_guid": parent_guid,
                    "title": item.name,
                    "position": position,
                    "date_added": now,
                    "last_modified": now,
                    "guid": generate_guid(),
                    "syncStatus": SYNC_STATUS_NEW,
                    "syncChangeCounter": 1,
                }
            )
        elif isinstance(item, BookmarkFolder):
            folder_guid = generate_guid()
            insert_bookmarks(
                db,
                [
                    {
                        "url": None,
                        "type": TYPE_FOLDER,
                        "root_id": root_id,
                        "parent_guid": parent_guid,
                        "title": item.name,
                        "position": position,
                        "date_added": now,
                        "last_modified": now,
                        "guid": folder_guid,
                        "syncStatus": SYNC_STATUS_NEW,
                        "syncChangeCounter": 1,
                    }
                ],
            )
            insert_tree(db, item.items, root_id, folder_guid)
        else:
            raise TypeError(f"Unknown item type: {type(item)}")

    if items:
        insert_bookmarks(db, items)
