# Zeke 3 - Pythonic engine for Discord bots
Deals with most of back-end so you can focus on creation of functionality.

# Features of engine

- Local environment of each guild saved on remote server (Dropbox, easy to reprogram to support any other platform)
- AES encryption of data (more on that later!)
- Custom (tree based) parser for commands
- Object-oriented
- Aliases (macros) to shorten frequently used commands
- Bundles (send multiple commands in one)
- Error handling (logging)
- Status check (test integration with third-party services)
- Translation and language detection
- Automatic loading of .py files in .features/ subdirectory
- Translation using emojis as example what it can be used for :)

# Setup

Created and tested for Python 3.11  
All python packages required are listed in ```requirements.txt```, install them using pip ```install -r requirements.txt```  

Tokens must be included in ".env" file in working directory, containing:  
```
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

# How to use

To add a feature, you should create .py file in ```.features/``` directory. It will be automatically loaded on startup and you can "attach" your own code to the main process using ```Triggers```. It may sound complicated so let me show an example

At first, let's load all of important modules. <b>We won't use all of them</b>, but here's import-recipe for you.
```py
from triggers import objectTriggers as Triggers
from triggers import objectGlobalTimers as GlobalTimers
from triggers import objectTimers as Timers
from tools import objectTools as Tools
from database import objectDatabase as Database
from cmdparser import objectMainParser as MainParser
from cmdparser import Parser, Command
from envvars import objectEnvVars as EnvVars
from discordbot import DiscordBot
```

Usually first thing within the script is to add some data to default environment of guilds. ```Database.Default``` (type ```GuildEnv```) is default environment which is used to update every existing guild environment. <b>TL:DR if you add something to ```Database.Default``` it will appear in every guild environment, including existing ones</b>.  



# Security

First of all, I've no education in computer security. I've tried to add encryption to all long-term storage data, but i don't have expertise to verify if the approach taken is actually secure. That being said, let me explain what's in the code.  

Database stores data in dictionary in form ```dict[hash(guild_id)] = GuildEnv()```. Any request for environment of guild not present in this dictionary warrants a request for ```Storage``` to load data from remote storage. If there's no file with data for this guild, new enviroment (cop of ```default```) is created and returned.  

Data of guild is stored in file named ```hash(guild_id)```. ```hash``` (in all cases) means PBKDF2, which uses guild_id AND random salt (automatically generated and stored in ```.salt.dump``` 24-byte long string of random bytes). This ensures that, even if connection or the remote storage itself is compromised, you can't even correlate those files to particular discord guilds.  

The data itself is encrypted with ```AES``` algorithm using 24-bytes long key (also automatically generated and stored in ```.aeskey.dump```). Encryption requires pickle-dumping of data, converting whole ```GuildEnv``` (except ```Temporary``` part) into binary string. SHA256 is used to compute hash of this binary string before encryption. Then, Initialisation Vector (IV) is randomly generated. Finally, binary string of data is encrypted into cipher. Tuple of all three ```(IV, cipher, hash)``` is then again pickle-dumped into binary string - which is returned.  

Decryption pretty much reverses this process, pickle-loading, decrypting and verifying hash. Note that pickle-dumping and pickle-loading is considered <b>INSECURE</b> in python and may run any code on server's machine if your storage is hacked. 

# aaa
