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

q = Queue.LifoQueue()

# Setting Test Group User Name/Password of Maintainer
fbgzUser = "paulsu"
fbgzPassword = "123456"


class Error(Exception):

    def __init__(self, msg=""):
        self.message = "{0} {1} ...".format("!" * 5, "Custom Error Occurred")
        logger.error(self.message)
        q.put(4)

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
        logger.info("!!!!! class Sample initialized")
        pass

    def Collect_Net_Data(self, arg1, arg2, arg3="arg3", arg4="argdefault"):
        try:
            # raise CopyDataError
            logger.info(arg1)
            logger.info(arg2)
            logger.info(arg3)
            logger.info(arg4)
            # time.sleep(5)
            q.put(0)
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

    def test_t_r(self, isFailed=False):
        try:
            time.sleep(3)
            if isFailed:
                raise Error
            q.put(1)
        except Error:
            pass
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
            q.put(5)

            pass

    def test_nt_r(self, isFailed=False):
        try:
            time.sleep(3)
            if isFailed:
                raise Error
            pass
            q.put(0)
        except (Error):
            pass
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
            q.put(4)
            pass

    def test_t_nr(self, isFailed=False):
        try:
            time.sleep(3)
            if isFailed:
                raise Error
            pass
            q.put(2)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
            q.put(4)
            pass

    def test_nt_nr(self, isFailed=False):
        try:
            time.sleep(3)
            if isFailed:
                raise Error
            q.put(3)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
            q.put(4)
            pass
