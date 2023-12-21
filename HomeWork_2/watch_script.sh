#!/bin/bash

WATCH_DIR=~/watch

inotifywait -m -e create --format '%f' "$WATCH_DIR" |
while read -r filename; do
    filepath="$WATCH_DIR/$filename"
    content=$(cat "$filepath")
    echo "File Content:"
    echo "$content"
    echo "Renaming $filename to $filename.back"
    mv "$filepath" "$WATCH_DIR/$filename.back"
done
