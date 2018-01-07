import sys
sys.dont_write_bytecode = True
try:
    from CommonFiles import sharedlib
except ImportError:
    sys.path.append("C:\WorkingFolder\CommonFiles")
    import sharedlib

logger = sharedlib.Logger(__name__)

# logLV = logging.INFO


class FEAInterface:

    def LaunchMDX3DI2(self):
        try:
            # logger.info( self.LaunchMDX3DI2.__name__)
            pass
            # q.put(0, block=True, timeout=None)
        except Exception:
            # q.put(2, block=True, timeout=None)
            pass

    def CheckOutputFiles(self):
        try:
            # logger.info( self.LaunchMDX3DI2.__name__)
            pass
            # q.put(0, block=True, timeout=None)
        except Exception:
            # q.put(2, block=True, timeout=None)
            pass
