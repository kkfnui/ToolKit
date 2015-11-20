import sys
from collections import namedtuple
import json

sys.path.append("../../")

from nginxSwitcher import NginxSwitcher
from deployNode import DeployNode


# 1. download lastest product package(restful api), ensure file right
# 2. scp file to dest sever
# 3. hot replace server

class Deploy:
    __nodes = []
    __switcher = None
    __deploy_nodes = []

    def __init__(self, conf, app_name):
        v = json.load(file(conf), object_hook=lambda d: namedtuple('server', d.keys())(*d.values()))
        for item in v:
            if item.name == "recsys-servering":
                servers = item.servers
                self.__deploy_nodes = item.deploy
                streams = []
                for server in servers:
                    node = DeployNode(server)
                    self.__nodes.append(node)
                    streams.append(server.stream)

                self.__switcher = NginxSwitcher(item.switcher, streams)

    def deploy(self):
        for node in self.__nodes:
            if node.name() in self.__deploy_nodes:
                print("----deploy-----" + node.name())
                self.__switcher.disable(node.ip())
                node.deploy()
                self.__switcher.reset()


if __name__ == '__main__':
    deploy = Deploy("/Users/lvfei/Code/ToolKit/conf/apps.local.json", "recsys-servering")
    deploy.deploy()
