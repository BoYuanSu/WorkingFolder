import sys
sys.dont_write_bytecode = True
try:
    from CommonFiles import sharedlib
except ImportError:
    sys.path.append("C:\WorkingFolder\CommonFiles")
    import sharedlib

logger = sharedlib.Logger(__name__)
# logLV = logging.INFO


class Error(Exception):

    def __init__(self, msg=""):
        self.message = msg
        logger.error(msg)
        # q.put(2, block=True, timeout=None)
        # Exception.__init__(self, msg)

    def __str__(self):
        return repr(self.message)


class Sample:

    def __init__(self):
        logger.info("cls Sample initialized")
        pass

    def Collect_Net_Data(self):
        try:
            # logger.info(self.Collect_Net_Data.__name__)
            pass
        except Exception:
            pass

    def Write_Stats_Data(self):
        try:
            # logger.info(self.Write_Stats_Data.__name__)
            pass
        except Exception:
            pass



