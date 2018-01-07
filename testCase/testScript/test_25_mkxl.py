T1 = "T1"
T2 = "T2"
T3 = "Test_25_mkxl"
sharedClassName = "Sample"


class TestStage:

    def __init__(self):
        print "initialized test Stage class"
        # shared class name for your own Test Group
        self.sharedClassName = "Sample"
        # attritubes for return Django DB
        self.t1 = T1
        self.t2 = T2
        self.t3 = T3
        self.mt = ""

        self.tlm = 0

        self.arg = ""
        self.fn = ""

    def Stage_001_CollectStatsData(self):
        # Not Implemented
        pass

    def Stage_003_WriteStatsData(self):
        # Not Implemented
        pass

    def Stage_000_Setup(self):
        # Not Implemented
        pass

    def Stage_999_Teardown(self):
        # Not Implemented
        pass
