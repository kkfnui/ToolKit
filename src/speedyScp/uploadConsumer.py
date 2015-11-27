import sys

import Queue
import os
import threading
import time
import pexpect

root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(root_path)

from src.common import utility

__author__ = 'lvfei'

SCP_TIMEOUT_INTERVAL = 150


class LanUploadConsumer(threading.Thread):
    def __init__(self, queue, server, session):
        threading.Thread.__init__(self)
        self._queue = queue
        self._server = server
        self._session = session

    def run(self):
        while True:
            if self._queue.empty():
                break

            task = self._queue.get()
            self.__scp(task.file, task.dest)

    def __scp(self, file_name, dest):
        print("remote scp file: " + file_name)

        self.__prepare_remote_path()
        full_path = self.__scp2lan(file_name)
        self.__remote_scp(full_path, file_name, dest)

    def __prepare_remote_path(self):
        pass

    def __scp2lan(self, file_name):
        full_path = os.path.join(self._server.tmpPath, self._session, file_name)
        print(full_path)

        client = pexpect.spawn("scp " + file_name + " " + self._server.user + "@" + self._server.host + ":" + full_path)
        index = client.expect(["password:"])
        if index == 0:
            client.sendline(self._server.password)
            index = client.expect(pexpect.EOF)
            if index == 0:
                client.close()
            else:
                utility.pexit("file transfer to " + self._server.host + " failed.")

        return full_path

    def __remote_scp(self, full_path, file_name, dest):
        print("Copy " + file_name + " from local to " + dest.host + " complete")
        client = pexpect.spawn("ssh -l " + self._server.user + " " + self._server.host)
        index = client.expect(["password:"])
        if index == 0:
            client.sendline(self._server.password)
            command = "scp " + full_path + " " + dest.user + "@" + dest.host + ":" + dest.path
            client.sendline(command)
            index = -1
            while index != 0:
                index = client.expect(["password", "yes"])
                if index == 0:
                    client.sendline(dest.password)
                    index = client.expect("[#$]", timeout=SCP_TIMEOUT_INTERVAL)
                    print(file_name + " has transfer to " + dest.host)

                    if index != 0:
                        utility.pexit("file remote transfer to " + dest.host + " failed.")

                    client.close()
                elif index == 1:
                    client.sendline("yes")


class LocalUploadConsumer(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self._queue = queue

    def run(self):
        while True:
            if self._queue.empty():
                break

            task = self._queue.get()
            self.__scp(task.file, task.dest)

    @staticmethod
    def __scp(file_name, dest):
        print("local scp file: " + file_name)
        child = pexpect.spawn("scp " + file_name + " " + dest.user + "@" + dest.host + ":" + dest.path)
        index = child.expect(["password:"])
        if index == 0:
            child.sendline(dest.password)
            index = child.expect(pexpect.EOF, timeout=SCP_TIMEOUT_INTERVAL)
            if index == 0:
                child.close()
                print("local transfer complete")
            else:
                utility.pexit("file transfer to " + dest.host + " failed.")


class Task:
    pass


def upload_file(sub_files, lan_servers, dest, session):
    queue = Queue.Queue()

    for f in sub_files:
        task = Task()
        task.file = f
        full_path = os.path.join(dest.tmpPath, session, f)
        task.dest = Task()
        task.dest.path = full_path
        task.dest.host = dest.host
        task.dest.user = dest.user
        task.dest.password = dest.password
        queue.put(task)

    consumers = []
    consumer = LocalUploadConsumer(queue)
    consumers.append(consumer)

    for server in lan_servers:
        consumer = LanUploadConsumer(queue, server, session)
        consumers.append(consumer)

    for consumer in consumers:
        consumer.start()

    start_time = time.time()
    while time.time() - start_time < 2000:
        print("remain files count: ", queue.qsize())
        time.sleep(1)
        if queue.empty():
            for consumer in consumers:
                consumer.join()
            print("sub files all uploaded , cost: " + str(time.time() - start_time))
            break
