# -*- coding: utf-8 -*-
import sys
sys.dont_write_bytecode = True
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


def main():
    """
    Doing main test
    """
    for key, val in globals().items():
        fmt = "{:<20} :: {:<1}"

        if isinstance(val, types.ModuleType):
            print fmt.format(key, val)
        pass


class Run:

    @staticmethod
    def createLoggerFilehdlr():
        print "Create logger handlers"
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


if __name__ == "__main__":
    timerecord = sharedlib.Timer()

    if iTestMode == 0:
        processes = sharedlib.ProcessSnapShot()

    sharedlib.ProcessSnapShot()
    timerecord.addTimeStamp("ProcessSnapShot")

    logger = Run.createLoggerFilehdlr()
    timerecord.addTimeStamp("Creatlogger")

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
