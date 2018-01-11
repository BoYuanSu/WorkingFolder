try:
    import _winreg
except ImportError:
    import winreg as _winreg


class MDXlib:
    # Not implemented
    pass


subKey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"


def getSoftwareName():
    with _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, subKey) as key:
        KeyInfo = _winreg.QueryInfoKey(key)
        installsoftware = []
        for enum in range(KeyInfo[0]):
            installsoftware.append(_winreg.EnumKey(key, enum))
    return installsoftware


def test(installsoftware):
    record = []
    for softwarename in installsoftware:
        softwareKey = subKey + r"\{}".format(softwarename)
        # print softwareKey
        with _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, softwareKey) as key2:
            keyInfo = _winreg.QueryInfoKey(key2)
            # print keyInfo
            for enum in range(keyInfo[1]):
                tupValue = _winreg.EnumValue(key2, enum)
                if tupValue[0] == "DisplayName" and tupValue[1] == "Moldex3D R16 64-bit":
                    print tupValue
                    record.append(tupValue)
                if len(record) >= 1:
                    if tupValue[1] == "InstallLocation":
                        print tupValue
                        record.append(tupValue)
                        return record

# print test(getSoftwareName())
