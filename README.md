# Zeke 3 - Pythonic engine for Discord bots
Deals with most of back-end so you can focus on creation of functionality.

---

# Features of engine

- Local environment for each guild saved on remote server
- AES encryption of data
- Custom <i>(tree based)</i> parser for commands
- Object-oriented
- Aliases <i>(macros)</i> to shorten frequently used commands
- Bundles <i>(send multiple commands in one)</i>
- Error handling <i>(logging)</i>
- Status check <i>(test integration with third-party services)</i>
- Translation and language detection
- Automatic loading of ```.py``` files in ```.features/``` subdirectory
- Translation using emojis as example what it can be used for :)

---

# Installation, setup

Created and tested for Python 3.11  
All python packages required are listed in ```requirements.txt```, install them using pip ```install -r requirements.txt```  

Tokens must be included in ```.env``` file in working directory, containing:  
```env
# Required. Your discord's bot token, You can get one at https://discord.com/developers/applications
DISCORD_TOKEN="your token here"
# Required. Your token for dropbox's app. You can get one at https://www.dropbox.com/developers/documentation/python
DROPBOX_TOKEN="your token here"
# Optional. Token for better language detection library. You can get one at https://detectlanguage.com/
DETECT_LANGUAGE_TOKEN="your token here"
# Optional. Number of minutes between saves of database, if unset it will default to 30 minutes
DATA_SAVE_INTERVAL_MIN=number_of_minutes_between_database_save
```
Discord bot must have... all intents enabled.  

Engine requires files ```.salt.dump``` and ```.aeskey.dump``` for encryption. If they don't exist, it will generate them automatically. Don't lose those files or you won't be able to load your data from storage!  

To start, run ```python executable_main.py``` while in the main directory. Project first loads and sets-up all relevenat scripts from ```engine/```, then imports all scripts from ```.features/```. Both those directories are added to ```sys.path``` so it's as-if they were in the same directory.

---

# Introduction, how-to-use

To add a feature, you should create .py file in ```.features/``` directory. It will be automatically loaded on startup and you can "attach" your own code to the main process using ```Triggers```. It may sound complicated so let me show an example

At first, let's load all of important modules. <b>We won't use all of them</b>, but here's import-recipe for you.
```py
from triggers import objectTriggers as Triggers
from triggers import objectTimers as Timers
from triggers import objectGlobalTimers as GlobalTimers
from tools import objectTools as Tools
from tools import objectTranslateTools as TranslateTools
from database import objectDatabase as Database
from cmdparser import objectMainParser as MainParser
from cmdparser import Parser, Command
from envvars import objectEnvVars as EnvVars
from discordbot import DiscordBot
```

Usually first thing within the script is to add some data to default environment of guilds. ```Database.Default``` <i>(type ```GuildEnv```)</i> is default environment which is used to update every existing guild environment. <b>TL:DR if you add something to ```Database.Default``` it will appear in every guild environment, including existing ones</b>.  

Let's take simplified code of ```translate.py```:
```py
Database.Default.Settings.AddDefault("reaction_translator", dict()) # dict[emoji] = tgt_lang
```
Here we create new dictionary ```dict()``` and store it in ```Env``` <i>(from ```guildenv.py```)</i>, inside ```Settings``` part, under name ```reaction_translator```. ```Env``` has three attributes: ```Settings```, ```Data```, ```Temporary```. They're the same except ```Temporary``` is lost on shutdown. <b>All data stored in Database must be pickle-able and MUST NOT contain any reference loops</b>.

Dictionary we've created can be used to store any kind of data. In this scenarion, we will use ```emoji``` <i>(type ```string```)</i> as key and language code as value.

