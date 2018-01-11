import sys

sys.dont_write_bytecode = True
sys.dont_write_bytecode = True
try:
    from CommonFiles import sharedlib
except ImportError:
    sys.path.append("C:\WorkingFolder\CommonFiles")
    import sharedlib

logger = sharedlib.Logger(__name__)

fu = "paulsu"
fp = "123456"
# Set your shared TC Project Suite path and TC Project Name
sharedTCPjsPath = r"C:\WorkingFolder\CommonFiles\TEALL\ComRunScript\ComRunScript.pjs"
sharedTCPjName = "Prototype"


class Entrance:

    def __init__(self):
        logger.info("!!!!! class Sample initialized")
        """
        This attribute is for checking whether to run all routines in TC unit script or not.
        If you want to run routines automatically, set it True.
        You can also would not set any attribute, Test Launcher will set it False by debault.
        """
        self.isRunAllRoutines = True
