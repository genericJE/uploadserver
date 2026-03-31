# uploadserver

Minimal upload-only HTTP server. No dependencies beyond Python 3 stdlib.

## Features

- Drag & drop + file picker
- Upload progress bar
- Toast notifications for success/failure
- Dark mode support
- No directory listing, no downloads — upload only

## Install

```
git clone https://github.com/genericJE/uploadserver.git
cd uploadserver
chmod +x uploadserver.py

# optional: symlink into PATH
ln -s "$(pwd)/uploadserver.py" /usr/local/bin/uploadserver
```

## Usage

```
uploadserver.py          # port 8000
uploadserver.py 9000     # custom port
```

Listens on `0.0.0.0` so it's reachable from other devices on the network.

Upload directory defaults to `~/Downloads`. Override with:

```
UPLOAD_DIR=/tmp/uploads uploadserver.py
```
