#!/usr/bin/env bash


/data/local/tcpdump -s 0 -w - | busybox nc -l -p 11233
