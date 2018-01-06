import os
import re


def GetBackUpItemList(backupInfo_Address, label):
    try:
        with open(backupInfo_Address, "r") as backUpInfoFile:
            backUpInfo = backUpInfoFile.read().split('\n')
        startPoint = backUpInfo.index("[{}]".format(label))
        endPoint = backUpInfo.index("[/{}]".format(label))
        backupItemList = backUpInfo[startPoint + 1: endPoint]
        return(backupItemList)
    except Exception:
        return(0)


def BackupTestingResult(backupInfo_Address, ReadVersion_Py, backUplabel, xFileNameLabel):
    # Read the DailyBuild version
    if "Py3" in ReadVersion_Py:
        from ReadMoldexVersion_py34 import AutoReadMoldexVersion
        version = AutoReadMoldexVersion()
    elif "Py2" in ReadVersion_Py:
        from ReadMoldexVersion_py27 import AutoReadMoldexVersion
        version = AutoReadMoldexVersion()

    # Read & check the specific step backup address
    backupItemList = GetBackUpItemList(backupInfo_Address, backUplabel)
    if backupItemList == 0:
        return("BackUp_infomation.ini_path setting | [{}] label_name setting Error !!".format(backUplabel))

    # Read the setting infomation from backupInfo_Address
    with open(backupInfo_Address, "r") as backUpInfoFile:
        backUpInfo = backUpInfoFile.read()
    [ProductLine, TestCaseModule, testCaseName, sourceParentPath, BackupTargetPath] = [
        "ProductLine", "TestCaseModule", "testCaseName", "sourceParentPath", "BackupTargetPath"]
    settingInfo_List = []
    for parameter in [ProductLine, TestCaseModule, testCaseName, sourceParentPath, BackupTargetPath]:
        patten = r"{}.+\".+\"\n".format(parameter)
        parameterLine = re.search(patten, backUpInfo).group()
        parameter = re.search(
            "\".+\"", parameterLine).group().replace("\"", "")
        settingInfo_List.append(parameter)
    [ProductLine, TestCaseModule, testCaseName,
        sourceParentPath, BackupTargetPath] = settingInfo_List

    # Change the default source parent path
    if "sourceParentPath:" in backupItemList[0]:
        patten2 = r"sourceParentPath: \".+\""
        sourceParentPathLine = re.search(patten2, backupItemList[0]).group()
        sourceParentPath = re.search(
            "\".+\"", sourceParentPathLine).group().replace("\"", "")
        del(backupItemList[0])

    # Check if the source parent path exist
    for path in [sourceParentPath, BackupTargetPath]:
        if not os.path.exists(path):
            return ("sourceParentPath | BackupTargetPath setting Error !!")

    # Build the DailyBuild folder under TestCase Module folder
    targetPath_parent = r"{}\{}\{}\{}\{}\{}".format(
        BackupTargetPath, ProductLine, TestCaseModule, version, testCaseName, sourceParentPath.split("\\")[-1])

    # Start backup
    try:
        for backupItem in backupItemList:
            # Pass the empty line in backUplabel
            if backupItem == "":
                pass
            # Check if the backup_address exist
            elif not os.path.exists(backupItem):
                return ("[{}] address Error(some address no exist) !!".format(backUplabel))

            # Case 1: if the backupItem is a file
            if os.path.isfile(backupItem):
                # Build the son_folder path
                singleSourcePath = os.path.dirname(backupItem)
                fileName = os.path.basename(backupItem)
                targetPath_son = os.path.dirname(
                    backupItem).replace(sourceParentPath, "")
                targetPath = targetPath_parent + targetPath_son

                # shutil.copy( backupItem, targetPath)
                os.system("ROBOCOPY \"{}\" \"{}\" /e /lev:1 /xo /nfl /ndl /njh /njs \"{}\"".format(
                    singleSourcePath, targetPath, fileName))

            # Case 2: if the backupItem is a folder
            elif os.path.isdir(backupItem):
                # Build the son_folder path
                targetPath_son = backupItem.replace(sourceParentPath, "")
                if targetPath_son == "":
                    targetPath = targetPath_parent
                else:
                    targetPath = targetPath_parent + targetPath_son

                # Case 2-1: Backup a folder without unwanted key words
                if xFileNameLabel == "":
                    os.system(
                        "ROBOCOPY \"{}\" \"{}\" /e /xo /nfl /ndl /njh /njs".format(backupItem, targetPath))
                # Case 2-2: Backup a folder including unwanted key words
                else:
                    noNeedBackupItem = GetBackUpItemList(
                        backupInfo_Address, xFileNameLabel)
                    if noNeedBackupItem == 0:
                        return("[{}] Unwanted_keywords_label_setting Error !!".format(xFileNameLabel))
                    else:
                        noNeedFile = "/xf"
                        for fileName in noNeedBackupItem:
                            # noNeedFile = noNeedFile +  " " + fileName
                            noNeedFile = "{} \"{}\"".format(
                                noNeedFile, fileName)
                        os.system("ROBOCOPY \"{}\" \"{}\" /e /xo /nfl /ndl /njh /njs {}".format(
                            backupItem, targetPath, noNeedFile))

        return("\"{}\" backup Done.".format(backUplabel))
    except Exception:
        return("\"{}\" backup Failed !!".format(backUplabel))


if __name__ == '__main__':

    backupInfo_Address = r"C:\WorkingFolder\testCase\testModel\backUp_Information.ini"
    ReadVersion_Py = "Py3.4"  # Py2.7
    backUplabel = "Stage_1"
    xFileNameLabel = ""  # xFileName1

    backupPoint = BackupTestingResult(
        backupInfo_Address, ReadVersion_Py, backUplabel, xFileNameLabel)
    print(backupPoint)
