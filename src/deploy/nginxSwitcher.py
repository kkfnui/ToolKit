import sys
import time

sys.path.append("../../")

from src.autoLogin import autoLogin
from upstream import UpStream

__author__ = 'lvfei'


class NginxSwitcher:
    __client = None
    __upstream = None
    __info = None

    def __init__(self, info, streams):
        self.__info = info
        self.__upstream = UpStream(streams)
        self.__client = autoLogin.login4public(info.name, "", "", "")

    def disable(self, ip):
        self.__upstream.disable(ip)
        self.__execute(self.__upstream.dump())

    def reset(self):
        self.__upstream.reset()
        self.__execute(self.__upstream.dump())

    def __execute(self, conf):
        self.__client.sendline("echo \"" + conf + "\" > " + self.__info.nginx_conf)
        self.__client.expect("[#$]")
        self.__client.sendline(self.__info.nginx_bin + "-s reload")
        self.__client.expect("[#$]")
        time.sleep(1)
