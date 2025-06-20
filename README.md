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

2. **Configure the tool**:
   - Open `config` and set the `profile_path` to your Firefox profile path.
   - Set the `bookmarks_url` to the URL of the HTML file containing your online bookmarks.
   - Set `root_folder` to root bookmark folder where you want to import the bookmarks. (options can be `toolbar`, `menu`, `unfiled`, or `mobile`). Default is `toolbar`.
   - Set `remove_if_duplicate` to `true` if you want to remove existing bookmarks with same name in the root folder before importing. Default is `true`.

3. **Run the tool**:

   At least python 3.8+ required to run
   ```bash
    python main.py
    ```

## Features
This program is compatible with scheduled tasks (cron job / task scheduler) by supplying the `-y` flag to the command line, which will run the import without prompting for confirmation.
   ```bash
   python main.py -y
   ```
Additionally, you can specify the `--config` option to use a different configuration file.
   ```bash
   python main.py -y --config /path/to/your/config
   ```

## Disclaimer

**This project is intended for personal use only.**

The author of this project are not responsible for any data loss or corruption that may occur as a result of using this software. It is strongly recommended to back up your Firefox profile and bookmarks before using this tool.

No support is provided for any errors, issues, or unexpected behavior that fall outside the direct scope and functionality of this project. Use at your own risk.