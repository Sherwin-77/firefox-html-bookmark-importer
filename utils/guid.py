"""
GUID generation can be found here:
https://searchfox.org/mozilla-central/source/toolkit/components/places/Helpers.cpp

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this file,
you can obtain one at http://mozilla.org/MPL/2.0/.
"""

import base64
import secrets


GUID_LENGTH = 12


def generate_guid():
    required_bytes = (GUID_LENGTH * 3) // 4

    random_bytes = secrets.token_bytes(required_bytes)
    guid = base64.urlsafe_b64encode(random_bytes).rstrip(b'=').decode('ascii')

    if len(guid) != GUID_LENGTH:
        raise ValueError(f"Generated GUID length is {len(guid)}, expected {GUID_LENGTH}")

    return guid


def is_valid_guid(guid: str) -> bool:
    if len(guid) != GUID_LENGTH:
        return False

    for c in guid:
        if (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or (c >= '0' and c <= '9') or c == '-' or c == '_':
            continue

        return False

    return True
