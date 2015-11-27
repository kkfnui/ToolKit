# ToolKit

It contains tools that help manager server more convenient。

## Installation

The tool dependence `pexpect`. Pexpect is on PyPI, and can be installed with standard tools:


```
pip install pexpect
```

Or

```
easy_install pexpect
```

## Requirements

The tool only test on `python 2.7`. Until someone use it on python 3.x, I won't test it.

## Tools

### speedyScp

`speedyScp` can speed up `scp` command at some special network.

In China, upload bandwidth is rare. So the upload speed will be low. For me the speed is 200KB/s.

I usually need to upload large file(`50MB`) to server. And it will cost me 4~5 minutes. Life is short, I need upload faster!


**Usage**

1. Edit `servers.json`. Set the right info of `host`, `user`, `password`.

    There are three type server.

    1. jump server
    2. lan server
    3. product server

2. Execute the script

```
Usage: speedyScp.py [options] arg

Options:
  -h, --help            show this help message and exit
  -f FILENAME, --file=FILENAME
                        transfer the file to remote server
  -c CONFIG, --config=CONFIG
                        the server config file
  -l LAN_SERVERS, --lan-servers=LAN_SERVERS
                        use lan servers to speed scp,
                        eg:server1,server2[,server_n]
  -d DEST_SERVERS, --destination-servers=DEST_SERVERS
                        destination that file would be upload.
                        eg:server1[,server_n]

```


**TODO**

2. file could be full path
3. refactor dependence of login,scp,deploy
5. split file smaller that can make upload as quick as possible
3. show upload progress and transfer speed
4. support input passcode artificial when get passcode from mail failed.
6. add logger to record every action to find errors 
7. manager interface https://github.com/emptyhua/sshgo/blob/master/sshgo.py
8. exception 

    The passcode has sent to your mail. If not, After 20 seconds try again.
    Input again:
    
9. support multi files transfer
10. support destination path
11. file name support regular
12. let config file in ~/.toolkit/

    - servers.json

**Done**

1. could execute on any work directory


**Feature**

- allow use normal `scp` , and also could dispatch file to product server

### autoLogin

`autoLogin` is aimed at remove passcode.
 
**Usage**
 
 1. Set office mail account info
 2. Execute the script
 
```
Usage: autoLogin.py [options] arg

Options:
  -h, --help            show this help message and exit
  -c CONFIG, --config=CONFIG
                        the server config file
  -s NAME, --server-name=NAME
                        the server name set in config file. eg: tw06177
```

