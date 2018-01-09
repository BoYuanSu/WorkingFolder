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
        self._resetAttrs()
        self.q = sharedmd.q
        self.fu = sharedmd.fbgzUser
        self.fp = sharedmd.fbgzPassword
        self.itercont = 0

    def run(self):
        logger.info("{0} {1:^25} {0}".format("@" * 20, self._StageName))
        self.syncVMInfo(self._StageName)
        fn = self._getSharedMthd
        logger.info("{0} Call Method: {1} ...".format("=" * 5, fn.__name__))
        self.thd = TempThread()
        self.thd.set(fn, self.insstages.fnargs, self.insstages.fnkwargs)
        self.thd.start()
        self.thd.join(0)
        # logger.info("{0} {1} {0}".format("@" * 20, self._StageName))

    def wait(self, ditcProcess={}):
        TimeLimit = getattr(self.insstages, "tlm")
        self.isIgnored_TimeOut = True
        if TimeLimit == 0:
            # if Time Limit == 0 means don't check time out
            logger.info("===== Disable Checking TimeOut")
        else:
            self.isIgnored_TimeOut = False
            logger.info("{} Enable Checking TimeOut: {} min(s)".format("=" * 5, TimeLimit / 60))

        tcont = 0
        self.isTimeOut = False
        while self.thd.isAlive():
            # logger.info("Waiting ...")
            if tcont > TimeLimit and TimeLimit:
                logger.info("!!!!! Time Out ...")
                self.isTimeOut = True
                break
            tcont += 1
            time.sleep(1)
        self.itercont += 1

    def checkTestResult(self):
        tr = self._wrapCheckTestResult()
        self._resetAttrs()
        logger.info("{0} Test Result: {1} !".format("=" * 5, tr))

        return tr

    def _wrapCheckTestResult(self):
        isIgnored_TestResult = getattr(self.insstages, "isIgnoredTr")
        isIgnored_TimeOut = self.isIgnored_TimeOut
        isTimeOut = self.isTimeOut
        logger.debug("""{},
            isIgnored_TestResult: {}
            isIgnored_TimeOut: {},
            isTimeOut: {}""".format("=" * 5, isIgnored_TestResult, isIgnored_TimeOut, isTimeOut))
        fmt = "Log True loggic {0}"
        while True:
            iResult = self._getQ()
            if iResult == 5:
                return "Exception Failed"
            fmt = "===== Log True loggic {0}"
            if isIgnored_TimeOut and not isIgnored_TestResult:
                logger.info(fmt.format("test_nt_r"))
                if iResult == "Empty" or iResult == 4:
                    return "Failed"
                if iResult == 0:
                    return "Successful"

            if not isIgnored_TimeOut and not isIgnored_TestResult:
                logger.info(fmt.format("test_t_r"))
                if iResult == "Empty" or iResult == 4:
                    return "Failed"
                if iResult == 1:
                    return "Successful"

            if not isIgnored_TimeOut and isIgnored_TestResult:
                logger.info(fmt.format("test_t_nr"))
                if iResult == "Empty":
                    return "Failed"
                if iResult == 2:
                    return "Successful"

            if isIgnored_TimeOut and isIgnored_TestResult:
                logger.info(fmt.format("test_nt_nr"))
                if iResult == "Empty":
                    return "Failed"
                if iResult == 3:
                    return "Successful"

    def _getQ(self):
        # logger.info("Q siez: {}".format(self.q.qsize()))
        if self.q.qsize() == 0:
            return "Empty"
        return self.q.get(block=False)
        # logger.info("Q result: {}".format(i))
        # logger.info("{0} Get Q Data, Current Q size: {1} ...".format("=" * 5, self.q.qsize()))

    @property
    def _getSharedMthd(self):
        if not getattr(self.insstages, "fn"):
            raise Exception("Attribute fn Setted by Stages not Found!")
        if not hasattr(self.insSharedclass, self.insstages.fn):
            raise Exception("Function(method) of Sharedclass Called by Stage not Found!")
        return getattr(self.insSharedclass, self.insstages.fn)

    def _resetAttrs(self):
        CONSTATTR = {
            "fn": None,
            "fnargs": (),
            "fnkwargs": {},
            "isIgnoredTr": False,
            "tlm": 0,
        }
        logger.info("{0} {1}".format("=" * 5, "Reset InsStages Attritubes ..."))
        for key in CONSTATTR.iterkeys():
            self.insstages.__dict__[key] = CONSTATTR[key]

    @property
    def stagesMethod(self):
        # Get Custom Stags for Maunal set stages
        isCustomStage = getattr(self.insstages, "isCustomStage", False)
        if isCustomStage:
            if not hasattr(self.insstages, "_customStage"):
                raise Exception("_customStage not Found")
            self._recordStagesName(getattr(self.insstages, "_customStage")())
            return getattr(self.insstages, "_customStage")()

        # Get methods from InsStags obj  which name was prefix "Stags_"
        methods = []
        methodsTup = inspect.getmembers(self.insstages, inspect.ismethod)
        for mthdtup in methodsTup:
            if mthdtup[0].startswith("Stage_"):
                methods.append(mthdtup[1])
        if len(methods) == 0:
            raise Exception("Stages from TestScript not Found!")
        self._recordStagesName(methods)
        return methods

    @property
    def _StageName(self):
        return self.calledStagesName[self.itercont]

    def _recordStagesName(self, methods):
        self.calledStagesName = []
        for stage in methods:
            self.calledStagesName.append(stage.__name__)

    @staticmethod
    def ReturnTestFinish(pathReserve=""):
        pathFinishProcess = r"C:\Work\XenTools\Test_Finish_Process\Test_Process_Process.py"
        if pathReserve != "":
            pathReserve = " -fp " + pathReserve
        os.popen("call python {} {}".format(pathFinishProcess, pathReserve))

    @staticmethod
    def syncVMInfo(StageName):
        logger.debug("{} {}".format("~" * 5, StageName))
        logger.info("===== Return Stage Info to Django DB ...")
        path = r"C:\work\VM_Require_Tools\VM_Info_Sync\VM_Info_Sync.py"
        os.popen("python {} -sn \"{}\"".format(path, StageName))


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

    formatter = logging.Formatter("%(asctime)s: %(message)s")
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
