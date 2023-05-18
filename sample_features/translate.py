
from triggers import objectTriggers as Triggers
from tools import objectTools as Tools
from tools import objectTranslateTools as TranslateTools
from database import objectDatabase as Database
from cmdparser import objectMainParser as MainParser
from cmdparser import Parser, Command
import discord
import langcodes

################################################################################

default_emojis = dict()
custom_lang = dict()

def AddDefaultTranslation(emoji, langcode):
    default_emojis[emoji] = langcode

def AddCustomTranslation(name, normalisation_code, func, help):
    custom_lang[name] = (normalisation_code, func, help)
 
################################################################################

Database.Default.Settings.AddDefault("reaction_translator", default_emojis) # dict[emoji] = tgt_lang

################################################################################

def GetReactionTranslator(local_env):
    return local_env.Settings.Get("reaction_translator")

def PartialToFullReaction(PartialEmoji, message):
    for reaction in message.reactions:
        if str(PartialEmoji) == str(reaction): return reaction
    return None

async def PostMessage(message, member, translated_text, src_lang, tgt_lang):
    channel = message.channel
    src_lang = langcodes.Language.get(src_lang).display_name()
    if tgt_lang not in custom_lang: tgt_lang = langcodes.Language.get(tgt_lang).display_name()
    embed = discord.Embed(title=f"Translation from {src_lang} to {tgt_lang}", description=translated_text)
    author = message.author
    embed.set_author(name=author.display_name, icon_url=author.display_avatar.url)
    embed.set_footer(text=f"Requested by: {member.display_name}", icon_url=member.display_avatar.url)
    await message.reply(embed=embed, mention_author=False)

async def on_raw_reaction_add(local_env, payload, PartialEmoji, member, guild, message):
    if message.author.bot: return
    if len(message.content) < 4: return
    reaction = PartialToFullReaction(PartialEmoji, message)
    if reaction and reaction.count > 1: return
    emoji = str(PartialEmoji)
    text = message.content
    reaction_translator = GetReactionTranslator(local_env)
    if emoji in reaction_translator:
        tgt_lang = reaction_translator[emoji]
        src_lang = "auto"
        translated = text
        if tgt_lang in custom_lang:
            (normalisation_code, func, _) = custom_lang[tgt_lang]
            (src_lang, _, normalised) = TranslateTools.Translate(text, normalisation_code)
            translated = func(normalised)
        else: 
            (src_lang, _, translated) = TranslateTools.Translate(text, tgt_lang)
        await message.add_reaction(PartialEmoji)
        await PostMessage(message, member, translated, src_lang, tgt_lang)
Triggers.Get("on_raw_reaction_add").Add(on_raw_reaction_add)

################################################################################

async def cmd_add(ctx, args, trail):
    if len(args) != 2: raise RuntimeError("Incorrect arguments. Expected: <emoji> <language>")
    local_env = Database.GetGuildEnv(ctx.guild.id)
    emoji = args[0]
    lang = args[1]
    if lang not in custom_lang: lang = langcodes.find(lang).language
    reaction_translator = GetReactionTranslator(local_env)
    if emoji in reaction_translator: raise RuntimeError(f"This emoji is already occupied by '{reaction_translator[emoji]}' language")
    reaction_translator[emoji] = lang
    
async def cmd_remove(ctx, args, trail):
    if len(args) != 1: raise RuntimeError("Incorrect arguments. Expected: <emoji>")
    local_env = Database.GetGuildEnv(ctx.guild.id)
    emoji = args[0]
    reaction_translator = GetReactionTranslator(local_env)
    if emoji not in reaction_translator: raise RuntimeError(f"Emoji {emoji} isn't used by translator")
    del reaction_translator[emoji]

async def cmd_list(ctx, args, trail):
    local_env = Database.GetGuildEnv(ctx.guild.id)
    reaction_translator = GetReactionTranslator(local_env)
    output = ["Programmed translations:"]
    for emoji in reaction_translator:
        lang = reaction_translator[emoji]
        if lang not in custom_lang: lang = langcodes.Language.get(lang).display_name()
        output.append(f"{emoji} -> {lang}")
    await Tools.DcReply(ctx.message, "\n".join(output))
    return True

async def cmd_custom(ctx, args, trail):
    output = ["Available custom languages:"]
    for name in custom_lang:
        (normalisation_code, func, help) = custom_lang[name]
        output.append(f"{name}: {help}")
    await Tools.DcReply(ctx.message, "\n".join(output))
    return True

parser = Parser("translate")
parser.Add( Command("add", cmd_add, Help = "Add emoji translation for language.", LongHelp = "Add emoji translation for language.\nSyntax: TRAIL <emoji> <language>\n<language> is name of the language in english") )
parser.Add( Command("remove", cmd_remove, Help = "Remove emoji translation for language.", LongHelp = "Remove emoji translation for language.\nSyntax: TRAIL <emoji>") )
parser.Add( Command("list", cmd_list, Help = "Display list of current emojis used in translations.", LongHelp = "Display list of current emojis used in translations.\nSyntax: TRAIL") )
parser.Add( Command("custom", cmd_custom, Help = "Display list of available custom languages.", LongHelp = "Display list of available custom languages.\nNot real languages obviously.\nSyntax: TRAIL") )
MainParser.Add( Command(parser.Name(), parser, Help = "Setup translation feature", StaticPerms=discord.Permissions.all()) )

################################################################################