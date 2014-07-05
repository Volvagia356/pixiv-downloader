pixiv Downloader
================

Info
----
pixiv Downloader is a script that batch downloads artworks of a specified artist
from [pixiv](http://www.pixiv.net/).

Python 2.7 is required.

Usage
-----
```pixivdl.py artist_id|tag [directory]```

```artist_id``` refers to the unique numerical ID for the artist, which can be
found in the URL. For example, ```http://www.pixiv.net/member.php?id=92448``` would
have an ID of ```92448```.

```tag``` refers to a pixiv tag, applied by the artist to a work.

If all characters of the argument are digits, it is assumed to be an artist ID.
Otherwise, it is assumed to be a tag.

```directory``` specifies the directory in which works would be downloaded to.
It is optional, and works will be downloaded to the present working directory
if it is not specified.

A ```metadata.pickle``` file is also placed in the download directory. This file
is a Python pickle of the ```Work``` objects from the ```pixiv_api``` module
used by the script. It contains metadata like the titles, descriptions, etc.
of each work, as fetched from the API.

GUI
---
A GUI has been implemented in Tkinter can be found in ```pixivdl-gui.py```.
The inputs for the GUI are similar to the command line arguments.

Do note that when "Cancel" is clicked, the download process isn't immediately cancelled.
Instead, it would only be cancelled when the current work has completed downloading.

Logging In
----------
This script works without logging in to pixiv. However, if you want to download
R18 images or MyPixiv-only images that are made available to you, you must
authenticate yourself.

Unfortunately, I could not figure out how logging in works, and thus have used
an alternative method. You must first log in to pixiv in your web browser, 
then copy the contents of the PHPSESSID cookie into a file at ```~/.config/pixivdl/session```

API
---
As there isn't an official publically documented API for pixiv, I had to poke at
their iOS app and figure out how the undocumented API for that worked. There is
a basic interface to that API in the ```pixiv_api``` module included in here,
though just enough for this script to work.
