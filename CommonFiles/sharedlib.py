import inspect
import logging
import os
# import subprocess
import sys
import threading
# import ConfigParser
# import json
import time
import types
import win32com.client
# from subprocess import PIPE

sys.dont_write_bytecode = True

# import TestFile_BackUp as backuptool
try:
    import AccessQAXenDB
except ImportError:
    pass




cwd = os.getcwd()
logLV_ = logging.INFO
# Default TC log path
logTC = os.path.join(cwd, r".\testModel\TCLog_{0}_{1}.mht")
logPy = r".\testModel\TimeLog.log"


class PyTestLauncher:

    def __init__(self, sharedmd, sharedClass, insStages):
        """
        initialized shared class
        reset attribute in Stages instance
        get some information for module shared lib
        itercont is used for counting excuted stages
        """
        argsinit = getattr(insStages, "argsInit", ())
        kwargsinit = getattr(insStages, "kwargsInit", {})
        self.insSharedclass = sharedClass(*argsinit, **kwargsinit)
        self.insStages = insStages
        self._resetAttrs()
        self.q, self.fu, self.fp = self._getSharedmdAttr(sharedmd, ["q", "fu", "fp"])
        self.itercont = 0
        self.totalTimeLimit = 0
        self.totalTimecont = 0

    def run(self):
        """
        return Django current stage
        initialized thread instance and starting testing
        attributes bellow are used to pass arguments to shared method
        self.insStages.fnargs
        self.insStages.fnkwargs
        """
        logger.info("{0} {1:^25} {0}".format("@" * 20, self._StageName))
        self.syncVMInfo(self._StageName)
        # Get current stage called method reference
        fn = self._getSharedMthd
        logger.info("{0} Call Method: {1} ...".format("=" * 5, fn.__name__))
        self.thd = TempThread()
        self.thd.set(fn, self.insStages.fnargs, self.insStages.fnkwargs)
        self.thd.start()
        self.thd.join(0)

    def wait(self, ditcProcess={}):
        """
        waiting test done
        """
        TimeLimit = getattr(self.insStages, "tlm", 0)
        self.isIgnored_TimeOut = True
        if TimeLimit == 0:
            # if Time Limit == 0 means don't check time out
            logger.debug("!!!!! Disable Checking TimeOut")
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
            if self.totalTimecont > self.totalTimeLimit:
                self.isReachCaseTimeLimit = True
                break
            tcont += 1
            # self.totalTimecont += 1
            time.sleep(1)

    def checkTestResult(self):
        """
        fake check test result method to wrap real check test result
        return Bug_Proxy to Django
        reset few Stages instance attributes
        excuted stages plus one
        """
        tr = self._wrapCheckTestResult()
        logger.info("{0} Test Result: {1} !".format("=" * 5, tr))
        self.reportBugProxy_(tr)
        if tr == "Time Out":
            return tr
        self._resetAttrs()
        self.itercont += 1
        return tr

    def _wrapCheckTestResult(self):
        if getattr(self, "isReachCaseTimeLimit", False):
            return "Time Out"
        isIgnored_TestResult = getattr(self.insStages, "isIgnoredTr", False)
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
        # communicate with thread by lifo Q
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
    def _getSharedMthd(self):
        logger.debug("~~~~~ Collecting execute function ...")
        if not getattr(self.insStages, "fn"):
            raise Exception("Attribute fn Setted by Stages not Found!")
        if not hasattr(self.insSharedclass, self.insStages.fn):
            raise Exception("Function(method) of Sharedclass Called by Stage not Found!")
        return getattr(self.insSharedclass, self.insStages.fn)

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
            self._getSharedmdAttr(sharedmd, ["sharedTCPjName"])[0])
        self._resetAttrs()
        self.itercont = 0
        self.totalTimeLimit = 0
        self.totalTimecont = 0

    def run(self):
        logger.info("{0} {1:^25} {0}".format("@" * 20, self._StageName))
        self.syncVMInfo(self._StageName)
        unitName, Routine = self._getSharedMthd
        logger.info("{0} Call Method: {1}::{2} ...".format("=" * 5, unitName, Routine))
        argsList = self.insStages.fnargs
        try:
            self.isCallRoutineFail = False
            if argsList:
                self.apiTE.runRoutine(unitName, Routine)
            else:
                self.apiTE.runRoutineEx(unitName, Routine, argsList)
        except Exception:
            self.isCallRoutineFail = True

    def wait(self):
        TimeLimit = getattr(self.insStages, "tlm")
        self.isIgnored_TimeOut = True
        if TimeLimit == 0:
            # if Time Limit == 0 means don't check time out
            logger.debug("!!!!! Disable Checking TimeOut")
        else:
            self.isIgnored_TimeOut = False
            logger.info("{} Enable Checking TimeOut: {} min(s)".format("=" * 5, TimeLimit / 60))

        tcont = 0
        self.isTimeOut = False
        while self.apiTE.IsRunning:
            if tcont > TimeLimit and TimeLimit:
                logger.info("!!!!! Time Out ...")
                self.apiTE.stopRunning()
                self.isTimeOut = True
                break
            if self.totalTimecont > self.totalTimeLimit and self.totalTimeLimit:
                self.isReachCaseTimeLimit = True
                self.apiTE.stopRunning("Reach Time Limit of Case")
                break
            tcont += 1
            self.totalTimecont += 1
            time.sleep(1)

    def checkTestResult(self):
        if self.isCallRoutineFail:
            logger.error("!!!!! Call Routine Failed ...")
            self.reportBugProxy_(self._StageName, "Call Routine Failed")
            return "Call Routine Failed"
        tr = self._wrapCheckTestResult(self.apiTE.getResultStatus)
        logger.info("{0} Test Result: {1} !".format("=" * 5, tr))
        fmt = logTC.format(getTestListID(), self._StageName)
        self.apiTE.exportResultLog(fmt)
        self.reportBugProxy_(tr)
        if tr == "Reach Time Limit of Case":
            return tr
        self._resetAttrs()
        self.itercont += 1
        return tr

    def _wrapCheckTestResult(self, iResult):
        if getattr(self, "isReachCaseTimeLimit", False):
            return "Reach Time Limit of Case"
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

        for Routine in self._routinesIterator:
            logger.info("{0} {1:^25} {0}".format("@" * 20, Routine))
            self.syncVMInfo(Routine)
            self.apiTE.runRoutine(self.unitName, Routine)
            while True:
                time.sleep(1)
                if not self.apiTE.IsRunning:
                    break
            tr = self._wrapCheckTestResult(self.apiTE.getResultStatus)
            fmt = logTC.format(getTestListID(), Routine)
            self.apiTE.exportResultLog(fmt)
            self.reportBugProxy_(tr)
            logger.info("{0} Test Result: {1} !".format("=" * 5, tr))
            if tr != "Successful":
                break

    @property
    def isRunAllRoutines(self):
        if hasattr(self.insSharedclass, "isRunAllRoutines"):
            return self.insSharedclass.isRunAllRoutines
        return False

    @property
    def _routinesIterator(self):
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
        self._recordRoutinesName(Routines)
        return Routines

    @property
    def _getSharedMthd(self):
        logger.debug("~~~~~ Collecting execute function ...")
        if not getattr(self.insStages, "fn"):
            raise Exception("Attribute fn Setted by Stages not Found!")
        fn = self.insStages.fn.split(".")
        if len(fn) != 2:
            raise Exception("fn formation Error! Concatenate Unit/Routine Name with \".\"")
        return fn[0], fn[1]

    @property
    def _StageName(self):
        if self.isRunAllRoutines:
            return self.calledRoutinesName[self.itercont]
        return self.calledStagesName[self.itercont]

    def _recordRoutinesName(self, methods):
        self.calledRoutinesName = methods

    def quitTECOM(self):
        logger.info("===== Quit TE COM ...")
        self.apiTE.Quit()


