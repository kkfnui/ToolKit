#!/usr/bin/python
# -*- coding:utf-8

import os
import struct
import fcntl
import pexpect
import termios
import sys


def main():
    child = pexpect.spawn("ls")
    t = child.getwinsize()
    # rows, cols = map(int, os.popen('stty size', 'r').read().split())
    # print(rows, cols)
    print(t)

    print(getwinsize())





if __name__ == "__main__":
    main()
