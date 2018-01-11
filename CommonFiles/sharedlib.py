import inspect
import logging
import os
# import subprocess
import sys
import threading
# import ConfigParser
# import json
import time
import win32com.client
# from subprocess import PIPE

# import TestFile_BackUp as backuptool

sys.dont_write_bytecode = True

logLV_ = logging.DEBUG


class PyTestLauncher:

    def __init__(self, sharedmd, sharedClass, insStages):

        argsinit = getattr(insStages, "argsInit", ())
        kwargsinit = getattr(insStages, "kwargsInit", {})
        self.insSharedclass = sharedClass(*argsinit, **kwargsinit)
        self.insStages = insStages
        self._resetAttrs()
        self.q, self.fu, self.fp = self._getSharedmdAttr(sharedmd, ["q", "fu", "fp"])
        self.itercont = 0

    def run(self):
        logger.info("{0} {1:^25} {0}".format("@" * 20, self._StageName))
        self.syncVMInfo(self._StageName)
        fn = self._getSharedMthd
        logger.info("{0} Call Method: {1} ...".format("=" * 5, fn.__name__))
        self.thd = TempThread()
        self.thd.set(fn, self.insStages.fnargs, self.insStages.fnkwargs)
        self.thd.start()
        self.thd.join(0)

    def wait(self, ditcProcess={}):
        TimeLimit = getattr(self.insStages, "tlm")
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

    def checkTestResult(self):
        tr = self._wrapCheckTestResult()
        logger.info("{0} Test Result: {1} !".format("=" * 5, tr))
        self.reportBugProxy_(tr)
        self._resetAttrs()
        self.itercont += 1
        return tr

    def _wrapCheckTestResult(self):
        isIgnored_TestResult = getattr(self.insStages, "isIgnoredTr")
        isIgnored_TimeOut = self.isIgnored_TimeOut
        isTimeOut = self.isTimeOut
        logger.debug("""{}
            isIgnored_TestResult: {}
            isIgnored_TimeOut: {},
            isTimeOut: {}""".format("~" * 5, isIgnored_TestResult, isIgnored_TimeOut, isTimeOut))
        fmt = "Log True loggic {0}"
        while True:
            iResult = self._getQ()
            if iResult == 5:
                return "Exception Failed"
            fmt = "~~~~~ Log True loggic {0}"
            if isIgnored_TimeOut and not isIgnored_TestResult:
                logger.debug(fmt.format("No TimeOutcheck, TestResultcheck"))
                if iResult == "Empty" or iResult == 4:
                    return "Failed"
                if iResult == 0:
                    return "Successful"

            if not isIgnored_TimeOut and not isIgnored_TestResult:
                logger.debug(fmt.format("TimeOutcheck, Check TestResultcheck"))
                if iResult == "Empty" or iResult == 4:
                    return "Failed"
                if iResult == 1:
                    return "Successful"

            if not isIgnored_TimeOut and isIgnored_TestResult:
                logger.debug(fmt.format("TimeOutcheck, No TestResultcheck"))
                if iResult == "Empty":
                    return "Failed"
                if iResult == 2:
                    return "Successful"

            if isIgnored_TimeOut and isIgnored_TestResult:
                logger.debug(fmt.format("No TimeOutcheck, No TestResultcheck"))
                if iResult == "Empty":
                    return "Failed"
                if iResult == 3:
                    return "Successful"

    def _getQ(self):
        logger.debug("~~~~~ Q siez: {}".format(self.q.qsize()))
        if self.q.qsize() == 0:
            return "Empty"
        elif self.q.qsize() != 1:
            logger.debug("~~~~~ Other tr may be get")
        return self.q.get(block=False)
        # logger.debug("~~~~~ Q result: {}".format(i))
        # logger.debug("{0} Get Q Data, Current Q size: {1} ...".format("=" * 5, self.q.qsize()))

    def reportBugProxy_(self, tr):
        # collect information for Report_Bug_Proxy
        insStages = self.insStages
        t1 = getattr(insStages, "t1")
        t2 = getattr(insStages, "t2")
        t3 = getattr(insStages, "t3")
        mt = getattr(insStages, "mt")
        sn = self._StageName
        se = ""
        aip = ""
        bcp = ""
        fu = self.fu
        fp = self.fp
        self.reportBugProxy(t1, t2, t3, mt, sn, tr, se, aip, bcp, fu, fp)

    @property
    def _getSharedMthd(self):
        logger.debug("~~~~~ Collecting execute function ...")
        if not getattr(self.insStages, "fn"):
            raise Exception("Attribute fn Setted by Stages not Found!")
        if not hasattr(self.insSharedclass, self.insStages.fn):
            raise Exception("Function(method) of Sharedclass Called by Stage not Found!")
        return getattr(self.insSharedclass, self.insStages.fn)

    @staticmethod
    def _getSharedmdAttr(sharedmd, sharedmdAttrs):
        logger.debug("~~~~~ Collecting Test Info ...")
        Attrs = []
        ErrorMsg = {
            "q": "Set q = Queue.LifoQueue in your shared module",
            "fu": "Set your Fogbugz account, ex: fu = \"paulsu\"",
            "fp": "Set your Fogbugz password (type string), ex: fp = \"123456\"",
            "sharedTCPjsPath": "Set your TC  ProjectSuite Path",
            "sharedTCPjName": "Set your TC  Project Name"
        }
        for sharedmdAttrName in sharedmdAttrs:
            if not hasattr(sharedmd, sharedmdAttrName):
                raise Exception(ErrorMsg[sharedmdAttrName])
            Attrs.append(getattr(sharedmd, sharedmdAttrName))
        return tuple(Attrs)

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
            self.insStages.__dict__[key] = CONSTATTR[key]

    @property
    def stagesMethod(self):
        # Get Custom Stags for Maunal set stages
        isCustomStage = getattr(self.insStages, "isCustomStage", False)
        if isCustomStage:
            if not hasattr(self.insStages, "_customStage"):
                raise Exception("_customStage not Found")
            methods = getattr(self.insStages, "_customStage")()
            self._recordStagesName(methods)
            return methods

        # Get methods from InsStags obj  which name was prefix "Stags_"
        methods = []
        methodsTup = inspect.getmembers(self.insStages, inspect.ismethod)
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
    def syncVMInfo(StageName):
        logger.debug("{} {}".format("~" * 5, StageName))
        logger.info("===== Upload Stage Info to Django DB ...")
        path = r"C:\work\VM_Require_Tools\VM_Info_Sync\VM_Info_Sync.py"
        os.popen("python {} -sn \"{}\"".format(path, StageName))

    @staticmethod
    def reportBugProxy(t1, t2, t3, mt, sn, tr, se, aip, bcp, fu, fp):
        logger.info("===== Upload Report Bug Info to Django DB ...")
        cmd = 'python "{path}" -t1 "{t1}" -t2 "{t2}" -t3 "{t3}" -sn "{sn}" -tr "{tr}" -se "{se}" -aip "{aip}" -bcp "{bcp}" -fu "{fu}" -fp "{fp}" -mt "{mt}"'.format(
            path=r"C:\work\XenTools\VM_Require_Tools\FogBugzAPITest\Report_Bug_Proxy.py",
            t1=t1,
            t2=t2,
            t3=t3,
            sn=sn,
            tr=tr,
            se=se,
            aip=aip,
            bcp=bcp,
            fu=fu,
            fp=fp,
            mt=mt)
        os.popen(cmd)

    @staticmethod
    def ReturnTestFinish(pathReserve=""):
        logger.info("===== Upload Test Complete Info to Django DB ...")
        pathFinishProcess = r"C:\Work\XenTools\Test_Finish_Process\Test_Process_Process.py"
        if pathReserve != "":
            pathReserve = " -fp " + pathReserve
        os.popen("call python {} {}".format(pathFinishProcess, pathReserve))