class APIsTE:

    def __init__(self, sharedTCPjsPath, sharedTCPjName):
        self.TCPjsPath = sharedTCPjsPath
        self.TCPjName = sharedTCPjName
        self.APP = self.dispatchTE()
        self.APP.Manager.RunMode = 1
        self.openTCPjs()

    @staticmethod
    def dispatchTE():
        logger.debug("~~~~~ Dispatch TE ...")
        try:
            time.sleep(1)
            return win32com.client.dynamic.Dispatch("TestExecute.TestExecuteApplication")
        except Exception:
            logger.debug("~~~~~ Dispatch TE Failed ...")

    def openTCPjs(self):
        self.TCPjsPath = os.path.join(cwd, self.TCPjsPath)
        if not os.path.isfile(self.TCPjsPath):
            raise Exception("Invalid TC Project Suite Path")
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

    def runRoutineEx(self, unitName, Routine, argsList):
        self.APP.Integration.RunRoutineEx(self.TCPjName, unitName, Routine, list(argsList))

    @property
    def IsRunning(self):
        return self.APP.Integration.IsRunning()

    def stopRunning(self, msg="Time Out"):
        logger.error("{0} Stop Running Routine: {1}".format("!" * 5, msg))
        self.APP.Integration.Halt(msg)

    @property
    def getResultStatus(self):
        try:
            return self.APP.Integration.GetLastResultDescription().Status
        except AttributeError:
            logger.warning("!!!!! Get TC Result Description Failed")
            return 2

    def exportResultLog(self, path=logTC):
        if not os.path.isdir(os.path.dirname(path)):
            logger.warning("{} Log Path is not illegal")
            return
        self.APP.Integration.ExportResults(path)

    def Quit(self):
        while True:
            if self.APP.Integration.CloseProjectSuite():
                logger.debug("~~~~~ Close TC ProjectSuit ...")
                break
        logger.debug("~~~~~ Quit TE ...")
        self.APP.Quit()
        while True:
            if "TestExecute.exe" not in os.popen("tasklist").read():
                break


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
        self.path = r".\testModel\TimeLog.log"
        if not os.path.isfile(self.path):
            logger.info("TimeLog.txt path not exist!")
            return
        with open(self.path, "a") as file:
            data = []
            for i in xrange(self.count):
                fmt = "{tpn:<30}: {t:>6.2f} sec\n"
                data.append(fmt.format(tpn=self.tpn[i], t=self.t[i]))
            file.writelines(data)


