
class Emoji:
    def __init__(self):
        self.__emocjis = dict()
    def Add(self, name, emoji):
        if name in self.__emocjis:
            raise RuntimeError(f"Emoji with name {name} already exists")
        self.__emocjis[name] = emoji
    def Get(self, name):
        return self.__emocjis[name]

objectEmoji = Emoji()
objectEmoji.Add("ThumbUp", "👍")
objectEmoji.Add("ThumbDown", "👎")
objectEmoji.Add("Heart", "❤️")
objectEmoji.Add("Skull", "💀")
objectEmoji.Add("Die", "🎲")
objectEmoji.Add("WhiteCheckMark", "✅")
objectEmoji.Add("Question", "❓")
objectEmoji.Add("GreyQuestion", "❔")
objectEmoji.Add("BallotBoxWithCheck", "☑️")
objectEmoji.Add("HeavyCheckMark", "✔️")
objectEmoji.Add("HeavyMultiplication", "✖️")
objectEmoji.Add("X", "❌")
objectEmoji.Add("Exclamation", "❗")