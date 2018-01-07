import sys
import traceback
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
        self.message = ">>> {} !!!".format(msg)
        logger.error(msg)
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
            logger.info(self.Collect_Net_Data.__name__)
            q.put(0, block=True)
            pass
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
            q.put(2, block=True)
            pass

    def Write_Stats_Data(self):
        try:
            logger.info(self.Write_Stats_Data.__name__)
            q.put(0, block=True)
            pass
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
            q.put(2, block=True)
            pass
