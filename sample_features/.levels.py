
from triggers import objectTriggers as Triggers
from tools import objectTools as Tools
from database import objectDatabase as Database
from cmdparser import objectMainParser as MainParser
from cmdparser import Parser, Command

# NOT REAL FEATURE
# It's just "feature" made for testing

Database.DefaultUser.AddDefault("messages_sent", 0)
async def on_message(local_env, message):
    user_env = Database.GetUserEnv(local_env, message.author.id)
    messages_sent = user_env.Get("messages_sent")
    messages_sent = messages_sent + 1
    user_env.Set("messages_sent", messages_sent)
Triggers.Get("on_message").Add(on_message)

parser = Parser("levels")

async def cmd_list(ctx, args, trail):
    # Get all player nicknames and levels into list -> [ (nick, lvl), (nick, lvl) ... (nick, lvl) ]
    levels = []
    local_env = Database.GetGuildEnv(ctx.guild.id)
    for member in ctx.guild.members:
        user_env = Database.GetUserEnv(local_env, member.id)
        name = member.display_name
        level = user_env.Get("messages_sent")
        if level > 0: levels.append( (name, level) )
    # Sort by level in descending order
    levels.sort( key = lambda item: -item[1] )
    # Create (ugly) message)
    mess = []
    for (name, level) in levels:
        mess.append(f"{name}: {level}")
    await Tools.DcReply(ctx.message, "\n".join(mess), postprocess = Tools.DcWrapCode)
    return True
parser.Add( Command("list", cmd_list, LongHelp="TRAIL what's up?") )
MainParser.Add( Command(parser.Name(), parser) )

async def cmd_save(ctx, args, trail):
    Database.Save()
MainParser.Add( Command("save", cmd_save) )
