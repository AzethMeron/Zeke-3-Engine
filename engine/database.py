
from guildenv import GuildEnv, Env
from envvars import objectEnvVars as EnvVars
from triggers import objectTriggers as Triggers
from triggers import objectGlobalTimers as GlobalTimers
from tools import objectTools as Tools
import aes as AES
import log as Log
from constants import AESKEY_FILENAME

import copy
import pickle

####################################################################

EnvVars.AddExpected("DROPBOX_TOKEN")
EnvVars.AddExpected("DATA_SAVE_INTERVAL_MIN", 30)

####################################################################
# Model for Storage part of database

class Storage:
    def __init__(self): pass
    def Save(self, var, path): pass
    def Load(self, path): pass
    def Exist(self, path): pass
    def Remove(self, path): pass
    async def Initialise(self): pass
    def Initialised(self): pass
    async def Status(self): pass

####################################################################
# If you want to use Dropbox as storage (like i do) you may use this class

import dropbox
class Dropbox(Storage):
    def __init__(self):
        self.__dbx = None 
    async def Initialise(self):
        self.__dbx = dropbox.Dropbox(EnvVars['DROPBOX_TOKEN'])
    def __hash(path):
        return Tools.sha256(path)
    def __raw_send(self, var, hashedpath):
        data = pickle.dumps(var, -1)
        self.__dbx.files_upload(data, '/' + hashedpath, mute=True, mode=dropbox.files.WriteMode.overwrite)
    def __raw_get(self, hashedpath):
        f, r = self.__dbx.files_download('/' + hashedpath)
        return pickle.loads(r.content)
    def __raw_exist(self, hashedpath):
        try:
            self.__dbx.files_get_metadata('/' + hashedpath)
            return True
        except:
            return False
    def __raw_remove(self, hashedpath):
        self.__dbx.files_delete('/' + hashedpath)
    def Initialised(self):
        if self.__dbx: return True
        return False
    def Save(self, var, path):
        hashedpath = Dropbox.__hash(path)
        try:
            self.__raw_send(var, hashedpath)
            return True
        except Exception as e:
            Log.Regular.Write(e)
    def Load(self, path):
        hashedpath = Dropbox.__hash(path)
        try:
            return self.__raw_get(hashedpath)
        except Exception as e:
            Log.Regular.Write(e)
    def Exist(self, path):
        hashedpath = Dropbox.__hash(path)
        return self.__raw_exist(hashedpath)
    async def __raw_status(self):
        data = Tools.RandomString(10)
        filename = Tools.RandomString(5)
        try:
            self.__raw_send(data, filename)
            recv = self.__raw_get(filename)
            self.__raw_remove(filename)
            if data == recv: return (True, "")
            else: return (False, "Unknown")
        except Exception as e:
            return (False, str(e))
    async def Status(self):
        status, err = await self.__raw_status()
        return ("Storage Integration", status, err)

####################################################################
# Database

class Database:
    def __init__(self):
        self.__guilds = dict()
        self.__storage = Dropbox()
        self.__aesKey = None
        self.DefaultUser = Env()
        self.Default = GuildEnv()
    def __hash(guild_id):
        #return Tools.sha256(guild_id)
        return AES.PasswdToKey(str(guild_id))
    def __aeskey(self):
        if not self.__aesKey:
            self.__aesKey = AES.LoadOrGenerateKey(AESKEY_FILENAME, bytelength=24)
        return self.__aesKey
    def GetGuildEnv(self, guild_id):
        key = Database.__hash(guild_id)
        if key not in self.__guilds:
            if not self.__loadOne(key):
                self.__guilds[key] = copy.deepcopy(self.Default)
        return self.__guilds[key]
    def GetUserEnv(self, local_env, user_id):
        key = Database.__hash(user_id)
        if not local_env._Users.Exist(key):
            local_env._Users.Set(key, copy.deepcopy(self.DefaultUser))
        local_env._Users.Get(key).Update(self.DefaultUser)
        return local_env._Users.Get(key)
    def Save(self): # Saves all 
        for key in self.__guilds:
            self.__saveOne(key)
    async def __saveSelf(self):
        self.Save()
    async def Initialise(self):
        GlobalTimers.Add( Tools.ToSeconds(minutes=int(EnvVars["DATA_SAVE_INTERVAL_MIN"])), lambda second: self.__saveSelf() )
        await self.__storage.Initialise()
    def __saveOne(self, key):
        guildenv = self.__guilds[key]
        data = guildenv.Pickle()
        cipher = AES.Encrypt( self.__aeskey(), data)
        self.__storage.Save(cipher, key)
    def __loadOne(self, key): 
        if self.__storage.Exist(key):
            tmp = self.__storage.Load(key)
            if tmp:
                tmp = AES.Decrypt( self.__aeskey(), tmp)
                self.__guilds[key] = GuildEnv.Unpickle(tmp)
                self.__guilds[key].Update(self.Default)
                return True
        return False
    async def Status(self):
        return await self.__storage.Status()

objectDatabase = Database()

Triggers.Get("Initialisation").Add(objectDatabase.Initialise)
Triggers.Get("Status").Add(objectDatabase.Status)