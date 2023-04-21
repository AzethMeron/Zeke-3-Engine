
from triggers import objectGlobalTimers as GlobalTimers
from triggers import objectTriggers as Triggers
from tools import objectTools as Tools
from cmdparser import objectMainParser as MainParser
from cmdparser import Command
from emoji import objectEmoji as Emoji
from constants import ENGINE_REPO

from datetime import datetime

STATUS_CACHE = None

async def GetStatusMessage():
    results = await Triggers.Get("Status").Call( lambda func: func() )
    operational = [ name for (name, value, errmess) in results if value == True ]
    failed = [ (name, errmess) for (name, value, errmess) in results if value == False ]
    output = [f"ZEKE-BASED BOT\nFree & open source available on: {ENGINE_REPO}\nReport created on: {str(datetime.now())}\n"]
    for name in operational:
        output.append(f"{name}: OK")
    output.append("")
    if len(failed) > 0:
        for (name, errmess) in failed:
            output.append(f"{name}: FAILED (error message: {errmess})")
    else:
        output.append(f"ALL SYSTEMS OPERATIONAL")
    return "\n".join(output)
    
async def CleanCache():
    global STATUS_CACHE
    STATUS_CACHE = None
    
async def cmd_status(ctx, args, trail):
    global STATUS_CACHE
    if not STATUS_CACHE: 
        await ctx.message.add_reaction( Emoji.Get("ThumbUp") )
        STATUS_CACHE = await GetStatusMessage()
    await Tools.DcReply(ctx.message, STATUS_CACHE, postprocess = Tools.DcWrapCode, DeleteAfter = None)
    return True
MainParser.Add( Command("status", cmd_status, Help =  "Check status of integration with third party", LongHelp = "Check status of integration with third party\nSyntax: TRAIL") )
GlobalTimers.Add( Tools.ToSeconds(hours=3), lambda second: CleanCache() )