```py
def PartialToFullReaction(PartialEmoji, message):
    for reaction in message.reactions:
        if str(PartialEmoji) == str(reaction): return reaction
    return None

async def on_raw_reaction_add(local_env, payload, PartialEmoji, member, guild, message):
    if message.author.bot: return # Skip if reaction added to bot's message
    if len(message.content) < 4: return # Skip if it's nearly empty message
    reaction = PartialToFullReaction(PartialEmoji, message) # Get full version of partial reaction (those are discord types)
    if reaction and reaction.count > 1: return # Skip if there're more such reactions already added
    emoji = str(PartialEmoji) # Stringify emoji - key for our dictionary
    text = message.content # Get text of the message
    reaction_translator = local_env.Settings.Get("reaction_translator") # get reference to dictionary object
    # local_env.Settings.Set("reaction_translator", reaction_translator) # If your data can't be accessed with a refence (python number, for example) you can set this value later with Env.Set
    if emoji in reaction_translator: # if emoji is programmed to translate message
        tgt_lang = reaction_translator[emoji] # get target language
        (src_lang, _, translated) = TranslateTools.Translate(text, tgt_lang) # Get src_lang, tgt_lang and translated text
        await message.add_reaction(PartialEmoji) # Add reaction with the same emoji, so users can't spam-translate the same message
        await Tools.DcReply(message, translated, postprocess = Tools.DcWrapCode) # send message with translation
Triggers.Get("on_raw_reaction_add").Add(on_raw_reaction_add)
```

This makes ```on_raw_reaction_add``` run every time anyone adds a reaction, even if corresponding message isn't loaded by the bot. <b>Triggers are Zeke's way of expanding functionality</b>; no need to modify engine, you just append your function and Zeke does the rest. More about available triggers and their syntax in separate chapter.  

Above code allows to translate messages with reaction, but there's still missing part: we need to fill ```reaction_translator``` dictionary with data, so it knows which emojis it should react to. Of course, it could be hardcoded but I prefer to make commands so users can fill their translation database on their own. 
```py
async def cmd_add(ctx, args, trail):
    if len(args) != 2: raise RuntimeError("Incorrect arguments. Expected: <emoji> <language>")
    local_env = Database.GetGuildEnv(ctx.guild.id) # Get GuildEnv for this guild
    emoji = args[0]
    lang = args[1]
    reaction_translator = local_env.Settings.Get("reaction_translator")
    if emoji in reaction_translator: raise RuntimeError(f"This emoji is already occupied by '{reaction_translator[emoji]}' language")
    reaction_translator[emoji] = lang
```
Zeke's custom command parser requires function with header ```async func(ctx, args, trail)```. ``ctx`` is of discord's type ```Context```, but both ```args``` and ```trail``` are lists. It works like this: ```zk3 translate add 🇵🇱 pl``` -> ```args = ["🇵🇱", "pl"], trail = ["zk3", "translate", "add"]```. Trail usually isn't very useful, used mostly by built-in command ```"help"```.  

Commands are considered to succeed if executed properly. If ```cmd_add``` doesn't return or returns ```None```/```False```, then Zeke automatically adds 👍 reaction; this can be prevented by returning ```True```. If you wish to give error feedback, raise any exception and Zeke will forward it to the user.  

Once function is created, we must add it to ```MainParser``` somehow. Typically, for features I'm making new instance of ```Parser``` which i fill with commands for given feature, then I add this parser as new command to ```MainParser```
```py
parser = Parser("translate")
parser.Add( Command("add", cmd_add, Help = "Add emoji translation for language.", LongHelp = "Add emoji translation for language.\nSyntax: TRAIL <emoji> <language>") )
#parser.Add( Command("remove", cmd_remove, Help = "Remove emoji translation for language.", LongHelp = "Remove emoji translation for language.\nSyntax: TRAIL <emoji>") )
#parser.Add( Command("list", cmd_list, Help = "Display list of current emojis used in translations.", LongHelp = "Display list of current emojis used in translations.\nSyntax: TRAIL") )
#parser.Add( Command("custom", cmd_custom, Help = "Display list of available custom languages.", LongHelp = "Display list of available custom languages.\nNot real languages obviously.\nSyntax: TRAIL") )
MainParser.Add( Command(parser.Name(), parser, Help = "Setup translation feature", StaticPerms=discord.Permissions.all()) )
```

