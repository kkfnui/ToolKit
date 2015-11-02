import os
import struct
import time
import hashlib
import getpass
import sys
import traceback
import termios
import fcntl

__author__ = 'lvfei'


def is_risk_path(file_path):
    parts = file_path.split(' ')
    if len(filter(lambda x: x == "/", parts)) != 0:
        return True

    return False


def generate_session_name():
    user_name = getpass.getuser()
    tick = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))
    return user_name + "_" + str(tick)


def split_file(name, size):
    prefix = name + "."
    command = "split -b " + size + " " + name + " " + prefix
    os.system(command)
    files = os.listdir(os.getcwd())
    return filter(lambda x: x.startswith(prefix, 0, len(prefix)), files)


def is_risk_path(file_path):
    parts = file_path.split(' ')
    if len(filter(lambda x: x == "/", parts)) != 0:
        return True

    return False


def calc_sha1sum(file_name):
    with open(file_name, 'rb') as f:
        sha1obj = hashlib.sha1()
        sha1obj.update(f.read())
        sha1sum = sha1obj.hexdigest()
        return sha1sum


def getwinsize():
    if 'TIOCGWINSZ' in dir(termios):
        TIOCGWINSZ = termios.TIOCGWINSZ
    else:
        TIOCGWINSZ = 1074295912L  # Assume
    s = struct.pack('HHHH', 0, 0, 0, 0)
    x = fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ, s)
    return struct.unpack('HHHH', x)[0:2]


def pexit(msg):
    sys.stderr.write(msg + "\n")
    traceback.print_exc()
    sys.exit(-1)


if __name__ == '__main__':
    print(generate_session_name())
