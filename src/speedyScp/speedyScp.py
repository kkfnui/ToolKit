#!/usr/bin/python
# -*- coding:utf-8
from multiprocessing.pool import ThreadPool

import sys
import os
import time
import pexpect
from time import clock
from optparse import OptionParser

root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(root_path)

from src.common import utility
from src.common import serverlist
from src.autoLogin import autoLogin
import uploadConsumer

__author__ = 'lvfei'

SCP_TIMEOUT_INTERVAL = 150


def ensure_remote_usable(remote, session, user, password, host):
    client = autoLogin.login4public(remote.name, user, host, password)
    if utility.is_risk_path(remote.tmpPath):
        utility.pexit("risk path: " + remote.tmpPath + " found when try to remove it.")

    path = os.path.join(remote.tmpPath, session)
    client.sendline("mkdir -p  " + path)
    client.expect("[$#]")
    time.sleep(1)
    client.close()


def is_all_task_finished(tasks):
    for task in tasks:
        if task.isAlive():
            return False

    return True


def merge_file(client, files, file_name, sha1sum):
    command = "cat "
    for f in files:
        command += f
        command += " "

    command += " > "
    command += file_name

    client.sendline(command)
    index = client.expect(["[#$]"])
    if index != 0:
        utility.pexit("operate remote failed!")

    # For unknown reason, it needs print sha1sum twice.
    client.sendline("sha1sum " + file_name + " > sha1sum.txt")
    index = client.expect(["[#$]"])
    if index != 0:
        utility.pexit("operate remote failed!")

    client.sendline("cat sha1sum.txt")
    index = client.expect(["[#$]"])
    if index != 0:
        utility.pexit("operate remote failed!")

    client.sendline("cat sha1sum.txt")
    index = client.expect(["[#$]"])
    if index != 0:
        utility.pexit("operate remote failed!")

    if index != 0:
        utility.pexit("file transfer failed for sha1sum not equal")
    else:
        log = client.before.replace('\r', ' ').replace('\n', ' ').split(' ')
        if len(filter(lambda x: x == sha1sum, log)) == 0:
            utility.pexit("file transfer failed for sha1sum not equal")


def login_server(server):
    child = pexpect.spawn("ssh -l " + server.user + " " + server.host)
    index = child.expect(["password:"])
    if index == 0:
        child.sendline(server.password)
        child.expect("[#$]")
        return child
    else:
        utility.pexit("login " + server.host + " failed!")


def remote_server_dispatch(child, file_name, servers):
    for server in servers:
        server_info = serverlist.get_product_server(server)
        if server_info is None:
            utility.pexit("there isn't server named " + server)

        child.sendline(
            "scp " + file_name + " " + server_info.user + "@" + server_info.host + ":" + server_info.tmpPath + "/" + file_name)
        index = child.expect("assword")
        if index == 0:
            child.sendline(server_info.password)
            index = child.expect("[$#]")
            print(file_name + " has dispatch to " + server_info.host)
            if index != 0:
                utility.pexit("error occur when dispatch file to " + server_info.host)
        else:
            utility.pexit("error occur when dispatch file to " + server_info.host)


def param_check(argv):
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-f", "--file", dest="filename", help="transfer the file to remote server")
    parser.add_option("-c", "--conf", dest="config", help="the server conf file")
    parser.add_option("-l", "--lan-servers", dest="lan_servers",
                      help="use lan servers to speed scp, eg:server1,server2[,server_n]")
    parser.add_option("-d", "--destination-servers", dest="dest_servers",
                      help="destination that file would be upload. eg:server1[,server_n]")

    parser.add_option("-u", "--user", dest="user", help="email user name, eg:lvfei@xunlei.com")
    parser.add_option("-p", "--password", dest="password", help="email password")
    parser.add_option("-H", "--host", dest="pop3", help="pop3 server host name, eg:pop3.xunlei.com")

    (option, args) = parser.parse_args(argv)

    if option.filename is None or option.config is None or option.dest_servers is None \
            or option.user is None or option.password is None or option.pop3 is None:
        parser.error("\nIncorrect number of arguments. \nUse option \'--help\'.")

    filename = option.filename
    if not os.path.exists(filename) or not os.path.isfile(filename):
        utility.pexit("File \"" + filename + "\" is not a file or not exist.")

    config = option.config
    if not os.path.exists(config) or not os.path.isfile(config):
        utility.pexit("File \"" + config + "\" is not a file or not exist.")
    serverlist.load_config(config)

    lan_servers = []
    if option.lan_servers is not None:
        lan_servers = option.lan_servers.split(',')
        for name in lan_servers:
            info = serverlist.get_lan_server(name)
            if info is None:
                utility.pexit("server \"" + name + "\" is not exist")

    product_servers = option.dest_servers.split(',')
    for server_name in product_servers:
        info = serverlist.get_product_server(server_name)
        if info is None:
            utility.pexit("server \"" + server_name + "\" is not exist")

    return filename, lan_servers, product_servers, option.user, option.password, option.pop3


def main():
    file_name, lan_servers, product_servers, user, password, host = param_check(sys.argv)
    session = utility.generate_session_name()
    start = clock()
    essh = serverlist.get_jump_server()
    print("makeup remote server: " + essh.host)
    ensure_remote_usable(essh, session, user, password, host)

    sha1sum = utility.calc_sha1sum(file_name)
    size = os.path.getsize(file_name)

    file_too_small = os.path.getsize(file_name) < 1 * 1024 * 1024

    servers = []
    if len(lan_servers) != 0 and not file_too_small:
        for index, name in enumerate(lan_servers):
            server = serverlist.get_lan_server(name)
            servers.append(server)

    block_size = 4 * 1024 * 1024
    files = utility.split_file(file_name, str(block_size))

    print(files)
    uploadConsumer.upload_file(files, servers, essh, session)

    child = login_server(essh)
    tmp_path = os.path.join(essh.tmpPath, session)
    child.sendline("cd " + tmp_path)
    if len(lan_servers) != 0:
        merge_file(child, files, file_name, sha1sum)

    for f in files:
        os.remove(f)

    print("-----------------File upload success.-----------------------")
    print("Total cost " + str(time.time() - start))
    print(file_name + ": " + sha1sum)
    print("-----------------Begin dispatch file.-----------------------")

    remote_server_dispatch(child, file_name, product_servers)
    child.close()


if __name__ == '__main__':
    main()
