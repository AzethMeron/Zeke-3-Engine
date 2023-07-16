import discord # Discord API
from discord.ext import tasks
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, CommandNotFound
from triggers import objectTriggers as Triggers
from triggers import objectTimers as Timers
from triggers import objectGlobalTimers as GlobalTimers
from database import objectDatabase as Database
from envvars import objectEnvVars as EnvVars
from constants import PREFIX, SECONDS_COUNTER_RESET
import log as Log

####################################################################

EnvVars.AddExpected("DISCORD_TOKEN")

####################################################################

intents = discord.Intents.all()
intents.members = True
DiscordBot = commands.Bot(command_prefix="unused",intents=intents) # create client of discord-bot

######################### CONNECT #########################

def Connect(bot):
    print("Connecting...")
    bot.run(EnvVars["DISCORD_TOKEN"])

######################### TIMERS #########################

second = 1
@tasks.loop(seconds=1)
async def timer():
    global second
    await TimerTick(second, DiscordBot)
    second = (second + 1) % SECONDS_COUNTER_RESET
    
async def TimerTick(second, DiscordBot):
    for (t, trigger) in GlobalTimers.Iterate():
        if (second % t) == 0:
            await trigger.Call(lambda func: func(second))
    for (t, trigger) in Timers.Iterate():
        if (second % t) == 0:
            for guild in DiscordBot.guilds:
                local_env = Database.GetGuildEnv(guild.id)
                await trigger.Call(lambda func: func(local_env, guild, second))

######################### ERROR #########################

@DiscordBot.event
async def on_error(event, *args, **kwargs):
    Log.Fatal.Write(event)
    
######################### DISCORD TRIGGERS #########################

Triggers.Add("on_message") # async func(local_env, message)
Triggers.Add("on_dm") # async func(message)
@DiscordBot.event
async def on_message(message):
    if message.author.bot: return
    if not message.guild:
        await Triggers.Get("on_dm").Call( lambda func: func(message) )
    else:
        local_env = Database.GetGuildEnv(message.guild.id)
        await Triggers.Get("on_message").Call( lambda func: func(local_env, message) ) 
    
Triggers.Add("on_reaction_add") # async func(local_env, reaction, user)
@DiscordBot.event
async def on_reaction_add(reaction, user):
    if user.bot: return 
    if not reaction.message.guild: return
    local_env = Database.GetGuildEnv(reaction.message.guild.id)
    await Triggers.Get("on_reaction_add").Call( lambda func: func(local_env, reaction, user) )

Triggers.Add("on_reaction_remove") # async func(local_env, reaction, user)
@DiscordBot.event
async def on_reaction_remove(reaction, user):
    if user.bot: return 
    if not reaction.message.guild: return
    local_env = Database.GetGuildEnv(reaction.message.guild.id)
    await Triggers.Get("on_reaction_remove").Call( lambda func: func(local_env, reaction, user) )

Triggers.Add("on_raw_reaction_add") # async func(local_env, payload, emoji, member, guild, message)
@DiscordBot.event
async def on_raw_reaction_add(payload):
    if not payload.guild_id: return
    guild = DiscordBot.get_guild(payload.guild_id)
    local_env = Database.GetGuildEnv(guild.id)
    member = guild.get_member(payload.user_id)
    if member.bot: return
    emoji = payload.emoji
    message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
    await Triggers.Get("on_raw_reaction_add").Call( lambda func: func(local_env, payload, emoji, member, guild, message) )

Triggers.Add("on_raw_reaction_remove") # async func(local_env, payload, emoji, member, guild, message)
@DiscordBot.event
async def on_raw_reaction_remove(payload):
    if not payload.guild_id: return
    guild = DiscordBot.get_guild(payload.guild_id)
    local_env = Database.GetGuildEnv(guild.id)
    member = guild.get_member(payload.user_id)
    if member.bot: return
    emoji = payload.emoji
    message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
    await Triggers.Get("on_raw_reaction_remove").Call( lambda func: func(local_env, payload, emoji, member, guild, message) )

Triggers.Add("on_member_join") # async func(local_env, member)
@DiscordBot.event
async def on_member_join(member):
    local_env = Database.GetGuildEnv(member.guild.id)
    await Triggers.Get("on_member_join").Call( lambda func: func(local_env, member) )

Triggers.Add("on_member_remove") # async func(local_env, member)
@DiscordBot.event
async def on_member_remove(member):
    local_env = Database.GetGuildEnv(member.guild.id)
    await Triggers.Get("on_member_remove").Call( lambda func: func(local_env, member) )

Triggers.Add("on_guild_join") # async func(local_env, guild)
@DiscordBot.event
async def on_guild_join(guild):
    local_env = Database.GetGuildEnv(guild.id)
    await Triggers.Get("on_guild_join").Call( lambda func: func(local_env, guild) )

Triggers.Add("on_guild_remove") # async func(local_env, guild)
@DiscordBot.event
async def on_guild_remove(guild):
    local_env = Database.GetGuildEnv(guild.id)
    await Triggers.Get("on_guild_remove").Call( lambda func: func(local_env, guild) )

Triggers.Add("on_ready") # async func()
@DiscordBot.event
async def on_ready():
    timer.start()
    print("Initialisation finished")
    print(f'{DiscordBot.user} has connected to Discord!')
    print("Number of servers (guilds) bot is connected to: "+str(len(DiscordBot.guilds)))
    await DiscordBot.change_presence(activity=discord.Game(name=f"{PREFIX} help"))
    await Triggers.Get("on_ready").Call( lambda func: func() )
