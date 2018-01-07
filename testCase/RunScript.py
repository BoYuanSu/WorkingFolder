# -*- coding: utf-8 -*-
import sys
sys.dont_write_bytecode = True

import inspect
import os
import types
import logging

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
logLV = logging.INFO
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
    Stages = Run.getStageInstance()


class Run:

    @staticmethod
    def createLoggerFilehdlr():
        print "Create logger handlers"
        logger = logging.getLogger(__name__)
        logger.setLevel(logLV)

        formatter = logging.Formatter("%(asctime)s: %(name)s: %(message)s")
        formatter2 = logging.Formatter("%(message)s")

        file_handler = logging.FileHandler(r".\testModel\TimeLog.log")
        file_handler.setLevel(logLV)
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter2)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        return logger

    @staticmethod
    def closeLoggerFilehdlr():
        print "close logger handlers"

        for name, obj in globals().items():
            if isinstance(obj, types.ModuleType):
                try:
                    for handler in obj.logger.handlers:
                        handler.close()
                except AttributeError:
                    pass

        for hdlr in logger.handlers:
            hdlr.close()
        with open(r".\testModel\TimeLog.log", "a") as log:
            log.write("{0} End log {0}\n".format("=" * 50))

    @staticmethod
    def getStageInstance():
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


if __name__ == "__main__":

    timerecord = sharedlib.Timer()

    logger = Run.createLoggerFilehdlr()
    timerecord.addTimeStamp("Creatlogger")

    if iTestMode == 0:
        processes = sharedlib.ProcessSnapShot()

    sharedlib.ProcessSnapShot()
    timerecord.addTimeStamp("ProcessSnapShot")

    print "=" * 100
    main()
    print "=" * 100

    Run.closeLoggerFilehdlr()
    timerecord.addTimeStamp("Closelogger")

    timerecord.OutputTimeLog()

    if iTestMode == 0:
        TestFile_BackUp

        # Test Finish, kill unused process(*.exe)
        processes.killRedundant()

        # Copy "TestCaseFN" folder to C:\work\LOG\TestID
        # Return Test Finish to Django DB
        sharedlib.ReturnTestFinish(os.path.dirname(__file__))
