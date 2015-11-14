#!/usr/bin/python
# -*- coding:utf-8
import sys
import os
from collections import namedtuple
import json
import httplib

sys.path.append("../../")

from src.common import utility

__author__ = 'lvfei'


def get_server_version_info(server):
    conn = httplib.HTTPConnection(host=server.host, port=server.port)
    conn.request("GET", server.versionPath)
    resp = conn.getresponse()
    if resp.status is not 200:
        utility.pexit(server.host + " failed, status: " + str(resp.status))

    data = resp.read()
    conn.close()
    return data


def get_config(path):
    v = json.load(file(path), object_hook=lambda d: namedtuple('server', d.keys())(*d.values()))

    apps = dict()
    for item in v:
        apps[item.name] = item
    return apps


if __name__ == '__main__':
    v = get_config("/Users/lvfei/Code/ToolKit/conf/apps.local.json")
    app = "recsys-servering"
    app = v.get(app)

    version = None
    for server in app.servers:
        tmp = get_server_version_info(server)
        if version is None:
            version = tmp
        else:
            if tmp != version:
                utility.pexit(server.name + " resp value is not equal prev's")

    print(version)
