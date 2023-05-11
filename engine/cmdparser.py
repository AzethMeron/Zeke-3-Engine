
from emoji import objectEmoji as Emoji
from triggers import objectTriggers as Triggers
from discordbot import DiscordBot
from database import objectDatabase as Database
import log as Log
import discord
from fuzzywuzzy import fuzz
from tools import objectTools as Tools

#####################################################################################################

from constants import PREFIX

# KEYWORDS FOR HELP
# NAME - name of command
# TRAIL - all of names of commands up to this point ("zeke music play" -> TRAIL=["zeke", "music", "play"])

class Command:
    def __init__(self, Name, obj, Help = "TODO", LongHelp = None, StaticPerms = discord.Permissions.none(), DynamicPerms = lambda ctx: True):
        self.obj = obj # Might be function(ctx, args, trail) or Parser
        self.Name = Name # String
        self.Help = Help 
        self.LongHelp = LongHelp if LongHelp else Help
        self.StaticPerms = StaticPerms # Must be met in order to get access
        self.DynamicPerms = DynamicPerms # Can be used to restrict, but not to allow
        # command can be accessed when both StaticPerms and DynamicPerms are met

class Parser:
    def __init__(self, Name):
        self.__commands = dict()
        self.__name = Name
        self.Add( Command("help", self.HelpCmd, Help = "Access help of given command", LongHelp = "Access help of given command\nSyntax: TRAIL <command> - access help about given command") ) 
    def __PermissionCheck(self, ctx, trail, command, author):
        role_check = admin_role_check(ctx, trail, author)
        static_check = author.guild_permissions >= command.StaticPerms
        dynamic_check = command.DynamicPerms(ctx)
        return (static_check and (dynamic_check or role_check))
    def __BinaryPermssionCheck(self, ctx, trail, command, author):
        try:
            return self.__PermissionCheck(ctx, trail, command, author)
        except:
            return False
    def __GetSimilarCommands(self, ctx, trail, cmd, author):
        commandNames = [ cmd for cmd in self.__commands if self.__BinaryPermssionCheck(ctx, trail, self.__commands[cmd], author) ]
        commandNames.sort(key = lambda x: -fuzz.ratio(x, cmd))
        return commandNames
    def Name(self):
        return self.__name
    def Help(self, ctx, args, trail):
        if len(args) >= 1: # parametrized
            next_cmd = args.pop(0)
            trail.append(next_cmd)
            if next_cmd not in self.__commands:
                similar = self.__GetSimilarCommands(ctx, trail, next_cmd, ctx.message.author)
                raise RuntimeError(f"Command {next_cmd} not found. Did you mean {similar[0]}")
            command = self.__commands[next_cmd]
            if type(command.obj) == Parser: # help parser
                return command.obj.Help(ctx, args, trail)
            else: # help command
                mess = command.LongHelp.replace("TRAIL", ' '.join(trail))
                mess = mess.replace("NAME", next_cmd)
                return mess
        else: # Not parametrized, parser help
            availableCommands = [ cmd for cmd in self.__commands if self.__BinaryPermssionCheck(ctx, trail, self.__commands[cmd], ctx.message.author) ]
            availableCommands.sort()
            admin_role = get_admin_role(ctx, trail, author)
            mess = ["Syntax: " + ' '.join(trail) + " <command>"]
            if admin_role: mess.append(f"Priviledged role: {admin_role.mention}")
            for cmd in availableCommands:
                Command = self.__commands[cmd]
                mess.append('{0: <10}'.format(cmd) + Command.Help)
            return "\n".join(mess)
    async def HelpCmd(self, ctx, args, trail):
        await Tools.DcReply(ctx.message, mess, lambda t: Tools.DcWrapCode(t), DeleteAfter = None)        mess = self.Help(ctx, args, trail)
        return True
    def Add(self, command):
        name = command.Name
        if name in self.__commands:
            raise RuntimeError(f"{cmd} already present in parser {self.Name}")
        self.__commands[name] = command
    async def __call__(self, ctx, args, trail):
        return await self.Call(ctx, args, trail)
    async def Call(self, ctx, args, trail):
        if len(args) == 0: raise RuntimeError('No command specified. Try "help"')
        trail.append( self.Name() )
        cmd = args.pop(0)
        if cmd not in self.__commands:
            similar = self.__GetSimilarCommands(ctx, trail, cmd, ctx.message.author)
            raise RuntimeError(f'Command "{cmd}" not found. Did you mean "{similar[0]}"?')
        command = self.__commands[cmd]
        if self.__PermissionCheck(ctx, trail, command, ctx.message.author): # check both requirements
            return await command.obj(ctx, args, trail)
        else:
            raise RuntimeError("Insufficent permissions")

objectMainParser = Parser(PREFIX)

#####################################################################################################
# Aliases 

from constants import ALIAS_SPECIAL_CHAR
Database.Default.Settings.AddDefault("aliases", dict())

def ParseAliases(local_env, content):
    aliases = local_env.Settings.Get("aliases")
    output = []
    for token in content:
        if token in aliases:
            output.extend( aliases[token] )
        else:
            output.append( token )
    return output

async def cmd_alias_add(ctx, args, trail):
    if len(args) < 2: raise RuntimeError(f"Not enough arguments, required: {ALIAS_SPECIAL_CHAR}<alias> <commands>")
    aliases = Database.GetGuildEnv(ctx.guild.id).Settings.Get("aliases")
    if args[0][0] != ALIAS_SPECIAL_CHAR: raise RuntimeError(f"Addition of alias requires leading {ALIAS_SPECIAL_CHAR}")
    alias = args[0][1:]
    if alias == PREFIX: raise RuntimeError(f"Cannot override {alias}")
    for item in args[1:]: 
        if item in aliases: 
            raise RuntimeError("Aliases cannot refer to another alias")
    command = args[1:]
    aliases[alias] = command
    
