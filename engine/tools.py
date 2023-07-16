
from envvars import objectEnvVars as EnvVars
from triggers import objectTriggers as Triggers
import string
import random
import requests

#####################################################################

EnvVars.AddExpected("DETECT_LANGUAGE_TOKEN")

#####################################################################

from deep_translator import GoogleTranslator
import detectlanguage # better but restricted by API key
import langdetect # worse but no restrictions

# Note: it's effectively static class but i'm treating it as object with dummy "self"
# Why? Probably no reason, but if at some point i need to remake it as real object with attributes, it will be dealt with already
# And it doesn't change much
class TranslateTools:
    def __init__(self):
        pass
    def __rawTranslate(self, text, src_lang, tgt_lang):
        return GoogleTranslator(source=src_lang, target=tgt_lang).translate(text)
    def DetectLanguage(self, text):
        try:
            return detectlanguage.simple_detect(text)
        except:
            try:
                return langdetect.detect(text)
            except:
                pass
        return 'auto'
    def Translate(self, text, tgt_lang):
        src_lang = self.DetectLanguage(text)
        translated = text
        try:
            if src_lang != tgt_lang:
                translated = self.__rawTranslate(text, src_lang, tgt_lang)
        except:
            pass
        return (src_lang, tgt_lang, translated)
    def EnsureEnglish(self, text):
        output = text
        try:
            output = self.__rawTranslate(text, 'auto', 'en')
        except:
            pass
        return output
    async def translator_status(self):
        pl_text = "Dzisiaj jest piękny dzień. W dni takie jak te, dzieci twojego pokroju..."
        try:
            self.__rawTranslate(pl_text, 'pl', 'en')
            return ( "Translation integration", True, "Unknown" )
        except Exception as e:
            return ( "Translation integration", False, str(e) )
    async def detector_status(self):
        pl_text = "Dzisiaj jest piękny dzień. W dni takie jak te, dzieci twojego pokroju..."
        detect = True if self.DetectLanguage(pl_text) == 'pl' else False
        return ( "Detect language integration", detect, "Unknown" )
    async def Initialise(self): 
        detectlanguage.configuration.api_key = EnvVars["DETECT_LANGUAGE_TOKEN"]

objectTranslateTools = TranslateTools()
Triggers.Get("Initialisation").Add(objectTranslateTools.Initialise)
Triggers.Get("Status").Add(objectTranslateTools.translator_status)
Triggers.Get("Status").Add(objectTranslateTools.detector_status)

#####################################################################

import hashlib

# Note: it's effectively static class but i'm treating it as object with dummy "self"
# Why? Probably no reason, but if at some point i need to remake it as real object with attributes, it will be dealt with already
# And it doesn't change much
class Tools:
    def Success(self, chance):
        return random.random() <= chance
    def DcLinkToMessage(self, guild_id, channel_id, message_id):
        return f"https://discordapp.com/channels/{guild_id}/{channel_id}/{message_id}"
    def DcWrapCode(self, string):
        return f"```{string}```"
    def DcWrapBold(self, string):
        return f"**{string}**"
    def DcWrapItallic(self, string):
        return f"*{string}*"
    def RandomString(self, length):
        return ''.join(random.choices(string.ascii_letters + string.digits, k = length))
    async def DcReply(self, message, text, postprocess = lambda t: t, MentionAuthor = False, DeleteAfter = None):
        for out in self.SegmentText(text):
            await message.reply( postprocess(out), mention_author = MentionAuthor, delete_after = DeleteAfter)
    def IsUrl(self, string):
        try:
            response = requests.get(string)
            return True
        except:
            return False
    def ParseSizeArgs(self, args, default_min, default_max, hard_min, hard_max):
        num_min = default_min
        num_max = default_max
        if len(args) == 1:
            num_max = max(1, int(float(args[0]))) 
        if len(args) == 2:
            min_arg = min(int(float(args[0])), int(float(args[1])))
            max_arg = max(int(float(args[0])), int(float(args[1])))
            num_min = max(1, min_arg) - 1
            num_max = max(1, max_arg)
        num_min = max(num_min, hard_min)
        num_max = min(num_max, hard_max)
        return (num_min, num_max)
    def MD5(self, name):
        encoded = str(name).encode()
        return hashlib.md5(encoded).hexdigest()
    def sha256(self, name):
        encoded = str(name).encode()
        return hashlib.sha256(encoded).hexdigest()
    def ToSeconds(self, seconds=0, minutes=0, hours=0, days=0, weeks=0):
        return seconds + minutes*60 + hours*60*60 + days*24*60*60 + weeks*7*24*60*60
    def Flatten(self, lists):
        return [item for sublist in lists for item in sublist]
    def SegmentText(self,string, length=1980):
        return (string[0+i:length+i] for i in range(0, len(string), length))
        
objectTools = Tools()