class TETestLauncher(PyTestLauncher):

    def __init__(self, sharedmd, sharedClass, insStages):
        argsinit = getattr(insStages, "argsInit", ())
        kwargsinit = getattr(insStages, "kwargsInit", {})
        self.insSharedclass = sharedClass(*argsinit, **kwargsinit)
        self.insStages = insStages
        self.fu, self.fp = self._getSharedmdAttr(sharedmd, ["fu", "fp"])
        self.apiTE = APIsTE(
            self._getSharedmdAttr(sharedmd, ["sharedTCPjsPath"])[0],
            self._getSharedmdAttr(sharedmd, ["sharedTCPjName"])[0],
            )
        self._resetAttrs()
        self.itercont = 0

    def quitTECOM(self):
        self.apiTE.Quit()

    @property
    def RoutinesIterator(self):
        Routines = []
        Iterator = self.apiTE.getRoutinesIterator()
        Iterator.Reset()
        while Iterator.HasNext():
            temp = Iterator.Next
            if temp.UnitName == self.unitName:
                Routines.append(temp.Name)
                logger.info("{} Routine ({}) found ...".format("=" * 5, temp.Name))
        if len(Routines) == 0:
            raise Exception("Routines not Found")
        Routines.sort()
        return Routines

    def run(self):
        pass

    def wait(self):
        pass

    def checkTestResult(self):
        pass

    def _wrapCheckTestResult(self, iResult):
        isIgnored_TestResult = getattr(self.insStages, "isIgnoredTr")
        isIgnored_TimeOut = self.isIgnored_TimeOut
        isTimeOut = self.isTimeOut
        logger.debug("""{}
            isIgnored_TestResult: {}
            isIgnored_TimeOut: {},
            isTimeOut: {}""".format("~" * 5, isIgnored_TestResult, isIgnored_TimeOut, isTimeOut))
        fmt = "~~~~~ Log True loggic {0}"
        if isIgnored_TimeOut and not isIgnored_TestResult:
            logger.debug(fmt.format("No TimeOutcheck, TestResultcheck"))
            if iResult == 0:
                return "Successful"

        if not isIgnored_TimeOut and not isIgnored_TestResult:
            logger.debug(fmt.format("TimeOutcheck, Check TestResultcheck"))
            if not isTimeOut and iResult == 0:
                return "Successful"

        if not isIgnored_TimeOut and isIgnored_TestResult:
            logger.debug(fmt.format("TimeOutcheck, No TestResultcheck"))
            if not isTimeOut:
                return "Successful"

        if isIgnored_TimeOut and isIgnored_TestResult:
            logger.debug(fmt.format("No TimeOutcheck, No TestResultcheck"))
            return "Successful"
        return "Failed"

    def runAllRoutines(self):
        logger.info("===== Run All Routines in Unit")
        if not hasattr(self.insStages, "unitname"):
            raise Exception("UnitName not Found")

        self.unitName = self.insStages.unitname
        self.isTimeOut = False
        self.isIgnored_TimeOut = True

        for Routine in self.RoutinesIterator:
            logger.info("{0} {1:^25} {0}".format("@" * 20, Routine))
            self.syncVMInfo(Routine)
            self.apiTE.runRoutine(self.unitName, Routine)
            while True:
                time.sleep(1)
                if not self.apiTE.isRunningRoutine:
                    break
            tr = self._wrapCheckTestResult(self.apiTE.getResultStatus)
            self.reportBugProxy_(Routine, tr)
            logger.info("{0} Test Result: {1} !".format("=" * 5, tr))
            if tr != "Successful":
                break

    def reportBugProxy_(self, sn, tr):
        # collect information for Report_Bug_Proxy
        insStages = self.insStages
        t1 = insStages.t1
        t2 = insStages.t2
        t3 = insStages.t3
        mt = insStages.mt
        sn = sn
        se = ""
        aip = ""
        bcp = ""
        fu = self.fu
        fp = self.fp
        self.reportBugProxy(t1, t2, t3, mt, sn, tr, se, aip, bcp, fu, fp)

    @property
    def isRunAllRoutines(self):
        if hasattr(self.insSharedclass, "isRunAllRoutines"):
            return self.insSharedclass.isRunAllRoutines
        return False

    @property
    def stagesMethod(self):
        # Get Custom Stags for Maunal set stages
        isCustomStage = getattr(self.insStages, "isCustomStage", False)
        if isCustomStage:
            if not hasattr(self.insStages, "_customStage"):
                raise Exception("_customStage not Found")
            methods = getattr(self.insStages, "_customStage")()
            self._recordStagesName(methods)
            return methods

        # Get methods from InsStags obj  which name was prefix "Stags_"
        methods = []
        methodsTup = inspect.getmembers(self.insStages, inspect.ismethod)
        for mthdtup in methodsTup:
            if mthdtup[0].startswith("Stage_"):
                methods.append(mthdtup[1])
        if len(methods) == 0:
            raise Exception("Stages from TestScript not Found!")
        self._recordStagesName(methods)
        return methods