async def cmd_alias_remove(ctx, args, trail):
    if len(args) < 1: raise RuntimeError(f"Not enough arguments, required: {ALIAS_SPECIAL_CHAR}<alias>")
    aliases = Database.GetGuildEnv(ctx.guild.id).Settings.Get("aliases")
    if args[0][0] != ALIAS_SPECIAL_CHAR: raise RuntimeError(f"Removal of alias requires leading {ALIAS_SPECIAL_CHAR}")
    alias = args[0][1:]
    if alias not in aliases: raise RuntimeError(f'There is no "{alias}" alias. Maybe you forgot about leading {ALIAS_SPECIAL_CHAR}?')
    del aliases[alias]

async def cmd_alias_list(ctx, args, trail):
    aliases = Database.GetGuildEnv(ctx.guild.id).Settings.Get("aliases")
    output = ["Created aliases:"]
    for alias in aliases:
        command = ' '.join(aliases[alias])
        output.append(f"{alias} -> {command}")
    await Tools.DcReply(ctx.message, "\n".join(output), postprocess = Tools.DcWrapCode, DeleteAfter = None)
    return True

aliasParser = Parser("alias")
aliasParser.Add( Command("add", cmd_alias_add, Help = "Create alias", LongHelp = f"Create alias (macro) for command.\nThis can be used to replace prefix, or as fast way to use common command.\n\nSyntac:\nTRAIL $<alias> <command> - now you can type in <alias> to run <command>.\nNote that you must use leading {ALIAS_SPECIAL_CHAR} to create/remove aliases, but then you omit it in usage.\nExample: TRAIL zk {PREFIX} - now you can use zk instead of {PREFIX} to use commands.", StaticPerms = discord.Permissions.all()) ) 
aliasParser.Add( Command("remove", cmd_alias_remove, Help ="Remove existing alias", LongHelp = f"Remove alias.\n\nSyntax: TRAIL $<alias>\nNote that you must use leading {ALIAS_SPECIAL_CHAR} to create/remove aliases, but then you omit it in usage.", StaticPerms = discord.Permissions.all()) ) 
aliasParser.Add( Command("list", cmd_alias_list, Help = "Display existing macros", LongHelp = "Display existing macros\n\nTRAIL") ) 
objectMainParser.Add( Command(aliasParser.Name(), aliasParser, Help = "Manage aliases (macros) for commands") )

#####################################################################################################

async def on_message(local_env, message):
    if len(message.content) > 0: 
        if message.content[0] == ALIAS_SPECIAL_CHAR: 
            content = message.content[1:].split()
        else:
            content = message.content.split()
            content = ParseAliases(local_env, content)
        if len(content) >= 1 and content[0] == PREFIX:
            ctx = await DiscordBot.get_context(message)
            args = content[1:] 
            trail = []
            try:
                feedback = await objectMainParser.Call(ctx, args, trail)
                if not feedback: await message.add_reaction( Emoji.Get("ThumbUp") )
            except Exception as e:
                Log.WIP.Write(e)
                await Tools.DcReply(message, str(e), DeleteAfter = None)
Triggers.Get("on_message").Add(on_message)

#####################################################################################################
# Bundle - warning, this feature may get buggy when combined with aliases. Shouldn't, but might.

from constants import BUNDLE_SPECIAL_CHAR

async def cmd_bundle(ctx, args, trail):
    local_env = Database.GetGuildEnv(ctx.guild.id)
    original_content = ctx.message.content
    commands = (" ".join(args)).split(BUNDLE_SPECIAL_CHAR)
    for cmd in commands:
        ctx.message.content = cmd
        await on_message(local_env, ctx.message)
    ctx.message.content = original_content
    return True
    
objectMainParser.Add( Command("bundle", cmd_bundle, Help = "Execute multiple commands in one go", LongHelp = "Execute multiple commands in one go.\nSyntax: TRAIL <command> ; <command> ; ... ; <command>\nTo separate commands, use ';' character.\nDo not use aliases in bundles please.") )

#####################################################################################################
# Admin role

Database.Default.Settings.AddDefault("admin_roles", dict()) # dict[' '.join(subtrail)] = admin_role_id
def admin_role_check(ctx, trail, author):
    local_env = Database.GetGuildEnv(ctx.guild.id)
    admin_roles = local_env.Settings.Get("admin_roles")
    for index in range (1, len(trail)):
        key = ' '.join(trail[:index])
        if key in admin_roles:
            role_id = admin_roles[key]
            if author.get_role(role_id):
                return True
    return False
def get_admin_role(ctx, trail, author):
    local_env = Database.GetGuildEnv(ctx.guild.id)
    admin_roles = local_env.Settings.Get("admin_roles")
    key = ' '.join(rail)
    if key not in admin_roles: return None
    role_id = admin_roles[key]
    return ctx.guild.get_role(role_id)
async def cmd_admin_role(ctx, args, trail):
    local_env = Database.GetGuildEnv(ctx.guild.id)
    admin_roles = local_env.Settings.Get("admin_roles")
    key = ' '.join(rail)
    if len(ctx.message.role_mentions) == 0: 
        del admin_roles[key]
    else:
        admin_roles[key] = ctx.message.role_mentions[0].id
objectMainParser.Add( Command("admrole", cmd_admin_role) )