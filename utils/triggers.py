"""
Trigger query can be found here:

https://searchfox.org/mozilla-central/source/toolkit/components/places/nsPlacesTriggers.h

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this file,
you can obtain one at http://mozilla.org/MPL/2.0/.
"""


IS_PLACE_QUERY = "url_hash BETWEEN HASH('place', 'prefix_lo') AND HASH('place', 'prefix_hi')"


CREATE_BOOKMARKS_FOREIGNCOUNT_AFTERINSERT_TRIGGER = f"""
CREATE TEMP TRIGGER moz_bookmarks_foreign_count_afterinsert_trigger
AFTER INSERT ON moz_bookmarks FOR EACH ROW
BEGIN
UPDATE moz_places
SET frecency = (CASE WHEN {IS_PLACE_QUERY} THEN 0 ELSE 1 END)
WHERE frecency = -1 AND id = NEW.fk;
UPDATE moz_places
SET foreign_count = foreign_count + 1,
    hidden = {IS_PLACE_QUERY},
    recalc_frecency = NOT {IS_PLACE_QUERY},
    recalc_alt_frecency = NOT {IS_PLACE_QUERY}
WHERE id = NEW.fk;
END;
"""

CREATE_PLACES_AFTERINSERT_TRIGGER = """
CREATE TEMP TRIGGER moz_places_afterinsert_trigger
AFTER INSERT ON moz_places FOR EACH ROW
BEGIN
    INSERT INTO moz_origins
    (prefix, host, frecency, recalc_frecency, recalc_alt_frecency)
    VALUES (
        get_prefix(NEW.url), 
        get_host_and_port(NEW.url),
        NEW.frecency, 
        1, 1
    )
    ON CONFLICT(prefix, host) DO UPDATE
    SET recalc_frecency = 1, recalc_alt_frecency = 1
    WHERE 
        EXCLUDED.recalc_frecency = 0 OR
        EXCLUDED.recalc_alt_frecency = 0;
    UPDATE moz_places SET origin_id = (
        SELECT id
        FROM moz_origins
        WHERE 
            prefix = get_prefix(NEW.url)
            AND host = get_host_and_port(NEW.url)
    )
    WHERE id = NEW.id;
END;
"""
