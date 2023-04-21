
import log as Log

class Trigger:
    def __init__(self):
        self.__functions = []
    def Add(self, func):
        self.__functions.append(func)
    async def Call(self, caller):
        output = []
        for func in self.__functions:
            try:
                output.append( await caller(func) )
            except Exception as e:
                Log.Regular.Write(e)
        return output
    def _Insert(self, func):
        self.__functions = [func] + self.__functions

class Triggers:
    def __init__(self):
        self.__triggers = dict()
    def Add(self, name):
        if name not in self.__triggers:
            self.__triggers[name] =  Trigger()
    def Get(self, name):
        self.Add(name)
        return self.__triggers[name]

class Timers:
    def __init__(self):
        self.__timers = dict()
    def Add(self, time, func):
        if time not in self.__timers: self.__timers[time] = Trigger()
        self.__timers[time].Add(func)
    def Iterate(self):
        return ( (time, self.__timers[time]) for time in self.__timers )
    
objectTriggers = Triggers()
objectTimers = Timers()
objectGlobalTimers = Timers()
objectTriggers.Add("Initialisation") # async func()
objectTriggers.Add("Status") # async func(), returns (string, boolean, string) <==> (name, value, err_mess) 