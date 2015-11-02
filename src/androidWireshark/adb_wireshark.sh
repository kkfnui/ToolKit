#!/usr/bin/env bash

adb root	#获取root权限
adb shell < adb_tcpdump.sh & #在手机上执行
Apid=$!

sleep 1
adb forward tcp:11233 tcp:11233	#将手机11233端口的数据转发到mac的11233端口上
sleep 1

mkfifo /tmp/sharkfin	#创建一个命名管道
wireshark -k -i /tmp/sharkfin & #运行本地的wireshark，并指定数据来源是在/tmp/sharkfin上

nc 127.0.0.1 11233 > /tmp/sharkfin #将本地11233端口的数据重定向到命名管道上
kill -9 $Apid