T1 = "T1"
T2 = "T2"
T3 = "Test_25_mkxl"
sharedClassName = "Sample"
argsInit = ()
kwargsInit = {}
argsStage = ()
kwargsStage = {}
isCustomStage = True

"""
if the Stages are all the same for your test group(like Solver Function Test)
You can try coding class at your common lib and inherit it
"""


class TestStage:

    def __init__(self):

        # print "initialized test Stage class"

        """
        # shared class name for your own Test Group
        # ex. ../CommonFiles/SAM/samlib.py -> class Sample
        argsInit, kwargsInit for initialized your own class implemented in your shared Class
        """
        self.sharedClassName = sharedClassName
        self.argsInit = argsInit
        self.kwargsInit = kwargsInit

        # Attritubes bellow must be assigned for return Django DB
        self.t1 = T1
        self.t2 = T2
        self.t3 = T3
        self.mt = "Unknown"
        self.isCustomStage = isCustomStage

        """
        Option Attributes and Default Value Below:
        PyTestLauncher will auto reset to default when Stage end

        Used for indentify whether to check Successful/Failed or not. for continue run next stages
        self.isIgnoredTr = False
        Used for setting time limit of the stage. when reaching time limit, PyTestLauncher auto stop running the stage
        self.tlm = 0
        Function(method) called by PyTestLauncher at the stage
        self.fn = None
        Attritbues fnargs, fnkwargs are used as arguments for sharedclass method
        self.fnargs = () # tuple
        self.fnkwargs = {} # dictionary
        """

        """
        if your want to some Stages (Not All Stages), Setting self.isCustomStage = True
        self.isCustomStage = isCustomStage
        """

    def Stage_001_CollectStatsData(self):
        self.mt = "cmd"
        # self.isIgnoredTr = True
        self.fn = "Collect_Net_Data"
        # self.tlm = 1
        self.fnargs = (1, 2,)
        self.fnkwargs = {"arg3": "arg4"}
        self.assertattr = "Successful"
        pass

    def Stage_002_WriteStatsData(self):
        self.mt = "openpyxl"
        # self.isIgnoredTr = True
        self.fn = "Write_Stats_Data"
        self.assertattr = "Successful"
        pass

    def Stage_UNT1_(self):
        self.mt = "None"
        self.fn = "test_t_r"
        self.tlm = 10
        self.assertattr = "Successful"
        # print("---------------------------------------- assertattr pass")
        pass

    def Stage_UNT2_(self):
        self.mt = "None"
        self.fn = "test_t_r"
        self.tlm = 1
        self.assertattr = "Failed"
        # print("---------------------------------------- assertattr failed")
        pass

    def Stage_UNT3_(self):
        self.mt = "None"
        self.fn = "test_nt_r"
        self.assertattr = "Successful"
        # print("---------------------------------------- assertattr pass")
        pass

    def Stage_UNT4_(self):
        self.mt = "None"
        self.fn = "test_nt_r"
        self.fnkwargs = {"isFailed": True}
        self.assertattr = "Failed"
        # print("---------------------------------------- assertattr failed")
        pass

    def Stage_UNT5_(self):
        self.mt = "None"
        self.isIgnoredTr = True
        self.fn = "test_t_nr"
        self.tlm = 10
        self.assertattr = "Successful"
        # print("---------------------------------------- assertattr pass")
        pass

    def Stage_UNT6_(self):
        self.mt = "None"
        self.isIgnoredTr = True
        self.fn = "test_t_nr"
        self.tlm = 1
        self.assertattr = "Failed"
        # print("---------------------------------------- assertattr failed")
        pass

    def Stage_UNT7_(self):
        self.mt = "None"
        self.isIgnoredTr = True
        self.fn = "test_nt_nr"
        self.assertattr = "Successful"
        # print("---------------------------------------- assertattr pass")
        pass

    def Stage_UNT8_(self):
        self.mt = "None"
        self.isIgnoredTr = True
        self.fn = "test_nt_nr"
        self.assertattr = "Successful"
        # print("---------------------------------------- assertattr pass")
        pass

    def _customStage(self):

        methods = []
        import inspect
        ms = inspect.getmembers(self, inspect.ismethod)
        for m in ms:
            if not m[0].startswith("Stage_"):
                continue
            methods.append(m[1])
        import random
        random.shuffle(methods)
        # methods.append(self.Stage_001_CollectStatsData)
        # methods.append(self.Stage_002_WriteStatsData)
        # methods.append(self.Stage_001_CollectStatsData)
        # methods.append(self.Stage_002_WriteStatsData)
        return methods
    # def Stage_000_Setup(self):
    #     # Not Implemented
    #     pass

    # def Stage_999_Teardown(self):
    #     # Not Implemented
    #     pass
