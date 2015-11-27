#!/usr/bin/python
import sys
import os
import time
import pexpect
from optparse import OptionParser

root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(root_path)

from src.common import utility
from src.common import serverlist
import passcode

__author__ = 'lvfei'

sub_term = None

serverlist.load_config("/Users/lvfei/Code/ToolKit/conf/servers.local.json")


class EmailInfo:
    pass


email = EmailInfo()


def login_server(server):
    child = pexpect.spawn("ssh -l " + server.user + " " + server.host)
    # child.logfile = sys.stdout
    index = child.expect(["password:"])
    if index == 0:
        child.sendline(server.password)
        child.expect("[#$]")
        child.sendline()
        return child
    else:
        utility.pexit("login " + server.host + " failed!")


def jump_login(child, server):
    print("begin login " + server.name)
    child.sendline("ssh -l " + server.user + " " + server.host)
    while True:
        index = child.expect(["assword", "yes/no"])
        if index == 1:
            child.sendline("yes")
            continue
        elif index == 0:
            child.sendline(server.password)
            index = child.expect("[#$]")
            if index == 0:
                print("login success!")
                child.sendline("")
                return child

        utility.pexit("login " + server.host + " failed!")


def auto_login_essh(essh):
    print("begin login essh")
    child = pexpect.spawn("ssh -l " + essh.user + " " + essh.host)
    # child.logfile = sys.stdout
    index = child.expect(["password:"])
    if index == 0:
        child.sendline(essh.password)
        index = child.expect(["passcode", "[#$]"])
        if index == 0:
            print("waiting passcode...")
            time.sleep(5)
            global email
            code = passcode.get_passcode_from_email(email.host, email.user, email.password)
            print("passcode is " + code)
            child.sendline(code)
            index = child.expect("[#$]")
            if index == 0:
                print("login essh success")
                return child
            else:
                utility.pexit("login " + essh.host + " failed!")
        elif index == 1:
            return child
        else:
            utility.pexit("login " + essh.host + " failed!")
    else:
        utility.pexit("login " + essh.host + " failed!")


def login_essh(essh):
    child = pexpect.spawn("ssh -l " + essh.user + " " + essh.host)
    index = child.expect(["password:"])
    if index == 0:
        child.sendline(essh.password)
        index = child.expect(["passcode", "[#$]"])
        if index == 0:
            print("please enter passcode:")
            return child
        elif index == 1:
            child.sendline("")
            return child
        else:
            utility.pexit("login essh failed!")


def login(name):
    if name == "essh":
        jump = serverlist.get_jump_server()
        child = auto_login_essh(jump)
        return child
    else:
        server = serverlist.get_lan_server(name)
        if server is not None:
            child = login_server(server)
            return child

        server = serverlist.get_product_server(name)
        if server is not None:
            jump = serverlist.get_jump_server()
            child = auto_login_essh(jump)
            child = jump_login(child, server)
            return child

        utility.pexit("server \"" + name + "\" not exists.")


def sigwinch_passthrough(sig, data):
    winsize = utility.getwinsize()
    print(winsize)
    global sub_term
    sub_term.setwinsize(winsize[0], winsize[1])


def param_check():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-c", "--conf", dest="config", help="the server conf file")
    parser.add_option("-s", "--server-name", dest="name",
                      help="the server name set in conf file. eg: tw06177")
    parser.add_option("-u", "--user", dest="user", help="email user name, eg:lvfei@xunlei.com")
    parser.add_option("-p", "--password", dest="password", help="email password")
    parser.add_option("-H", "--host", dest="pop3", help="pop3 server host name, eg:pop3.xunlei.com")

    (option, args) = parser.parse_args()
    if option.config is None or option.name is None:
        parser.error("\nIncorrect number of arguments. \nUse option \'--help\'.")

    config = option.config
    if not os.path.exists(config) or not os.path.isfile(config):
        utility.pexit("File \"" + config + "\" is not a file or not exist.")
    serverlist.load_config(config)

    return option


def login4public(name, user, host, password):
    global email

    email.user = user
    email.host = host
    email.password = password

    client = login(name)
    winsize = utility.getwinsize()
    client.setwinsize(winsize[0], winsize[1])
    return client


def main():
    option = param_check()
    global email
    email.user = option.user
    email.password = option.password
    email.host = option.pop3

    global sub_term
    sub_term = login(option.name)
    winsize = utility.getwinsize()
    sub_term.setwinsize(winsize[0], winsize[1])
    sub_term.interact()


if __name__ == '__main__':
    main()
