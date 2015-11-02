#!/usr/bin/python
from collections import namedtuple
import json

__author__ = 'lvfei'

JUMP = None
LAN_SERVERS = None
PRODUCT_SERVERS = None


def load_config(path):
    v = json.load(file(path), object_hook=lambda d: namedtuple('server', d.keys())(*d.values()))
    if v.jump is None or v.lanServer is None or v.productServer is None:
        return False;
    else:
        global JUMP
        JUMP = v.jump

        global LAN_SERVERS
        LAN_SERVERS = dict()
        for server in v.lanServer:
            LAN_SERVERS[server.name] = server

        global PRODUCT_SERVERS
        PRODUCT_SERVERS = dict()
        for server in v.productServer:
            PRODUCT_SERVERS[server.name] = server


def get_jump_server():
    return JUMP


def get_lan_server(name):
    return LAN_SERVERS.get(name)


def get_product_server(name):
    return PRODUCT_SERVERS.get(name)


if __name__ == '__main__':
    load_config("local.json")
    print(get_jump_server())

    print(get_lan_server("test41"))
    print(get_lan_server("test"))
