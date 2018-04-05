import pyperclip
from Crypto.Cipher import AES
from sys import stdout
from msvcrt import getch
import requests
import json
import re
from itertools import ifilter

# program specific settings, change these
from programcredentials import credentials
# program debug module
from debugmodule import DumpStr, RestoreParis

class program(object):
    def __init__(self):
        self.shouldExit = False
        self.paris = {}
        self.fileLoc = "paris.prjrem"
        self.randomURL = "https://api.random.org/json-rpc/1/invoke"
        self.keywords = ["make", "remove", "overview", "dump", "password", "help", "restoreparis"]
        self.creds = credentials()


    def Run(self):
        self.paris = self.ReadFromFile()

        while self.shouldExit is False:
            cmds = self.ReadKeys().lower().split()
            cc = len(cmds)
            if cc == 0:
                self.PrintOptions()
                continue
            
            if self.IsImportant(cmds[0]):
                if cmds[0] == "make" and cc == 2:
                    self.Make(cmds[1])
                    continue
                if cmds[0] == "make" and cc == 3:
                    self.Make(cmds[1], cmds[2])
                    continue
                if cmds[0] == "remove" and cc == 2:
                    self.Remove(cmds[1])
                    continue
                if cmds[0] == "overview":
                    self.Overview()
                    continue
                if cmds[0] == "help":
                    self.PrintOptions()
                    continue
                if cmds[0] == "restoreparis":
                    self.paris = RestoreParis(self.paris)
                    self.SaveToFile()
                    continue

                self.PrintOptions()
                continue

            if self.paris.has_key(cmds[0]): 
                self.Retrieve(cmds[0])
            else:
                stdout.write("No such key found, type 'help' to get a commandlist\n\n")
                         

    def ReadKeys(self):
        """Input parsing. Intercepts carriage return, escape and backspace. All other keypressses are matched to a regular expression"""

        reg = re.compile(r"\w|\s")
        chars = ""
        while True:
            key = getch()
            keynum = ord(key)

            if keynum == 27: #escape
                self.shouldExit = True
                return ""

            if keynum == 13: #enter
                stdout.write("\n")
                break

            if keynum == 8: #backspace
                chars = chars[:-1]
                stdout.write(key)
                stdout.write(" ")
                stdout.write(key)
                continue

            if reg.match(key): 
                chars += key
                stdout.write(key)

        return chars


    def Retrieve(self, key):
        """Retrieve a password and copy it to the clipboard"""

        pyperclip.copy(self.paris[key])
        pyperclip.paste()
        stdout.write("Password copied to clipboard\n\n")

        
    def GetRandomString(self):
        """Post request to the random.org API and return a randomized string"""

        head = {"content-type": "application/json-rpc"}
        body = {
            "jsonrpc": "2.0",
            "method": "generateStrings",
            "params": [
                self.creds.randomAPIkey,
                3,
                16,
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
            ],
            "id": 42
        }
        response = requests.post(self.randomURL, data=json.dumps(body), headers=head).json()

        try:
            return response["result"]["random"]["data"][1]
        except  KeyError:
            return "error"

    def Encrypt(self, data):
        """Sensitive data comes in, jumbled junk comes out"""

        if len(data) % 16 != 0:
            data += ' ' * (16 - len(data) % 16)
        es = AES.new(self.creds.aesKey, AES.MODE_CBC, self.creds.aesIV)
        return es.encrypt(data)

    def Decrypt(self, data):
        """Gibberish comes in, cool data comes out"""

        es = AES.new(self.creds.aesKey, AES.MODE_CBC, self.creds.aesIV)
        solved = ""
        try:
            solved = es.decrypt(data)
        except  ValueError:
            # Debug, pad out the file before decrypting
            #if len(data) % 16 != 0:
            #    data += ' ' * (16 - len(data) % 16)
            #solved = es.decrypt(data)
            #self.DumpStr(solved)

            stdout.write("Error, cannot decrypt corrupted file. Backup paris.prjrem to avoid overwriting.\n\n")
            return "%errorpass:1234123412341234%"

        return solved


    def ReadFromFile(self):
        """Open the password file, decrypt the string, and populate a dict by parsing the formatted string to key/value pairs"""

        data = ""
        try:
            file = open(self.fileLoc, "r")
            data = file.read()
            file.close()
        except  IOError:
            file = open(self.fileLoc, "w")
            file.close()
            return {}
        
        if len(data) == 0:
            return {}

        data = self.Decrypt(data)

        data = "".join(data.split())
        kvstrings = data.split("%")
        kvstrings = filter(None, kvstrings)

        pairs = {}
        for x in kvstrings:
            kv = x.split(":")
            pairs[kv[0]] = kv[1]

        return pairs


    def SaveToFile(self):
        """Format self.paris to a string, encrypt it, and write to self.fileloc"""

        if len(self.paris) == 0:
            file = open(self.fileLoc, "w")
            file.write("")
            file.close()
            return

        data = ""
        for x in self.paris.iterkeys():
            data += "%" + x + ":" + self.paris[x] + "%"
        
        data = self.Encrypt(data)

        file = open(self.fileLoc, "w")
        file.write(data)
        file.close()


    def Make(self, arg_name, arg_value="make"):
        """Make a new key"""

        if self.IsImportant(arg_name):
            stdout.write("Protected keyword, attempt aborted\n\n")
            return
        
        value = ""
        if arg_value == "make":
            value = self.GetRandomString()
            if value == "error":
                stdout.write("Something went wrong. Could not contact random.org. Sorry\n\n")
                return
        else:
            value = arg_value

        self.paris[arg_name] = value
        self.Retrieve(arg_name)
        self.SaveToFile()


    def Remove(self, arg_name):
        """Remove a key"""

        if self.paris.has_key(arg_name) and self.IsImportant(arg_name) is False:
            self.paris.pop(arg_name)
            self.SaveToFile()
            stdout.write("Removed!\n\n")
        else:
            stdout.write("No such key found\n\n")


    def Overview(self):
        """Prints all passwords"""

        for x in self.paris.iterkeys():
            stdout.write(x + "\n")
        stdout.write("\n")


    def IsImportant(self, key):
        """Compares a statement to the protected keywords"""

        if any(x.lower() == key for x in self.keywords):
            return True
        return False


    def PrintOptions(self):
        stdout.write("Displaying commands\n\n" + 
                             "- make [key]             Creates a new random password and saves it under the specified key\n" + 
                             "- make [key] [value]     Uses specified value as password and saves it under the specified key\n" + 
                             "- remove [key]           Deletes a password under the specified key\n" +
                             "- overview               List all keywords\n" +
                             "- [key]                  Retrieves a password to the clipboard\n\n")
