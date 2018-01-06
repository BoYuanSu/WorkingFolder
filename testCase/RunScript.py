# -*- coding: utf-8 -*-
import sys
import os
sys.path.append("../CommonFiles")
sys.path.append("./testScript")
import sharedlib
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
    timerecord.OutputTimeLog()

    if iTestMode == 0:
        # Test Finish, kill unused process(*.exe)
        processes.killRedundant()
        # Copy "TestCaseFN" folder to C:\work\LOG\TestID
        # Return Test Finish to Django DB
        sharedlib.ReturnTestFinish(os.path.dirname(__file__))


if __name__ == "__main__":
    main()
