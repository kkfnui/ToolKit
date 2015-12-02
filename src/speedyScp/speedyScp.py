#!/usr/bin/python
# -*- coding:utf-8

import sys
import os
import threading
import time
from optparse import OptionParser

import pexpect

root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(root_path)

from src.common import utility
from src.common import serverlist
from src.autoLogin import autoLogin

__author__ = 'lvfei'

SCP_TIMEOUT_INTERVAL = 150


def rscp(child, file_name, remote, session):
    path = os.path.join(remote.tmpPath, session)
    path = os.path.join(path, file_name)
    command = "scp " + file_name + " " + remote.user + "@" + remote.host + ":" + path
    child.sendline(command)
    index = -1
    while index != 0:
        index = child.expect(["password", "yes"])
        if index == 0:
            child.sendline(remote.password)
            index = child.expect("[#$]", timeout=SCP_TIMEOUT_INTERVAL)
            print(file_name + " has transfer to " + remote.host)

            if index != 0:
                utility.pexit("file remote transfer to " + remote.host + " failed.")
        elif index == 1:
            child.sendline("yes")


def ensure_remote_usable(remote, session, user, password, host):
    client = autoLogin.login4public(remote.name, user, host, password)
    if utility.is_risk_path(remote.tmpPath):
        utility.pexit("risk path: " + remote.tmpPath + " found when try to remove it.")

    path = os.path.join(remote.tmpPath, session)
    client.sendline("mkdir -p  " + path)
    client.expect("[$#]")
    time.sleep(1)
    client.close()


def remote_upload(file_name, remote, dest, session):
    ensure_remote_usable(remote, session)
    tmp_path = os.path.join(remote.tmpPath, session)
    file_full_path = os.path.join(tmp_path, file_name)
    print(file_full_path)
    client = pexpect.spawn(
        "scp " + file_name + " " + remote.user + "@" + remote.host + ":" + file_full_path)
    index = client.expect(["password:"])
    if index == 0:
        client.sendline(remote.password)
        index = client.expect(pexpect.EOF)
        if index == 0:
            client.close()
        else:
            utility.pexit("file transfer to " + remote.host + " failed.")

    print("Copy " + file_name + " from local to " + remote.host + " complete")
    client = pexpect.spawn("ssh -l " + remote.user + " " + remote.host)
    index = client.expect(["password:"])
    if index == 0:
        client.sendline(remote.password)
        client.sendline("cd " + tmp_path)
        rscp(client, file_name, dest, session)


def local_upload(file_name, dest, session):
    print("local computer begin transfer " + file_name)
    path = os.path.join(dest.tmpPath, session)
    path = os.path.join(path, file_name)
    child = pexpect.spawn("scp " + file_name + " " + dest.user + "@" + dest.host + ":" + path)
    child.logfile = sys.stdout
    index = child.expect(["password:"])
    if index == 0:
        child.sendline(dest.password)
        index = child.expect(pexpect.EOF, timeout=SCP_TIMEOUT_INTERVAL)
        if index == 0:
            child.close()
            print("local transfer complete")
        else:
            utility.pexit("file transfer to " + dest.host + " failed.")


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
    start = time.time()
    essh = serverlist.get_jump_server()
    print("makeup remote server: " + essh.host)
    ensure_remote_usable(essh, session, user, password, host)

    sha1sum = utility.calc_sha1sum(file_name)
    size = os.path.getsize(file_name)

    tasks = []
    files = []
    if len(lan_servers) != 0:
        print(lan_servers, len(lan_servers))
        client_count = len(lan_servers) + 1
        block_size = size / client_count + client_count
        files = utility.split_file(file_name, str(block_size))

        for index, name in enumerate(lan_servers):
            transfer_file = files[index]
            server_info = serverlist.get_lan_server(name)
            task = threading.Thread(target=remote_upload, args=(transfer_file, server_info, essh, session))
            tasks.append(task)

        task = threading.Thread(target=local_upload, args=(files[len(lan_servers)], essh, session))
        tasks.append(task)
    else:
        task = threading.Thread(target=local_upload, args=(file_name, essh, session))
        tasks.append(task)

    for t in tasks:
        t.setDaemon(True)
        t.start()

    while True:
        time.sleep(1)
        if is_all_task_finished(tasks):
            break

    finish = time.time()

    child = login_server(essh)
    tmp_path = os.path.join(essh.tmpPath, session)
    child.sendline("cd " + tmp_path)
    if len(lan_servers) != 0:
        merge_file(child, files, file_name, sha1sum)

    for f in files:
        os.remove(f)

    print("-----------------File upload success.-----------------------")
    print("Total cost " + str(finish - start))
    print(file_name + ": " + sha1sum)
    print("-----------------Begin dispatch file.-----------------------")

    remote_server_dispatch(child, file_name, product_servers)
    child.close()


if __name__ == '__main__':
    main()
