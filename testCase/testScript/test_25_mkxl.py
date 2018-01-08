T1 = "T1"
T2 = "T2"
T3 = "Test_25_mkxl"
sharedClassName = "Sample"
argsInit = ()
kwargsInit = {}
argsStage = ()
kwargsStage = {}
isCustomStage = True

class TestStage:

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

        self.fn = ""

        # Used for Indentify whether to Check Successful/Failed or not.
        self.isIgnoredTr = False

    def Stage_001_CollectStatsData(self):
        self.mt = "cmd"
        # self.isIgnoredTr = True
        self.fn = "Collect_Net_Data"
        self.tlm = 1
        self.isIgnoredTr = True
        pass

    def Stage_002_WriteStatsData(self):
        self.mt = "openpyxl"
        # self.isIgnoredTr = True
        self.fn = "Write_Stats_Data"
        pass

    def _customStage(self):
        methods = []
        methods.append(self.Stage_001_CollectStatsData)
        methods.append(self.Stage_002_WriteStatsData)
        methods.append(self.Stage_001_CollectStatsData)
        methods.append(self.Stage_002_WriteStatsData)
        return methods
    # def Stage_000_Setup(self):
    #     # Not Implemented
    #     pass

    # def Stage_999_Teardown(self):
    #     # Not Implemented
    #     pass
