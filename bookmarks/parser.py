from __future__ import annotations

import re
from typing import Tuple

from bookmarks.bookmark_types import Bookmark, BookmarkFolder, BookmarkTree


def print_tree(nodes: BookmarkTree, indent: int = 0):
    prefix = "  " * indent
    for node in nodes:
        if isinstance(node, BookmarkFolder):
            print(f"{prefix}📁 {node.name} ({len(node.items)} items)")
            # Recursive call to print the items in the folder
            print_tree(node.items, indent + 1)
        elif isinstance(node, Bookmark):
            print(f"{prefix}🔗 {node.name} -> {node.url[:50]}...")


def parse_dl_node(lines, pointer) -> Tuple[BookmarkTree, int]:
    tree: BookmarkTree = []

    while pointer < len(lines):
        line = lines[pointer].strip()
        if line.lower().startswith("</dl>"):
            # End of the current DL node
            return tree, pointer + 1
        elif line.lower().startswith("<dt>"):
            # Bookmark or folder
            if "<a " in line.lower():
                # Bookmark
                name_match = re.search(r'>([^<]*)</a>', line, re.IGNORECASE)
                name = name_match.group(1).strip() if name_match else "Unnamed Bookmark"
                
                # URL
                url_match = re.search(r'href="([^"]*)"', line, re.IGNORECASE)
                url = url_match.group(1).strip() if url_match else ""
                
                tree.append(Bookmark(name=name, url=url))

                pointer += 1
            elif "<h3>" in line.lower():
                # Folder
                name_match = re.search(r'<h3>([^<]*)</h3>', line, re.IGNORECASE)
                name = name_match.group(1).strip() if name_match else "Unnamed Folder"
                
                folder, pointer = parse_dl_node(lines, pointer + 1)
                tree.append(BookmarkFolder(name=name, items=folder))
        else:
            pointer += 1
        
    return tree, pointer


def parse_html_bookmark(html_content):
    lines = html_content.splitlines()
    for pointer, line in enumerate(lines):
        if line.lower().startswith("<dl"):
            # Root DL
            bookmarks, _ = parse_dl_node(lines, pointer+1)
            return bookmarks
