
import os
from dotenv import load_dotenv
from triggers import objectTriggers as Triggers

class EnvVarsParser(dict):
    def __init__(self):
        super().__init__()
        self.__expected = dict() # (key : default_value)
    async def Initialise(self):
        load_dotenv()
        for key in self.__expected:
            self[key] = os.getenv(key) if os.getenv(key) else self.__expected[key]
    def AddExpected(self, key, default = None):
        if key in self.__expected:
            raise RuntimeError(f"{key} already in expected environmental variables")
        self.__expected[key] = default

objectEnvVars = EnvVarsParser()
