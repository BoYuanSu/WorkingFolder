import os
import sys
import subprocess
import logging
from subprocess import PIPE
# import ConfigParser
# import json
import time

import TestFile_BackUp as backuptool


class ProcessSnapShot:

    def __init__(self):
        logger.info("ProcessSnapShot")
        self.proBefore = checkTasks()

    def killRedundant(self):
        print "killRedundant"
        self.proAfter = checkTasks()
        for i in range(len(self.proAfter)):
            if not (self.proAfter[i] in self.proBefore):
                os.system(
                    "taskkill /t /f /im {}".format(str(self.proAfter[i][0])))
                print "Python killed {}".format(self.proAfter[i])


def checkTasks():
    TaskList = os.popen('tasklist').read().strip().split('\n')
    for i in range(len(TaskList)):
        TaskList[i] = [q for q in TaskList[i].split(' ') if q != ''][:1]
    return TaskList


def ReturnTestFinish(pathReserve=""):
    pathFinishProcess = r"C:\Work\XenTools\Test_Finish_Process\Test_Process_Process.py"
    if pathReserve != "":
        pathReserve = " -fp " + pathReserve
    os.popen("call python {} {}".format(pathFinishProcess, pathReserve))


def detectCrash():
    r = os.popen('tasklist /v').read()
    if "WerFault.exe" in r:
        return True
    return False


class MDXlib:
    # Not implemented
    pass


class Timer:

    def __init__(self):
        self.t = [time.clock()]
        self.tpn = ["Test Start"]
        self.count = 1

    def addTimeStamp(self, TimePointName):
        self.count += 1
        self.t.append(time.clock())
        self.tpn.append(TimePointName)
        print ("Add Time Point: {}".format(TimePointName))

    def OutputTimeLog(self):
        self.path = r"C:\WorkingFolder\testCase\testModel\TimeLog.log"
        if not os.path.isfile(self.path):
            print "TimeLog.txt path not exist!"
            return
        # print self.path
        with open(self.path, "a") as file:
            data = []
            for i in xrange(self.count):
                fmt = "{tpn:<30}: {t:>6.2f} sec\n"
                data.append(fmt.format(tpn=self.tpn[i], t=self.t[i]))
            data.append("{0} End log {0}".format("=") * 50)
            file.writelines(data)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s: %(name)s: %(message)s")
formatter2 = logging.Formatter("%(message)s")

file_handler = logging.FileHandler(r".\testModel\TimeLog.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter2)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)