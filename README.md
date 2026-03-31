# uploadserver

Minimal upload-only HTTP server. No dependencies beyond Python 3 stdlib.

Files are saved to `~/Downloads` with automatic rename on conflict.

## Features

- Drag & drop + file picker
- Upload progress bar
- Toast notifications for success/failure
- Dark mode support
- No directory listing, no downloads — upload only

## Usage

```
uploadserver          # port 8000
uploadserver 9000     # custom port
```

Listens on `0.0.0.0` so it's reachable from other devices on the network.