```Parser(name)``` requires only ```name:string``` to create. ```Command(...)``` is more complicated, it requires: ```name:string, obj:async func(ctx, args,trail) OR Parser, Help = :string, LongHelp = :string, StaticPerms = :discord.Permissions```, although only ```name``` and ```obj``` are strictly required, rest is optional. 

---

# Triggers

Triggers are Zeke's way of expanding functionality - if you want your functionality to react to message being sent, you create such function <i>(coroutine, actually)</i> and add it to corresponding trigger. It's very similar to discord events, but Zeke usually passes additional arguments to trigger calls.  

Here's recipe how to add every type of trigger.  
```py
Triggers.Get("on_dm").Add(func) # async func(message)
Triggers.Get("on_message").Add(func) # async func(local_env, message)
Triggers.Get("on_reaction_add").Add(func) # async func(local_env, reaction, user)
Triggers.Get("on_reaction_remove").Add(func) # async func(local_env, reaction, user)
Triggers.Get("on_raw_reaction_add").Add(func) # async func(local_env, payload, emoji, member, guild, message)
Triggers.Get("on_raw_reaction_remove").Add(func) # async func(local_env, payload, emoji, member, guild, message)
Triggers.Get("on_member_join").Add(func) # async func(local_env, member)
Triggers.Get("on_member_remove").Add(func) # async func(local_env, member)
Triggers.Get("on_guild_join").Add(func) # async func(local_env, guild)
Triggers.Get("on_guild_remove").Add(func) # async func(local_env, guild)
Triggers.Get("on_ready").Add(func) # async func()
```
All triggers and parameters are self explanatory or taken directly from ```discord.py``` so I won't describe them. ```local_env``` is ```GuildEnv``` of server (guild) within which this trigger was called. Also it's worth noting that <b>Zeke ignores messages and reactions sent in DM or by other bots</b>. You can get DMs with ```on_dm``` trigger but given guild-oriented focus of this bot, there's little support for that <i>(f.e. ```Database``` only works with guilds, not DMs)</i>  

There are also strictly Zeke's triggers
```py
Triggers.Get("Initialisation").Add(func) # async func()
Triggers.Get("Status").Add(func) # async func(), returns (name:string, result:bool, err_mess:string)
```
```Initialisation``` is called after the entire engine <i>(especially ```EnvVars```)</i> is initialised. ```Status``` deserves own chapter, but in short: it's used to create status check for given feature <i>(useful to detect and debug problems with 3rd party integrations)</i>

---

# Command Parser

---

# Status check

---

# Security

First of all, I've no education in computer security. I've tried to add encryption to all long-term storage data, but i don't have expertise to verify if the approach taken is actually secure. That being said, let me explain what's in the code.  

Database stores data in dictionary in form ```dict[hash(guild_id)] = GuildEnv()```. Any request for environment of guild not present in this dictionary warrants a request for ```Storage``` to load data from remote storage. If there's no file with data for this guild, new enviroment <i>(copy of ```Database.Default```)</i> is created and returned.  

Data of guild is stored in file named ```hash(guild_id)```. ```hash``` <i>(in all cases)</i> means PBKDF2, which uses guild_id AND random salt <i>(automatically generated and stored in ```.salt.dump``` 24-byte long string of random bytes)</i>. This ensures that, even if connection or the remote storage itself is compromised, you can't even correlate those files to particular discord guilds.  

The data itself is encrypted with ```AES``` algorithm using 24-bytes long key <i>(also automatically generated and stored in ```.aeskey.dump```)</i>. Encryption requires pickle-dumping of data, converting whole ```GuildEnv``` <i>(except ```Temporary``` part)</i> into binary string. SHA256 is used to compute hash of this binary string before encryption. Then, Initialisation Vector (IV) is randomly generated. Finally, binary string of data is encrypted into cipher. Tuple of all three ```(IV, cipher, hash)``` is then again pickle-dumped into binary string - which is returned.  

Decryption pretty much reverses this process, pickle-loading, decrypting and verifying hash. Note that pickle-dumping and pickle-loading is considered <b>INSECURE</b> in python and may run any code on server's machine if your storage is hacked. 
