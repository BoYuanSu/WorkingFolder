import sys

sys.dont_write_bytecode = True
try:
    from CommonFiles import sharedlib
except ImportError:
    sys.path.append(r".\CommonFiles")
    import sharedlib

logger = sharedlib.Logger(__name__)

fu = "paulsu"
fp = "123456"
# Set your shared TC Project Suite path and TC Project Name
sharedTCPjsPath = r"..\CommonFiles\TE1by1\ComRunScript\ComRunScript.pjs"
sharedTCPjName = "Prototype"


class Entrance_:

    def __init__(self):
        logger.info("!!!!! class Entrance_ initialized")
