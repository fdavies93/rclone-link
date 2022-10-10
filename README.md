# Rclone Link

This is a simple python script designed to work with rclone and inotify to keep a directory contents synchronised with a remote source (e.g. Google Drive, Dropbox, etc.)

I developed it to work with Obsidian or other similar note-taking apps on different devices. This is because Obsidian uses autosave as a core part of its functionality, and other synching methods have various issues:

* GNOME drive integration creates unusual pathnames with Obsidian and many other programs (e.g. VSCode).
* Directly mounting a remote works fine but introduces very bad latency for apps like Obsidian which rely on autosave.
* Manual syncs are annoying to remember to maintain, especially for note-taking purposes.

Because it uses inotifywait it will only work on Linux systems. I might update it for MacOS / Windows if there's interest.