import inspect
import logging
import os
import Queue
# import subprocess
import sys
import threading

# import ConfigParser
# import json
import time
# from subprocess import PIPE

# import TestFile_BackUp as backuptool

sys.dont_write_bytecode = True


class PyTestLauncher():

    def __init__(self, sharedmd, sharedClass, insStages):

        argsinit = getattr(insStages, "argsInit", ())
        kwargsinit = getattr(insStages, "kwargsInit", {})
        self.insSharedclass = sharedClass(*argsinit, **kwargsinit)
        self.insstages = insStages
        self.q = sharedmd.q
        self._stop_event = threading.Event()
        self.CONSTATTR = self._constattr

    def Run(self):
        fn = getattr(self.insSharedclass, self.insstages.fn)
        if not fn:
            raise Exception("Function of Shared Class not Found!")
        logger.info("{0} Call Method: {1} ...".format("=" * 5, fn.__name__))
        self.thd = TempThread()
        self.thd.set(fn, (), {})
        self.thd.start()
        self.thd.join(0)

    def wait(self):
        hasTimeLimit = getattr(self.insstages, "tlm")
        tcont = 0
        while self.thd.isAlive():
            logger.info("Waiting ...")
            if tcont > hasTimeLimit:
                logger.info("!!!!! Time Out Failed ...")
                self.q.put(3, block=False)
                break
            tcont += 1
            time.sleep(1)

    def check_test_result(self):
        # Must get Q for clearing q data struct before check isIgnoredTr
        try:
            iResult = self.q.get(block=False)
        except Queue.Empty:
            logger.info("===== Get Q Data Failed ...")
            return "Failed"

        # Check the Stage Whether to Check Test Result or not
        if getattr(self.insstages, "isIgnoredTr", False):
            return "Successful"

        # Check iResult Type
        if iResult == 0:
            return "Successful"
        elif iResult == 3:
            return "Time Out"
        else:
            return "Failed"


    def _get_shared_mthd(self):
        if not hasattr(self.insstages, "fn"):
            raise Exception("Function for Test Stage not Found!")
        return getattr(self.insSharedclass, self.insstages.fn)

    def _reset_attr(self):
        CONSTATTR = {
            "isIgnoredTr": True,
            "tlm": 0,
        }
        logger.info("{0} {1}".format("=" * 5, "Reset InsStages Attritubes ..."))
        for key in self.CONSTATTR.iterkeys():
            self.insstages.__dict__[key] = CONSTATTR[key]

    @property
    def _constattr(self):
        keys = self.insstages.__dict__.keys()
        excludedKeys = [
            "t1",
            "t2",
            "t3",
            "sharedClassName",
            "fn",
            "mt",
            "argsInit",
            "kwargsInit",
        ]
        CONSTATTR = {}
        for excludekey in excludedKeys:
            if excludekey not in keys:
                continue
            keys.pop(keys.index(excludekey))
        # print keys
        for key in keys:
            CONSTATTR[key] = self.insstages.__dict__[key]
        return CONSTATTR

    @property
    def _stagesMethod(self):
        # Get Custom Stags for Maunal set stages
        isCustomStage = getattr(self.insstages, "isCustomStage", False)
        if isCustomStage:
            if not hasattr(self.insstages, "_customStage"):
                raise Exception("_customStage not Found")
            return getattr(self.insstages, "_customStage")()

        # Get methods from InsStags obj  which name was prefix "Stags_"
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
        threading.Thread.__init__(self)

    def run(self):
        self.fn(*self.args, **self.kwargs)

    def set(self, fn, args, kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs


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