class SearchRef:

    @staticmethod
    def getStageClass(dictGlobals):
        testclass = []
        for name, obj in dictGlobals.items():
            if not isinstance(obj, types.ModuleType):
                continue
            if not hasattr(obj, "__file__"):
                continue
            # print "{:<20} :: {}".format(name, obj)
            # print os.path.dirname(obj.__file__)
            if r"\testCase\testScript" in os.path.dirname(obj.__file__):
                testclass = inspect.getmembers(obj, inspect.isclass)
        if not len(testclass):
            raise Exception("TestStage not found")
        for cls in testclass:
            if cls[0] == "TestStage":
                return cls[1]()

    @staticmethod
    def getSharedModule(dictGlobals, clsname):
        for name, obj in dictGlobals.items():
            if not isinstance(obj, types.ModuleType):
                continue
            if "..\CommonFiles" not in os.path.dirname(str(obj)):
                continue
            # Get Modules import from ..\CommonFildes
            modules = inspect.getmembers(obj, inspect.ismodule)
            # iter over all class in modules and get matched classname
            for m in modules:
                clses = inspect.getmembers(m[1], inspect.isclass)
                for cls in clses:
                    if cls[0] == clsname:
                        return m[1], cls[1]

    @staticmethod
    def isTCTest(sharedmd):
        if hasattr(sharedmd, "sharedTCPjsPath") and getattr(sharedmd, "sharedTCPjsPath", ""):
            return True
        return False


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
        pathTestlog = logPy
    logger = logging.getLogger(name)
    logger.setLevel(logLV)

    formatter = logging.Formatter("%(asctime)s: %(message)s")
    formatter2 = logging.Formatter("%(message)s")
    try:
        file_handler = logging.FileHandler(pathTestlog)
    except IOError:
        file_handler = logging.FileHandler(r"TimeLog.log")
    file_handler.setLevel(logLV)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter2)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def getTestListID():
    try:
        db = AccessQAXenDB.AccessQAXenDB()
    except Exception:
        return AccessQAXenDB.GetFakeTestID()
    return db.CurrentTestRecord().id

def getCaseTimeLimit():
    try:
        db = AccessQAXenDB.AccessQAXenDB()
    except Exception:
        return 0
    return int(db.GetTestCaseExeTime())


def findLoggerFilehdlr(dictGlobals):
    print "close logger handlers"
    for name, obj in dictGlobals.items():
        if not isinstance(obj, types.ModuleType):
            continue
        if "..\CommonFiles" not in os.path.dirname(str(obj)):
            continue
        # print "{:<20} :: {}".format(name, obj)
        modules = inspect.getmembers(obj, inspect.ismodule)
        for m in modules:
            # print m[0]
            closeHdlr(m[1])
        closeHdlr(obj)

    with open(logPy, "a") as log:
        log.write("{0} End log {0}\n".format("=" * 50))


def closeHdlr(ref):
    try:
        if isinstance(ref, logging.Logger):
            tmplogger = ref
        else:
            tmplogger = ref.logger
        for handler in tmplogger.handlers:
            handler.close()
        # print "=" * 10 + "> delete hdlr " + str(ref.__name__)
    except AttributeError:
        pass


logger = Logger(logLV=logLV_)


def main():
    pass

if __name__ == '__main__':
    main()