class APIsTE:

    def __init__(self,  sharedTCPjsPath, sharedTCPjName):
        self.TCPjsPath = sharedTCPjsPath
        self.TCPjName = sharedTCPjName
        self.APP = self.dispatchTE()
        self.APP.Manager.RunMode = 1
        self.openTCPjs()

    @staticmethod
    def dispatchTE():
        logger.debug("~~~~~ Dispatch TE ...")
        try:
            return win32com.client.dynamic.Dispatch("TestExecute.TestExecuteApplication")
        except Exception:
            logger.debug("~~~~~ Dispatch TE Failed ...")

    def openTCPjs(self):
        logger.debug("{} Open TC ProjectSuite: {} ...".format(
            "~" * 5,
            os.path.basename(self.TCPjsPath)))
        while True:
            if self.APP.Integration.OpenProjectSuite(self.TCPjsPath):
                logger.debug("{} IsProjectSuiteOpened: {} ...".format(
                    "~" * 5,
                    self.APP.Integration.IsProjectSuiteOpened()))
                return

    def getRoutinesIterator(self):
        logger.debug("~~~~~ Get Project Routines Iterator ...")
        return self.APP.Integration.ProjectRoutinesIterator(self.TCPjName)

    def runRoutine(self, unitName, Routine):
        self.APP.Integration.RunRoutine(self.TCPjName, unitName, Routine)

    @property
    def isRunningRoutine(self):
        return self.APP.Integration.IsRunning()

    @property
    def getResultStatus(self):
        return self.APP.Integration.GetLastResultDescription().Status

    def Quit(self):
        logger.debug("~~~~~ Quit TE ...")
        self.APP.Quit()


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


logger = Logger(logLV=logLV_)
