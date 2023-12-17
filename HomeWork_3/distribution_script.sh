#!/bin/bash

#Check the distribution
distribution=$(lsb_release -si)

# Check if the disctribution is Ubuntu
if [ "$distribution" != "Ubuntu" ]; then
    echo "Error: This script is intendent for Ubuntu only!"
    exit 1
fi

# Output CPU usage for the last hour to a file
date >> cpu-usage.log
sar -u 60 60 >> cpu-usage.log

echo "CPU usage logged to cpu-usage.log"

