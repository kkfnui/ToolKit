import time

__author__ = 'lvfei'

import sys

sys.path.append("../../")

from src.autoLogin import autoLogin
from src.common import utility


# 1. backup
# 2. deploy
# 3. test
# 4. log



class DeployNode:
    def __init__(self, nodeInfo):
        self.__nodeInfo = nodeInfo

    def deploy(self):
        client = autoLogin.login4public(self.__nodeInfo.name, "", "", "")  # todo reactor mail user info

        client.sendline("cd ~/")
        client.expect("[#$]")

        client.sendline("echo \"" + self.__generateDeployShell() + "\" > deploy.sh")
        client.expect("[#$]")

        client.sendline("chmod +x deploy.sh")
        client.expect("[#$]")

        client.sendline("./deploy.sh")
        client.expect("[#$]")
        client.expect("[#$]")
        time.sleep(5)

    def test(self):
        pass

    def name(self):
        return self.__nodeInfo.name

    def ip(self):
        return self.__nodeInfo.stream.ip

    @staticmethod
    def __generateDeployShell():
        shell = ""
        shell += "cd /usr/local/tomcat7/webapps\n"  # todo read config

        shell += "mv recsys-servering.war ~/webappbak/recsys-servering.war."
        shell += utility.generate_session_name()
        shell += "\n"

        shell += "rm -rvf recsys-servering*\n"
        shell += "mv /tmp/recsys-servering.war .\n"  # todo config it
        shell += "mkdir recsys-servering\n"
        shell += "cd recsys-servering\n"
        shell += "cp ../recsys-servering.war .\n"
        shell += "jar -xvf recsys-servering.war\n"
        shell += "rm recsys-servering.war\n"
        shell += "service tomcat restart\n"

        return shell
