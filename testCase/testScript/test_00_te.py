T1 = "T1"
T2 = "T2"
T3 = "Test_00_te"
sharedClassName = "Entrance"
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

        # Attritubes bellow must be assigned for return Django DB
        self.t1 = T1
        self.t2 = T2
        self.t3 = T3
        self.mt = "Unknown"
        self.unitname = "teself"
        # self.isCustomStage = isCustomStage

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

    def Stage_001_Calculator(self):
        self.mt = "Calculator"
        # self.isIgnoredTr = True
        # self.tlm = 1
        self.un = "teimport"
        self.fn = "teimport.runCalc"
        self.assertattr = "Successful"
        pass

    def Stage_002_Notepad(self):
        self.mt = "Notepad"
        # self.isIgnoredTr = True
        # self.tlm = 1
        self.un = "teself"
        self.fn = "runNotepad"
        self.assertattr = "Successful"
        pass

    def Stage_003_Calculator(self):
        self.mt = "None"
        self.isIgnoredTr = True
        self.un = "teimport"
        self.fn = "runCalc"
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
        return methods
