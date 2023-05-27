from tools import objectTools as Tools
import os
import shutil
from constants import TEMP_DIR

class TempObject:
    def __init__(self, path, manager):
        self.__manager = manager
        self.__path = path
        self.__manager._Reference(self.__path)
    def __del__(self):
        self.Remove()
        self.__manager._Dereference(self.__path)
    def Path(self):
        return self.__path
    def Remove(self):
        if os.path.exists(self.Path()):
            os.remove(self.Path())

class TempManager:
    def __init__(self, dirname):
        self.__claimed = set()
        self.__directory = dirname
        shutil.rmtree(self.__directory, ignore_errors=True)
    def __del__(self):
        shutil.rmtree(self.__directory, ignore_errors=True)
    def _Reference(self, path):
        self.__claimed.add(path)
    def _Dereference(self, path):
        self.__claimed.remove(path)
    def New(self):
        if not os.path.exists(self.__directory): os.mkdir(self.__directory)
        for i in range(1,100):
            fname = Tools.RandomString(24)
            path = os.path.join(self.__directory, fname)
            if path in self.__claimed: continue
            return TempObject(path, self)
        raise RuntimeError("Couldn't create new temporary file within 100 trials")

objectTempManager = TempManager(TEMP_DIR)