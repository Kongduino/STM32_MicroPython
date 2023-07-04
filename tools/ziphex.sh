#!/bin/sh
cd ../builds/ ; find . -name "*.hex" -execdir zip '{}.zip' '{}' \;

