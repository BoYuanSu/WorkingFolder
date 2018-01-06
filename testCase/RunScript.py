# -*- coding: utf-8 -*-
import sys
import os
sys.dont_write_bytecode = True
os.chdir(os.path.dirname(__file__))
sys.path.append("./testScript")
sys.path.append("..")
from CommonFiles import *
# from PythonScript_SAM import utility, mypycom
# from testScript import TestScript

# For Test Mode Setting(Test or not, 1:Yes, 0:No)
iTestMode = 1


def main():
    if iTestMode == 0:
        processes = sharedlib.ProcessSnapShot()

    timerecord = sharedlib.Timer()

    """
    Doing main test
    """
    for key, val in globals().items():
        print key, "::", val
        pass

    timerecord.OutputTimeLog()

    if iTestMode == 0:
        # Test Finish, kill unused process(*.exe)
        processes.killRedundant()
        # Copy "TestCaseFN" folder to C:\work\LOG\TestID
        # Return Test Finish to Django DB
        sharedlib.ReturnTestFinish(os.path.dirname(__file__))


if __name__ == "__main__":
    main()
