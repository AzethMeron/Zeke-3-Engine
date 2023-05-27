
import asyncio
import os
import sys
import signal
sys.path.extend( ["engine"] )

# LOADING ENGINE MODULES - SEQUENCE MATTERS! DO NOT CHANGE
from triggers import objectTriggers as Triggers
from envvars import objectEnvVars as EnvVars
from tools import objectTranslateTools as TranslateTools
from tools import objectTools as Tools
from database import objectDatabase as Database
from discordbot import DiscordBot, Connect
from cmdparser import objectMainParser as MainParser

# Engine level "FEATURES" - non-essentials
import status
import features
import temp

# RUNNING THE ENGINE    
def SigtermHandler(*args):
    Database.Save()
    exit()
async def Initialise():
    await EnvVars.Initialise()
    await Triggers.Get("Initialisation").Call( lambda func: func() )
def Main():
    signal.signal(signal.SIGINT, SigtermHandler)
    signal.signal(signal.SIGTERM, SigtermHandler)
    asyncio.run(Initialise())
    Connect(DiscordBot)
if __name__ == "__main__":
    Main()
    