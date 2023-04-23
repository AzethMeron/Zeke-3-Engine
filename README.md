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
All python packages required are listed in requirements.txt, install them using pip install -r requirements.txt  

Tokens must be included in ".env" file in working directory, containing:  
DISCORD_TOKEN="your token here"  
DROPBOX_TOKEN="your token here"  
(optional) DETECT_LANGUAGE_TOKEN="your token here"  
Discord bot must have... all intents enabled.  

Engine requires files .salt.dump and .aeskey.dump for encryption. If they don't exist, it will generate them automatically. Don't lose those files or you won't be able to load your data from storage!  
