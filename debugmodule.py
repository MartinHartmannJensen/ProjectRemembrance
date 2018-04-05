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
        file = open(debugFile, "r")
        data = file.read()
        file.close()
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