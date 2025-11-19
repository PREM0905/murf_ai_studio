#!/usr/bin/env python3
"""Download and extract a Vosk model into integrations/models/.

Usage:
  python download_vosk_model.py --model small --dest ../models

By default downloads the small English model `vosk-model-small-en-us-0.15`.
"""
import os
import sys
import argparse
import requests
import zipfile
from pathlib import Path

DEFAULT_MODEL_NAME = "vosk-model-small-en-us-0.15"
DEFAULT_URL = f"https://alphacephei.com/vosk/models/{DEFAULT_MODEL_NAME}.zip"


def download(url, dest_path):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} -> {dest_path}")
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    with open(dest_path, "wb") as f:
        downloaded = 0
        for chunk in resp.iter_content(chunk_size=8192):
            if not chunk:
                continue
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = downloaded / total * 100
                print(f"  {downloaded}/{total} bytes ({pct:.1f}%)", end="\r")
    print("\nDownload complete")


def extract(zip_path, dest_dir):
    print(f"Extracting {zip_path} -> {dest_dir}")
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(dest_dir)
    print("Extraction complete")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", help="Download URL", default=DEFAULT_URL)
    p.add_argument("--model-name", help="Model directory name after extraction", default=DEFAULT_MODEL_NAME)
    p.add_argument("--dest", help="Destination parent folder for models", default=str(Path(__file__).resolve().parents[1] / "models"))
    args = p.parse_args()

    dest_dir = Path(args.dest).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)

    zip_filename = dest_dir / (args.model_name + ".zip")

    try:
        download(args.url, zip_filename)
    except Exception as e:
        print(f"Download failed: {e}")
        if zip_filename.exists():
            print("Using existing zip file")
        else:
            sys.exit(1)

    try:
        extract(zip_filename, dest_dir)
    except Exception as e:
        print(f"Extraction failed: {e}")
        sys.exit(1)

    print("Model is available at:")
    print(dest_dir / args.model_name)
    print("You can set VOSK_MODEL_PATH in your .env to this path and restart the server.")


if __name__ == '__main__':
    main()
