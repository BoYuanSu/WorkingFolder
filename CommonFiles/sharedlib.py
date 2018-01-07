import inspect
import logging
import os
import Queue
import subprocess
import sys
import threading

# import ConfigParser
# import json
import time
from subprocess import PIPE

import TestFile_BackUp as backuptool

sys.dont_write_bytecode = True


class PyTestLauncher():

    def __init__(self, sharedmd, sharedClass, insStages):

        argsinit = getattr(insStages, "argsInit", ())
        kwargsinit = getattr(insStages, "kwargsInit", {})
        self.insSharedclass = sharedClass(*argsinit, **kwargsinit)
        self.insstages = insStages
        self.q = sharedmd.q
        self._stop_event = threading.Event()
        self.CONSTATTR = self.constattr
        # for k in self.CONSTATTR.iterkeys():
        #     if id(self.CONSTATTR[k]) == id(self.insstages.__dict__[k]):
        #         print "WARNING"

    def Run(self):
        self._reset_attr()
        fn = getattr(self.insSharedclass, self.insstages.fn)
        if not fn:
            raise Exception("Function of Shared Class not Found!")
        # print function
        self.thd = TempThread()
        self.thd.setfn(fn)
        self.thd.start()
        # self.thd.join(0)

    def wait(self):
        while self.thd.isAlive():
            pass
        try:
            self.q.get(block=False)
        except Queue.Empty:
            pass

    def _get_shared_mthd(self):
        if not getattr(self.insstages, "fn"):
            raise Exception("Function for Test Stage not Found!")
        return getattr(self.insSharedclass, self.insstages.fn)

    def _reset_attr(self):
        for key in self.CONSTATTR.iterkeys():
            self.insstages.__dict__[key] = self.CONSTATTR[key]

    @property
    def constattr(self):
        keys = self.insstages.__dict__.keys()
        excludedKeys = ["t1", "t2", "t3", "sharedClassName", "fn", "mt"]
        CONSTATTR = {}
        for excludekey in excludedKeys:
            keys.pop(keys.index(excludekey))
        # print keys
        for key in keys:
            CONSTATTR[key] = self.insstages.__dict__[key]
        return CONSTATTR

    @property
    def _stagesMethod(self):
        methods = []
        methodsTup = inspect.getmembers(self.insstages, inspect.ismethod)
        for mthdtup in methodsTup:
            if mthdtup[0].startswith("Stage_"):
                methods.append(mthdtup[1])
        if len(methods) == 0:
            raise Exception("Stages from TestScript not Found!")
        return methods


class TempThread(threading.Thread):

    def __int__(self):

        super(TempThread, self).__init__()
        # self._stop_event = threading.Event()
        # threading.Thread.__init__(self)
        # self.f = fn
        self.min = 1
        self.max = 2
        self.fn = None
        # threading.Thread.__init__(self)

    def run(self):
        print self.min, self.max
        self.min = ()
        self.max = {}
        self.fn(*self.min, **self.max)
        pass

    def setfn(self, fn):
        # self.args_f = ()
        # self.kwargs_f = {}
        self.fn = fn

    # def stop(self):
    #     self._stop_event.set()

    # def stopped(self):
    #     return self._stop_event.is_set()


class ProcessSnapShot:

    def __init__(self):
        logger.debug("ProcessSnapShot")
        self.proBefore = checkTasks()

    def killRedundant(self):
        logger.debug("killRedundant")
        self.proAfter = checkTasks()
        for i in range(len(self.proAfter)):
            if not (self.proAfter[i] in self.proBefore):
                os.system("taskkill /t /f /im {}".format(str(self.proAfter[i][0])))
                logger.debug("Python killed {}".format(self.proAfter[i]))


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


class Timer:

    def __init__(self):
        self.t = [time.clock()]
        self.tpn = ["Test Start"]
        self.count = 1

    def addTimeStamp(self, TimePointName):
        self.count += 1
        self.t.append(time.clock())
        self.tpn.append(TimePointName)
        logger.debug(("Add Time Point: {}".format(TimePointName)))

    def OutputTimeLog(self):
        self.path = r"C:\WorkingFolder\testCase\testModel\TimeLog.log"
        if not os.path.isfile(self.path):
            logger.info("TimeLog.txt path not exist!")
            return
        with open(self.path, "a") as file:
            data = []
            for i in xrange(self.count):
                fmt = "{tpn:<30}: {t:>6.2f} sec\n"
                data.append(fmt.format(tpn=self.tpn[i], t=self.t[i]))
            file.writelines(data)


def Logger(name=__name__, logLV=logging.INFO, pathTestlog=""):

    if not pathTestlog:
        pathTestlog = r".\testModel\TimeLog.log"
    logger = logging.getLogger(name)
    logger.setLevel(logLV)

    formatter = logging.Formatter("%(asctime)s: %(name)s: %(message)s")
    formatter2 = logging.Formatter("%(message)s")
    try:
        file_handler = logging.FileHandler(pathTestlog)
    except IOError:
        file_handler = logging.FileHandler(r"C:\WorkingFolder\testCase\testModel\TimeLog.log")
    file_handler.setLevel(logLV)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter2)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


logger = Logger()
