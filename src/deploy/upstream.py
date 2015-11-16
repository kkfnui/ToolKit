from collections import namedtuple
import json

__author__ = 'lvfei'


# upstream xmtj {
# 	server 10.33.1.180:8080 max_fails=3 fail_timeout=1s weight=10;
# 	#server 10.33.1.181:8080 max_fails=3 fail_timeout=1s weight=1;
# 	#server 10.33.1.182:8080 max_fails=3 fail_timeout=1s weight=1;
# 	server 10.33.1.183:8080 max_fails=3 fail_timeout=1s weight=3;
# 	server 10.33.1.184:8080 max_fails=3 fail_timeout=1s weight=3;
# 	#server 10.33.1.185:8080 max_fails=3 fail_timeout=1s weight=3;
# 	server 10.33.1.186:8080 max_fails=3 fail_timeout=1s weight=3;
# 	#server 10.33.1.187:8080 max_fails=3 fail_timeout=1s weight=5;
# 	#server 10.33.1.188:8080 max_fails=3 fail_timeout=1s backup;
# 	#server 10.33.1.189:8080 max_fails=3 fail_timeout=1s backup;
# }


class Node:
    def __init__(self, ip, port, fails, timeout, weight):
        self.ip = ip
        self.port = port
        self.fails = fails
        self.timeout = timeout
        self.weight = weight

    def dump(self):
        conf = "server "
        conf += self.ip
        conf += ":"
        conf += self.port
        conf += " "
        conf += "max_fails="
        conf += self.fails
        conf += " "
        conf += "fail_timeout="
        conf += self.timeout
        conf += " "
        conf += "weight="
        conf += self.weight
        return conf


class UpStream:
    __state = []
    __nodes = []

    def __init__(self, conf):
        v = json.load(file(conf), object_hook=lambda d: namedtuple('server', d.keys())(*d.values()))
        for item in v:
            node = Node(item.ip, item.port, item.fails, item.timeout, item.weight)
            self.__state.append(True)
            self.__nodes.append(node)

    def enable(self, ip):
        for index, value in enumerate(self.__nodes):
            if value.ip == ip:
                self.__state[index] = True
                break

    def disable(self, ip):
        for index, value in enumerate(self.__nodes):
            if value.ip == ip:
                self.__state[index] = False
                break

    def reset(self):
        for index, value in enumerate(self.__state):
            self.__state[index] = True

    def dump(self):
        conf = "upstream xmtj {\n"
        for index, value in enumerate(self.__nodes):
            conf += "\t"
            if self.__state[index] is False:
                conf += "#"

            conf += value.dump()
            conf += "\n"
        conf += "}\n"
        return conf


def main():
    up = UpStream("/Users/lvfei/Code/ToolKit/conf/upstream.local.json")
    up.disable("10.33.1.180")
    up.reset()
    up.disable("10.33.1.183")
    print(up.dump())


if __name__ == '__main__':
    main()
