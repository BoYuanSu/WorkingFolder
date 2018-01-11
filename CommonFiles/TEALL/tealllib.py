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
sharedTCPjsPath = r"C:\WorkingFolder\CommonFiles\TEALL\ComRunScript\ComRunScript.pjs"
sharedTCPjName = "Prototype"


class Entrance:

    def __init__(self):
        logger.info("!!!!! class Sample initialized")
        self.isRunAllRoutines = True
