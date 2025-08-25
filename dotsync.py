#!/usr/bin/env python3
import os
import shutil
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Path to your git repo
GIT_REPO = str(Path.home() / "Repos" / "dotfiles")

# List of files/directories to track
FILES_TO_TRACK = [
    "/etc/nixos/configuration.nix",
    "/usr/share/sddm/themes/",
    str(Path.home() / ".config"), 
]

class FileSyncHandler(FileSystemEventHandler):
    def __init__(self, file_map, dir_map):
        self.file_map = file_map
        self.dir_map = dir_map

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path in self.file_map:
            self.sync_file(event.src_path)
        else:
            # Check if it belongs in a tracked directory
            for src_dir, dest_dir in self.dir_map.items():
                if event.src_path.startswith(src_dir):
                    self.sync_file(event.src_path, base_dir=src_dir, dest_dir=dest_dir)
                    break

    def on_created(self, event):
        self.on_modified(event)

    def sync_file(self, src_path, base_dir=None, dest_dir=None):
        if base_dir and dest_dir:
            rel = Path(src_path).relative_to(base_dir)
            dest_path = Path(dest_dir) / rel
        else:
            dest_path = self.file_map[src_path]

        os.makedirs(dest_path.parent, exist_ok=True)

        try:
            shutil.copy2(src_path, dest_path)
            print(f"[UPDATED] {src_path} -> {dest_path}")
        except PermissionError:
            print(f"[ERROR] Permission denied: {src_path}")
        except Exception as e:
            print(f"[ERROR] Could not sync {src_path}: {e}")

def main():
    file_map = {}  # individual files
    dir_map = {}   # tracked directories

    for f in FILES_TO_TRACK:
        src = Path(f).expanduser().resolve()
        rel_path = src.relative_to(src.anchor)
        dest = Path(GIT_REPO) / rel_path

        if src.is_dir():
            dir_map[str(src)] = str(dest)
            # initial copy of whole directory
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            print(f"[INIT] Copied directory {src} -> {dest}")
        else:
            file_map[str(src)] = str(dest)
            os.makedirs(dest.parent, exist_ok=True)
            try:
                shutil.copy2(src, dest)
                print(f"[INIT] Copied file {src} -> {dest}")
            except Exception as e:
                print(f"[ERROR] Could not copy {src}: {e}")

    observer = Observer()
    handler = FileSyncHandler(file_map, dir_map)

    # Watch parent dirs of all tracked files
    for f in file_map.keys():
        observer.schedule(handler, str(Path(f).parent), recursive=False)

    # Watch tracked directories recursively
    for d in dir_map.keys():
        observer.schedule(handler, d, recursive=True)

    observer.start()
    print("[INFO] Watching for changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
