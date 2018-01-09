# -*- coding: utf-8 -*-
import inspect
import logging
import os
import sys
import types

sys.dont_write_bytecode = True

try:
    os.chdir(os.path.dirname(__file__))
except WindowsError:
    pass
sys.path.append("..")

from CommonFiles import *
from testScript import *


# For Test Mode Setting(Test or not, 1:Yes, 0:No)
iTestMode = 1

# Setting log level
logLV = logging.DEBUG
pathTestlog = r".\testModel\TimeLog.log"
"""
Options List of logging Level
CRITICAL = 50
ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
NOTSET = 0
"""


def main():
    """
    Doing main test
    """
    insStages = Run.getStageClass()

    sharedmd, sharedclass = Run.getSharedModule(insStages.sharedClassName)

    testlauncher = sharedlib.PyTestLauncher(sharedmd, sharedclass, insStages)

    for stage in testlauncher.stagesMethod:
        stage()
        testlauncher.run()
        testlauncher.wait()
        tr = testlauncher.checkTestResult()
        timerecord.addTimeStamp(stage.__name__)
        # Used for unittest
        if tr != testlauncher.insstages.assertattr:
            raise AssertionError
        logger.debug("{0} Test Result: {1} !".format("=" * 5, "Pass"))


class Run:

    @staticmethod
    def findLoggerFilehdlr():
        print "close logger handlers"
        for name, obj in globals().items():
            if not isinstance(obj, types.ModuleType):
                continue
            if "..\CommonFiles" not in os.path.dirname(str(obj)):
                continue
            # print "{:<20} :: {}".format(name, obj)
            modules = inspect.getmembers(obj, inspect.ismodule)
            for m in modules:
                # print m[0]
                Run.closeHdlr(m[1])
            Run.closeHdlr(obj)

        for hdlr in logger.handlers:
            hdlr.close()
        with open(pathTestlog, "a") as log:
            log.write("{0} End log {0}\n".format("=" * 50))

    @staticmethod
    def closeHdlr(ref):
        try:
            for handler in ref.logger.handlers:
                handler.close()
            # print "=" * 10 + "> delete hdlr " + str(ref.__name__)
        except AttributeError:
            pass

    @staticmethod
    def getStageClass():
        testclass = []
        for name, obj in globals().items():
            if not isinstance(obj, types.ModuleType):
                continue
            if not hasattr(obj, "__file__"):
                continue
            # print "{:<20} :: {}".format(name, obj)
            # print os.path.dirname(obj.__file__)
            if r":\WorkingFolder\testCase\testScript" in os.path.dirname(obj.__file__):
                testclass = inspect.getmembers(obj, inspect.isclass)
        if not len(testclass):
            raise Exception("TestStage not found")
        for cls in testclass:
            if cls[0] == "TestStage":
                return cls[1]()

    @staticmethod
    def getSharedModule(clsname):
        for name, obj in globals().items():
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


if __name__ == "__main__":

    timerecord = sharedlib.Timer()

    logger = sharedlib.Logger(__name__, logLV=logLV, pathTestlog=pathTestlog)

    if iTestMode == 0:
        processes = sharedlib.ProcessSnapShot()

    print "=" * 100
    main()
    # print "=" * 100

    timerecord.OutputTimeLog()

    Run.findLoggerFilehdlr()

    os.system("copy {0} {0}bak /y".format(r".\testModel\TimeLog.log"))
    # os.system("del {} /s /q".format(r".\testModel\TimeLog.log"))

    if iTestMode == 0:
        TestFile_BackUp

        # Test Finish, kill unused process(*.exe)
        processes.killRedundant()
        # Copy "TestCaseFN" folder to C:\work\LOG\TestID
        # Return Test Finish to Django DB
        sharedlib.PyTestLauncher.ReturnTestFinish(os.path.dirname(__file__))
