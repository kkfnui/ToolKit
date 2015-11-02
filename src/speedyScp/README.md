# speedyScp

`speedyScp` can speed up `scp` command at some special network.

In China, upload bandwidth is rare. So the upload speed will be low. For me the speed is 200KB/s.

I usually need to upload large file(`50MB`) to server. And it will cost me 4~5 minutes. Life is short, I need upload faster!


## Usage

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


## TODO

1. param should be set by option

    http://www.cnblogs.com/captain_jack/archive/2011/01/11/1933366.html
   
2. show upload progress and transfer speed 