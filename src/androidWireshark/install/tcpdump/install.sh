#!/usr/bin/env bash

adb root
adb remount
adb push tcpdump /data/local/

adb shell chmod 777 /data/local/tcpdump