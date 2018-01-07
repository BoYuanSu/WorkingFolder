T1 = "T1"
T2 = "T2"
T3 = "Test_25_mkxl"
sharedClassName = "Sample"
argsInit = ()
kwargsInit = {}


class TestStage:

    def __init__(self):
        print "initialized test Stage class"
        # shared class name for your own Test Group
        self.sharedClassName = "Sample"
        # self.argsInit = argsInit
        # self.kwargsInit = kwargsInit
        # attritubes for return Django DB
        self.t1 = T1
        self.t2 = T2
        self.t3 = T3
        self.mt = ""

        self.tlm = 0

        self.fn = ""
        # Used for Indentify Need to Check Successful or Failed
        self.isIgnoredTr = False

    def Stage_001_CollectStatsData(self):
        self.mt = "cmd"
        # self.isIgnoredTr = True
        self.fn = "Collect_Net_Data"
        pass

    def Stage_002_WriteStatsData(self):
        self.mt = "openpyxl"
        # self.isIgnoredTr = True
        self.fn = "Write_Stats_Data"
        pass

    # def Stage_000_Setup(self):
    #     # Not Implemented
    #     pass

    # def Stage_999_Teardown(self):
    #     # Not Implemented
    #     pass
