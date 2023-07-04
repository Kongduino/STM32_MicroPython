#!/bin/sh
EXT=${1: -4:4}
FORMAT="binary"
if [ $EXT = ".hex" ]
then FORMAT="ihex"
fi
OUTPUT0="~/bin/st-flash --format $FORMAT write $1"
echo $OUTPUT0
~/bin/st-flash --format $FORMAT write $1
