"""
Database query can be found here:

https://searchfox.org/mozilla-central/source/toolkit/components/places/PlacesUtils.sys.mjs


This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this file,
you can obtain one at http://mozilla.org/MPL/2.0/.
"""

from sqlite3 import Cursor
from urllib.parse import urlparse


def get_prefix(url: str) -> str:
    scheme = urlparse(url).scheme
    return scheme + "://" if scheme else ""


def get_host_and_port(url: str) -> str:
    return urlparse(url).netloc or ""


def maybe_insert_place(db: Cursor, url: str) -> None:
    parsed = urlparse(url)
    db.execute(
        """
        INSERT OR IGNORE INTO moz_places (url, url_hash, rev_host, hidden, frecency, guid)
        VALUES (
            :url, HASH(:url), :rev_host,
            (CASE WHEN :url BETWEEN 'place:' AND 'place:' || X'FFFF' THEN 1 ELSE 0 END),
            :frecency,
            IFNULL(
                (SELECT guid FROM moz_places WHERE url_hash = hash(:url) AND url = :url),
                GENERATE_GUID()
            )
        )
        """,
        {
            "url": url,
            "rev_host": parsed.netloc[::-1] + ".",
            "frecency": 0 if parsed.scheme == "place" else -1,
        },
    )


def fetch_place_id(db: Cursor, url: str) -> int:
    row = db.execute(
        """
        SELECT id FROM moz_places WHERE url = :url
        """,
        {"url": url},
    ).fetchone()

    if row is None:
        return -1

    return row[0]
