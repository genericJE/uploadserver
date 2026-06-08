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
brew install genericJE/tools/uploadserver

# Or manually install

git clone https://github.com/genericJE/uploadserver.git
cd uploadserver
chmod +x uploadserver.py

# optional: symlink into PATH
ln -s "$(pwd)/uploadserver.py" /usr/local/bin/uploadserver
```

## Usage

```
uploadserver.py                      # port 8000, saves to ~/Downloads
uploadserver.py 9000                 # custom port
uploadserver.py -d /tmp/uploads      # custom directory
uploadserver.py 9000 -d /tmp/uploads # both
uploadserver.py -h                   # help
```

Listens on `0.0.0.0` so it's reachable from other devices on the network.

The target directory is created if it doesn't exist. It defaults to `~/Downloads`;
override it with `-d`/`--dir` or the `UPLOAD_DIR` environment variable (the `-d`
flag takes precedence):

```
UPLOAD_DIR=/tmp/uploads uploadserver.py
```

If anything here ends up being useful to you and you feel like saying thanks, my PayPal is https://paypal.me/genericJE. Truly no expectation either way, just leaving the option here in case.
