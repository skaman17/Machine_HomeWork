#!/bin/bash

watch_directory="/./home/WATCH"


/usr/bin/inotifywait -m -r -e create,move,delete /home/kostia | /home/HomeWork/HomeWork_1/watch_script.sh >> /home/HomeWork/HomeWork_1/watch.log  2>&1  "$WATCH_DIR" | while read FILE; do

    echo "New file detected: $FILE"
    cat "$FILE"
    mv "$FILE" "${FILE}.back"
    echo "File moved to ${FILE}.back"

done

