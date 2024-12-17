import discord
import random
from discord.ext import commands
import json
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

GAME_DATA_FILE = "game_data.json"

fail_messages = [
    "Intelligence is chasing you, but you are faster.",
    "Wisdom is not a flower that blooms in every garden.",
    "Can you count how many letters are in L-O-S-E-R?",
    "Do you hate me? Why are you doing this to me?",
    "Ah. You must be a business major the way you can't count.",
    "YOU NEED TO LEAVE!",
    "I should ban you for that.",
    "Here you go, it's a dunce cap. 🎩",
    "You nincompoop.",
    "Yeah so I'm going to stop you right there actually.",
    "Pack it up buddy.",
    "First name Stu, last name Pid.",
    "IM GONNA GO INSANE IM GONNA GO INSANE GET THE VOICES OUT OF MY HEAD!!!!",
    "Thanks for bringing down the average IQ. Now I appear smarter.",
    "The lights are on, but nobody's home.",
    "You are proof that evolution can reverse itself.",
    "Truly a scholar in the art of poor judgement.",
    "I trusted you with all my heart, and you broke it.",
    "Well now we know who's NOT smarter than a 5th grader.",
    "I wanted to believe in you... I was naive...",
    "Oh... you're doing great sweetheart...",
    "Can you count how many ways I dislike you right now?",
    "Are you sure you're not competing for 'most confused'?",
    "Well at least you're consistent... consistently wrong.",
    "I can't tell if you're intentionally slow or just naturally gifted at it.",
    "It's not that you're wrong, it's that you're not even close.",
    "It takes REAL talent to be this oblivious.",
    "Ladies and gentlemen, in this exhibit we have an example of a Sapien that didn't develop critical thinking.",
    "I hope you step in a puddle with socks on.",
    "I hope you wash your hands and get your long sleeves wet."
    "I hope you get an itch where you can't reach."
]

config = {"servers":{}}

def get_random_string(string_list):
    return random.choice(string_list)

def load_game_data():
    global config
    if os.path.exists(GAME_DATA_FILE):
        with open(GAME_DATA_FILE, "r") as f:
            config = json.load(f)
    else:
        config = {"servers": {}}

def save_game_data():
    with open(GAME_DATA_FILE, "w") as f:
        json.dump(config, f, indent=4)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    load_game_data()

state_lock = asyncio.Lock()

@bot.listen('on_message')
async def on_message(message):
    if message.author.bot or message.guild is None:
        return

    guild_id = str(message.guild.id)
    guild_config = config["servers"].get(guild_id)

    if not guild_config or message.channel.id != guild_config.get("channel_id"):
        return

    async with state_lock:
        expected_number = guild_config.get("expected_number", 1)
        last_user_name = guild_config.get("last_user_name", None)

        try:
            number = int(message.content)
            if number == expected_number:
                if message.author.name == last_user_name:
                    await message.reply(
                        f"{message.author.mention} {get_random_string(fail_messages)} **You can't count twice in a row. Now you have to restart from 1.**"
                    )
                    await message.add_reaction("❌")
                    config["servers"][guild_id]["expected_number"] = 1
                    config["servers"][guild_id]["last_user_name"] = None
                else:
                    await message.add_reaction("✅")
                    config["servers"][guild_id]["expected_number"] += 1
                    config["servers"][guild_id]["last_user_name"] = message.author.name
            else:
                await message.reply(
                    f"{message.author.mention} {get_random_string(fail_messages)} You ruined it at **{expected_number}**. **Now you have to restart from 1.**"
                )
                await message.add_reaction("❌")
                config["servers"][guild_id]["expected_number"] = 1
                config["servers"][guild_id]["last_user_name"] = None

            save_game_data()

        except ValueError:
            pass

@bot.command(name="set_channel")
async def set_channel(ctx):
    print("hi")
    guild_id = str(ctx.guild.id)

    if "servers" not in config:
        config["servers"] = {}

    config["servers"][guild_id] = {
        "channel_id": ctx.channel.id,
        "expected_number": 1,
        "last_user": None,
    }
    save_game_data()

    await ctx.send(f"Counting game channel has been set to {ctx.channel.mention}.")
    
bot.run(
    "[token redacted]"
)
