
from tools import objectTools as Tools

import copy
import pickle

class Env:
    def __init__(self):
        self.__data = dict()
    def __recursiveDictUpdate(a,b):
        for key in b:
            if key not in a:
                a[key] = copy.deepcopy(b[key])
            else:
                if isinstance(b[key], dict):
                    Env.__recursiveDictUpdate(a[key], b[key])
    def Set(self, key, value):
        self.__data[key] = value
    def Exist(self, key):
        return key in self.__data
    def Get(self, key):
        return self.__data[key]
    def Update(self, default):
        Env.__recursiveDictUpdate(self.__data, default.__data)
    def AddDefault(self, key, value = None):
        if key in self.__data:
            raise RuntimeError(f"{key} already in default guild environment")
        self.Set(key, value)

class GuildEnv:
    def __init__(self):
        self.Data = Env()
        self.Settings = Env()
        self.Temporary = Env()
        self._Users = Env()
    def Update(self, default):
        self.Data.Update(default.Data)
        self.Settings.Update(default.Settings)
        self.Temporary.Update(default.Temporary)
    def Pickle(self):
        tmp = self.Temporary
        self.Temporary = Env()
        data = pickle.dumps(self, -1)
        self.Temporary = tmp
        return data
    def Unpickle(dump):
        return pickle.loads(dump)