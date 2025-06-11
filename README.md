# Firefox HTML Bookmark Importer

This project is a tool designed to import bookmarks from an **Online** HTML file into Firefox.

Worked tested on Firefox 139.0 Windows

Originally created to import bookmarks specifically from [FMHY Bookmarks](https://github.com/fmhy/bookmarks) that is generated automatically. Might work with other similar HTML bookmark files, but not guaranteed.

## Running the Tool
**Strongly recommended to run this tool when Firefox is closed. Backup places.sqlite before running**

Profile path can be found in Firefox by going to `about:profiles` and looking for the profile you want to use on root directory.
1. **Clone the repository**:
   ```bash
   git clone
   cd firefox-bookmark-importer
   ```
2. **Install dependencies**:
    It is recommended to use virtual environments
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
    ```bash
    pip install -r requirements.txt
    ```
3. **Configure the tool**:
   - Open `config` and set the `profile_path` to your Firefox profile path.
   - Set the `bookmarks_url` to the URL of the HTML file containing your online bookmarks.
   - Set `root_folder` to root bookmark folder where you want to import the bookmarks. (options can be `toolbar`, `menu`, `unfiled`, or `mobile`). Default is `toolbar`.
   - Set `remove_if_duplicate` to `true` if you want to remove existing bookmarks with same name in the root folder before importing. Default is `true`.

4. **Run the tool**:
   ```bash
    python main.py
    ```

## Disclaimer

**This project is intended for personal use only.**

The author of this project are not responsible for any data loss or corruption that may occur as a result of using this software. It is strongly recommended to back up your Firefox profile and bookmarks before using this tool.

No support is provided for any errors, issues, or unexpected behavior that fall outside the direct scope and functionality of this project. Use at your own risk.