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

q = Queue.Queue(maxsize=1)


class Error(Exception):

    def __init__(self, msg=""):
        self.message = "{0} {1} ...".format("!" * 5, msg)
        logger.error(self.message)
        q.put(2, block=True)

    def __str__(self):
        return repr(self.message)


class CopyDataError(Error):
    def __init__(self):
        Error.__init__(self, "Copy Failed")


class MonitorError(Error):
    def __init__(self):
        Error.__init__(self, "Only Monitor Case Submitted")


class Sample:

    def __init__(self):
        logger.info("cls Sample initialized")
        pass

    def Collect_Net_Data(self):
        try:
            time.sleep(5)
            # raise CopyDataError
            q.put(0, block=False)
            pass
        except (CopyDataError,):
            pass
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
            q.put(2, block=False)
            pass

    def Write_Stats_Data(self):
        try:
            time.sleep(5)
            q.put(0, block=False)
            print "Put Q = 0 at Write_Stats_Data"
            pass
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
            q.put(2, block=False)
            print "Put Q = 2 at Write_Stats_Data"
            pass
