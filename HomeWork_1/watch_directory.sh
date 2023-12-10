#!/bin/bash

watch_directory="$home/watch"


inotifywait -m -e create --format '%w%f' "$watch_directory" | while read new_file; do
    echo "New file detected: $new_file"
    file_content=$(cat "$new_file")
    echo "File content: "
    echo "$file_content"
    mv "$new_file" "$new_file.back"
    echo "File renamed to $new_file.back"
done


