T1 = "T1"
T2 = "T2"
T3 = "Test_01_Ansys"
sharedClassName = "FEAInterface"
argsInit = ()
kwargsInit = {}
argsStage = ()
kwargsStage = {}
isCustomStage = True

"""
if the Stages are all the same for your test group(like Solver Function Test)
You can try coding class at your common lib and inherit it
"""


class ComTestStage:

    def __init__(self):
        print "initialized test Stage class"
        """
        # shared class name for your own Test Group
        # ex. ../CommonFiles/SAM/samlib.py -> class Sample
        """
        self.sharedClassName = "Sample"
        """
        if your want to some Stages (Not All Stages), Setting self.isCustomStage = True
        """
        # self.isCustomStage = isCustomStage
        """
        Initial *args, **kwargs for initialized your own class implemented in your shared Class
        """
        # self.argsInit = argsInit
        # self.kwargsInit = kwargsInit
        # attritubes for return Django DB

        # Attritubes Bellow Must be setted
        self.t1 = T1
        self.t2 = T2
        self.t3 = T3
        self.mt = ""

        self.tlm = 0

        # Used for Indentify whether to Check Successful/Failed or not.
        self.isIgnoredTr = False

    def Stage_001_LaunchMDX3DI2(self):
        self.mt = "cmd"
        # self.isIgnoredTr = True
        self.fn = "LaunchMDX3DI2"
        # self.tlm = 1
        # self.isIgnoredTr = True
        pass

    def Stage_002_CheckOutputFiles(self):
        self.mt = "CheckOutputFiles"
        # self.isIgnoredTr = True
        self.fn = "CheckOutputFiles"
        pass

    def _customStage(self):
        methods = []
        methods.append(self.Stage_001_CollectStatsData)
        methods.append(self.Stage_002_WriteStatsData)
        methods.append(self.Stage_001_CollectStatsData)
        methods.append(self.Stage_002_WriteStatsData)
        return methods
