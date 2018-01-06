import os
import sys
import subprocess
from subprocess import PIPE
# import ConfigParser
# import json
import time
# import logging

# import TestFile_BackUp


class ProcessSnapShot:

    def __init__(self):
        print "ProcessSnapShot"
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
    TaskList = os.popen('tasklist /v').read().strip().split('\n')
    for i in range(len(TaskList)):
        TaskList[i] = [q for q in TaskList[i].split(' ') if q != ''][:1]
    return TaskList


def ReturnTestFinish(pathReserve=""):
    pathFinishProcess = r"C:\Work\XenTools\Test_Finish_Process\Test_Process_Process.py"
    if pathReserve != "":
        pathReserve = " -fp " + pathReserve
    os.popen("call python {} {}".format(pathFinishProcess, pathReserve))


class MDXlib:
    # Not implemented
    pass


class Timer:

    def __init__(self):
        self.t = [time.clock()]
        self.tpn = ["Test Start"]
        self.count = 1

    def Add_Time_Point(self, TimePointName):
        self.count += 1
        self.t.append(time.clock())
        self.tpn.append(TimePointName)
        print ("Add Time Point: %s" % TimePointName)
        # print self.count

    def OutputTimeLog(self):
        self.path = r"C:\WorkingFolder\testCase\testModel\TimeLog_%s.txt"
        if not os.path.isdir(self.path):
            print "TimeLog.txt path not exist!"
            return
        # print self.path
        with open(self.path, "w") as file:
            data = []
            for i in xrange(self.count):
                fmt = "{tpn:<30}: {t:>6.2f} sec\n"
                data.append(fmt.format(tpn=self.tpn[i], t=self.t[i]))
            file.writelines(data)
