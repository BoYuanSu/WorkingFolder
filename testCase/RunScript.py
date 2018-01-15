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

from CommonFiles import sharedlib

"""
import your Module CommonFiles/TestScript here
pass module/module class/TestScript instance reference into sharedlib.TETestLauncher

from CommonFiles.SAM import samlib
from testScript import test_25_mkxl

insStages = test_25_mkxl.TestStage()
sharedmd = samlib
sharedclass = samlib.Sample
testlauncher = sharedlib.TETestLauncher(sharedmd, sharedclass, insStages)
"""
from CommonFiles.FEA import fealib
# from CommonFiles.SAM import samlib
# from CommonFiles.TE1by1 import te1by1lib
# from CommonFiles.TEALL import tealllib

from testScript import testscript
# from testScript import test_25_mkxl
# from testScript import test_00_teall
# from testScript import test_00_te1by1


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
    # insStages = SearchRef.getStageClass(globals())
    insStages = testscript.TestStage()

    # sharedmd, sharedclass = SearchRef.getSharedModule(globals(), insStages.sharedClassName)
    sharedmd = fealib
    sharedclass = fealib.FEAInterface

    if sharedlib.SearchRef.isTCTest(sharedmd):
        testlauncher = sharedlib.TETestLauncher(sharedmd, sharedclass, insStages)
        if testlauncher.isRunAllRoutines:
            testlauncher.runAllRoutines()
            testlauncher.quitTECOM()
            return
    else:
        testlauncher = sharedlib.PyTestLauncher(sharedmd, sharedclass, insStages)

    for stage in testlauncher.stagesMethod:
        stage()
        testlauncher.run()
        testlauncher.wait()
        tr = testlauncher.checkTestResult()
        timerecord.addTimeStamp(stage.__name__)
        # if tr != "Successful":
        #     break
        if tr == "Reach Time Limit of Case":
            break
        # Used for unittest
        # if tr != testlauncher.insStages.assertattr:
        #     raise AssertionError
        # logger.debug("{0} Test Result: {1} !".format("=" * 5, "Pass"))
    if hasattr(testlauncher, "quitTECOM"):
        testlauncher.quitTECOM()


if __name__ == "__main__":

    timerecord = sharedlib.Timer()

    logger = sharedlib.Logger(__name__, logLV=logLV)

    if iTestMode == 0:
        processes = sharedlib.ProcessSnapShot()

    print "=" * 100
    main()
    # print "=" * 100

    timerecord.OutputTimeLog()

    sharedlib.closeHdlr(logger)
    sharedlib.findLoggerFilehdlr(globals())

    os.system("copy {0} {0}bak /y".format(r".\testModel\TimeLog.log"))
    os.system("del {} /s /q".format(r".\testModel\TimeLog.log"))

    if iTestMode == 0:
        TestFile_BackUp

        # Test Finish, kill unused process(*.exe)
        processes.killRedundant()
        # Copy "TestCaseFN" folder to C:\work\LOG\TestID
        # Return Test Finish to Django DB
        sharedlib.PyTestLauncher.ReturnTestFinish(os.path.dirname(__file__))
