from sys import stdout

debugFile = "parisdebug.txt"

def Dump(pairs):
    if len(pairs) == 0:
        return

    data = ""
    for x in pairs.iterkeys():
        data += "%" + x + ":" + pairs[x] + "%"

    file = open(debugFile, "w")
    file.write(data)
    file.close()


def DumpStr(data):
    file = open(debugFile, "w")
    file.write(data)
    file.close()


def RestoreParis(defaultReturnDict):
    """Load a set of key/value pairs from the plain text debugFile"""

    data = ""
    try:
        with open(debugFile, "r") as file:
                data = file.read()
    except  IOError:
        stdout.write("No file found\n\n")
        return defaultReturnDict
        
    if len(data) == 0:
        return defaultReturnDict

    data = "".join(data.split())
    kvstrings = data.split("%")
    kvstrings = filter(None, kvstrings)

    pairs = {}
    for x in kvstrings:
        kv = x.split(":")
        pairs[kv[0]] = kv[1]

    return pairs


def ReadFrom(location):
    data = ""
    try:
        with open(location, "r") as file:
                data = file.read()
    except  IOError:
        stdout.write("No file found\n\n")
        return ""

    return data


def WriteTo(location, data):
    with open(location, "w") as file:
                file.write(data)