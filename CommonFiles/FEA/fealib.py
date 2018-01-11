import sys
import traceback
import time
import Queue

sys.dont_write_bytecode = True
try:
    from CommonFiles import sharedlib
except ImportError:
    sys.path.append("C:\WorkingFolder\CommonFiles")
    import sharedlib

logger = sharedlib.Logger(__name__)
# logLV = logging.INFO

"""
You can try to code Father class at comstages.py
Then inhenrit it from testScipt/testScript.py
"""
from comstages import ComTestStage

q = Queue.LifoQueue()


# Setting Test Group User Name/Password of Maintainer
fu = "paulsu"
fp = "123456"


class Error(Exception):

    def __init__(self, msg=""):
        self.message = "{0} {1} ...".format("!" * 5, msg)
        logger.error(self.message)
        q.put(2, block=True)

    def __str__(self):
        return repr(self.message)


class MatchDataError(Error):
    def __init__(self):
        Error.__init__(self, "Copy Failed")


class FileSizeError(Error):
    def __init__(self):
        Error.__init__(self, "Only Monitor Case Submitted")


class FEAInterface:

    def __init__(self):
        logger.info("!!!!! class FEAInterface initialized")
        pass

    def LaunchMDX3DI2(self):
        try:
            # raise CopyDataError
            time.sleep(5)
            q.put(0, block=False)
            pass
        except (FileSizeError,):
            pass
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
            q.put(2, block=False)
            pass

    def CheckOutputFiles(self):
        try:
            time.sleep(5)
            # print
            # print q.qsize()
            # print "Put Q = 0 at Write_Stats_Data"
            q.put(0, block=False)
            pass
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
            q.put(2, block=False)
            pass
